import re, time
from typing import List, Optional, Union, Sequence, Callable, Any, Dict, Tuple

from langchain.agents import Tool, LLMSingleActionAgent, AgentOutputParser, BaseSingleActionAgent, BaseMultiActionAgent
from langchain.agents.agent import ExceptionTool
from langchain.prompts import StringPromptTemplate
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.tools.base import BaseTool
from langchain.agents.tools import InvalidTool

from autoxx.config.config import GlobalConfig
from autoxx.tools.llm.base import llm_uils


# Set up the base template
template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take. Choose the most appropriate action from the following tool name list: [{tool_names}]. Don't take the useless tools.
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin! Give your final answer and follow the above format.

Question: {input}
{agent_scratchpad}"""

# Set up a prompt template
class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]
    
    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\n"
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)


class CustomOutputParser(AgentOutputParser):
    
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action: (.*?)[\n]*Action Input:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL|re.IGNORECASE)
        if not match:
            print(f"Could not parse LLM output: `{llm_output}`")
            return AgentAction(tool=llm_output.strip(" ").strip('"'), tool_input=llm_output.strip(" ").strip('"'), log=llm_output)
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)

    
def setup_planner(tools: List[Tool], model: str = "gpt-3.5-turbo") -> BaseSingleActionAgent:
    tool_names = [tool.name for tool in tools]
    output_parser = CustomOutputParser()
    config = GlobalConfig().get()

    prompt = CustomPromptTemplate(
        template=template,
        tools=tools,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=["input", "intermediate_steps"]
    )

    model_config = config.get_llm_model_config(model)
    llm = ChatOpenAI(temperature=0, model_name=model_config.model, model_kwargs={
        "api_key": model_config.api_key,
        "api_base": model_config.api_base,
        "api_type": model_config.api_type,
        "api_version": model_config.api_version,
        "deployment_id": model_config.api_deployment_id,
    })

    # LLM chain consisting of the LLM and a prompt
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    return LLMSingleActionAgent(
        llm_chain=llm_chain, 
        output_parser=output_parser,
        stop=["\nObservation:"], 
        allowed_tools=tool_names
    )

class AgentExecutor:
    """Consists of an agent using tools."""

    agent: Union[BaseSingleActionAgent, BaseMultiActionAgent]
    tools: Sequence[BaseTool]
    return_intermediate_steps: bool = False
    max_iterations: Optional[int] = 5
    max_execution_time: Optional[float] = None
    early_stopping_method: str = "force"
    handle_parsing_errors: Union[
        bool, str, Callable[[OutputParserException], str]
    ] = False
    name_to_tool_map: dict[str, BaseTool]

    def __init__(self, tools: List[Tool], model: str = "gpt-3.5-turbo"):
        self.tools = tools
        self.agent = setup_planner(tools, model=model)
        self.name_to_tool_map = {tool.name: tool for tool in self.tools}

    def _should_continue(self, iterations: int, time_elapsed: float) -> bool:
        if self.max_iterations is not None and iterations >= self.max_iterations:
            return False
        if (
            self.max_execution_time is not None
            and time_elapsed >= self.max_execution_time
        ):
            return False

        return True

    def _return(
        self,
        output: AgentFinish,
        intermediate_steps: list,
    ) -> Dict[str, Any]:
        final_output = output.return_values
        if self.return_intermediate_steps:
            final_output["intermediate_steps"] = intermediate_steps
        return final_output

    def _decide_next_step(self, inputs: Dict[str, str], intermediate_steps: List[Tuple[AgentAction, str]]) -> Union[List[AgentAction], AgentFinish]:
        try:
            # Call the LLM to see what to do.
            output = self.agent.plan(
                intermediate_steps,
                **inputs,
            )
            return output
        except OutputParserException as e:
            if isinstance(self.handle_parsing_errors, bool):
                raise_error = not self.handle_parsing_errors
            else:
                raise_error = False
            if raise_error:
                raise e
            text = str(e)
            if isinstance(self.handle_parsing_errors, bool):
                observation = "Invalid or incomplete response"
            elif isinstance(self.handle_parsing_errors, str):
                observation = self.handle_parsing_errors
            elif callable(self.handle_parsing_errors):
                observation = self.handle_parsing_errors(e)
            else:
                raise ValueError("Got unexpected type of `handle_parsing_errors`")
            output = AgentAction(ExceptionTool.name, observation, text)
            return [output]

    def _take_next_step(
        self,
        actions: List[AgentAction],
    ) -> List[Tuple[AgentAction, str]]:
        """Take a single step in the thought-action-observation loop.

        Override this to take control of how the agent makes and acts on choices.
        """
        result = []
        for agent_action in actions:
            # Otherwise we lookup the tool
            if agent_action.tool in self.name_to_tool_map:
                tool = self.name_to_tool_map[agent_action.tool]
                # We then call the tool on the tool input to get an observation
                observation = str(tool.run(agent_action.tool_input))
            else:
                observation = InvalidTool().run(agent_action.tool)
            result.append((agent_action, observation))
        return result

    def _return_stopped_response(
        self,
        question: str,
        intermediate_steps: List[Tuple[AgentAction, str]],
    ) -> AgentFinish:
        """Return response when agent has been stopped due to max iterations."""
        # `force` just returns a constant string

        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\n"

        task_prompt = (
            f"Based on these factual information:\n{thoughts}\n"
            f"\nAnswer the question: {question}. Answer="
        )

        response = llm_uils("gpt-4").text_completion(task_prompt)
        return AgentFinish(
            {"output": response}, task_prompt
        )

    def run(
        self,
        input: str,
    ) -> Dict[str, Any]:
        """Run text through and get agent response."""
        inputs = {"input": input}

        intermediate_steps: List[Tuple[AgentAction, str]] = []
        # Let's start tracking the number of iterations and time elapsed
        iterations = 0
        time_elapsed = 0.0
        start_time = time.time()
        # We now enter the agent loop (until it returns something).
        while self._should_continue(iterations, time_elapsed):
            next_step = self._decide_next_step(
                inputs,
                intermediate_steps,
            )
            if isinstance(next_step, AgentFinish):
                return self._return(
                    next_step, intermediate_steps
                )
            elif isinstance(next_step, AgentAction):
                next_step = [next_step]
            
            for step in next_step:
                print(f"\nNext action:\n{step.log}\n")
            
            next_step_output = self._take_next_step(next_step)
            intermediate_steps.extend(next_step_output)
            for output in next_step_output:
                print(f"\nAction: {output[0].tool}({output[0].tool_input})\nOutput:{output[1]}\n")

            iterations += 1
            time_elapsed = time.time() - start_time
        output = self.agent.return_stopped_response(
            self.early_stopping_method, intermediate_steps, **inputs
        )
        return self._return(output, intermediate_steps)

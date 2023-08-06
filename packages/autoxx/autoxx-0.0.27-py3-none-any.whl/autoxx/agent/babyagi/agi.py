import json, time
from typing import Dict, List, Dict, Optional
import logging

from autogpt.llm_utils import create_chat_completion
from autogpt.config import Config

from autoxx.tools.web_search.search import web_search
from autoxx.tools.llm.utils import llm_uils, create_message


class AGIExecutor:
    def __init__(self, objective:str, max_tasks_count: Optional[int] = 5):
        if objective is None or len(objective) <= 1:  
            raise ValueError("Must provide an objective")  

        self.objective = objective
        self.max_tasks_count = max_tasks_count

        self.task_list = self.init_task_list(objective)
        self.status = "initizing"
        self.error_message = None
        self.final_answer = None

    def get_task_by_id(self, task_id: int):
        for task in self.task_list:
            if task["id"] == task_id:
                return task
        return None

    def init_task_list(self, objective: str) -> List[Dict]:
        task_id_counter = 0
        prompt = (
            f"You are a task management AI tasked with creating tasks for the following objective: {objective}.\n"
            f"Create new tasks based on the following plan delimited by triple backtick if necessary for the objective. Limit tasks types to those that can be completed with the available tools listed below. Task description should be detailed. "
            f"Your task: decelop a task list .\n"
            f"The current tool option is [web-search, text-completion] only. What each tool does is as follows:\n"
            f"web-search: It supports searching for information from the Internet. Interaction with web pages is not supported. For tasks using [web-search], provide the search query, and only the search query to use (eg. not 'research waterproof shoes, but 'waterproof shoes').\n"
            f"text-completion: It can be used for text extraction, summarization, copywrite, translation, etc., and it can also be used for LLM-based QA.\n"
            f"Make sure all task IDs are in chronological order.\n"
            f"For efficiency, let's think step by step and create the tasks (up to 5 tasks) that are most critical to objective. "
            f"The last step is always to provide a final formal knowledge base article (at least contains title, summary and solutions) about objective including summary of knowledge acquired.\n"
            f"Do not create any summarizing steps outside of the last step.\n"
            f"The task list output format is as follows: "
            "[{\"id\": 1, \"task\": \"Untapped Capital\", \"tool\": \"web-search\", \"dependent_task_ids\": [], \"status\": \"incomplete\", \"result\": null, \"result_summary\": null}, {\"id\": 2, \"task\": \"Consider additional insights that can be reasoned from the results of...\", \"tool\": \"text-completion\", \"dependent_task_ids\": [1], \"status\": \"incomplete\", \"result\": null, \"result_summary\": null}].\n"
            f"Ensure the output can be parsed by Python json.loads.\n task list="
        )

        messages = create_message(prompt)
        response = create_chat_completion(
            model=Config().smart_llm_model,
            messages=messages,
        )

        new_tasks = json.loads(response)
        task_list = []
        for new_task in new_tasks:
            task_id_counter += 1
            new_task.update({"id": task_id_counter})
            task_list.append(new_task)
        return task_list

    ### Agent functions ##############################
    def execute_task(self, task: Dict) -> Dict:
        # Check if dependent_task_id is completed
        dependent_task_ids = []
        dependent_task_prompt = ""
        if task["dependent_task_ids"]:
            if isinstance(task["dependent_task_ids"], list):
                dependent_task_ids = task["dependent_task_ids"]
            else:
                dependent_task_ids = [task["dependent_task_ids"]]

            for dependent_task_id in dependent_task_ids:
                dependent_task = self.get_task_by_id(dependent_task_id)
                if dependent_task and dependent_task["status"] != "completed":
                    return
                elif dependent_task:
                    dependent_task_prompt += f"\ntask ({dependent_task['id']}. {dependent_task['task']}) result: {dependent_task['result']}"

        # Execute task
        
        task_prompt = (
            f"Complete your assigned task based on the objective: {self.objective}. Your task: {task['task']}. "
            f"Please keep the link reference like newbing in the response.\n"
        )
        if dependent_task_prompt != "":
            task_prompt += f"The previous tasks: {dependent_task_prompt}"

        task_prompt += "\nResponse:"
        if task["tool"] == "text-completion":
            result = llm_uils("gpt-4").text_completion(task_prompt)
            summary_result_prompt = f"Please summarize the following text and and keep the reference links:\n{result}\nSummary:"
            task["result_summary"] = llm_uils().text_completion(summary_result_prompt)
        elif task["tool"] == "web-search":
            result = str(web_search(str(task['task'])))
            summary_result_prompt = f"Please summarize the following text and keep all links:\n{result}\nSummary:"
            task["result_summary"] = llm_uils().text_completion(summary_result_prompt)
        else:
            result = "Unknown tool"
        
        # Update task status and result
        task["status"] = "completed"
        task["result"] = result
        return task
    
    def execute(self):
        self.status = "running"
        # Main loop
        while any(task["status"] == "incomplete" for task in self.task_list):
              # Filter out incomplete tasks
            incomplete_tasks = [task for task in self.task_list if task["status"] == "incomplete"]
            logging.info(f"\033[95m\033[1m INCOMPLETE TASK LIST({self.objective}) \033[0m\033[0m {[str(t['id'])+': '+t['task'] + '[' + t['tool'] + ']' for t in incomplete_tasks]}")
            if incomplete_tasks:
                # Sort tasks by ID
                incomplete_tasks.sort(key=lambda x: x["id"])

                # Pull the first task
                task = incomplete_tasks[0]
                logging.info(f"\033[92m\033[1m NEXT TASK({self.objective}) \033[0m\033[0m {task['id']}:{task['task']}[{task['tool']}], depends on {task['dependent_task_ids']}")

                # Execute task & call task manager from function
                try:
                    completed_task = self.execute_task(task)
                    logging.info(f"\033[93m\033[1m TASK RESULT({self.objective}) \033[0m\033[0m {completed_task['result']}")
                except Exception as e:  
                    logging.error(f"An error occurred while executing the task({self.objective}): {e.with_traceback(None)}")
                    self.status = "error"
                    self.error_message = str(e)  
                    return

            time.sleep(1)  # Sleep before checking the task list again
        self.status = "completed"

    def stat(self) -> Dict:
        return {"task_list": self.task_list, "status": self.status, "error_message": self.error_message}
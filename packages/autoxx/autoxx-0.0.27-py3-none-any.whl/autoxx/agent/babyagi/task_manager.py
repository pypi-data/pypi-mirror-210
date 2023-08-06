import logging, time, threading
from typing import Dict, Optional
from autoxx.agent.babyagi.agi import AGIExecutor
  
class TaskManager:  
    def __init__(self):  
        self.tasks = {}  
  
    def create_task(self, objective: str, max_tasks_count: Optional[int] = 3):  
        if objective in self.tasks:
            if self.tasks[objective].status == "error":
                task = self.tasks[objective]
                task_thread = threading.Thread(target=task.execute)  
                task_thread.start()
                return
            else:
                raise ValueError(f"Task found with objective: {objective}")
        
        task = AGIExecutor(objective, max_tasks_count) 
        self.tasks[objective] = task  
  
        # Start task execution in a separate thread  
        task_thread = threading.Thread(target=task.execute)  
        task_thread.start()
  
    def get_task_stat(self, objective: str) -> Dict:  
        if objective not in self.tasks:  
            raise ValueError(f"No task found with objective: {objective}")  
  
        return self.tasks[objective].stat()
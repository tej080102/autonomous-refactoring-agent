"""
Sample 8: Task/todo manager with deeply nested logic.
Issues: deep nesting, duplicated priority logic, no type hints,
        manual date handling, long methods.
"""


import time


class TaskManager:
    def __init__(self):
        self.tasks = []
        self.next_id = 1

    def add_task(self, title, priority, due_date=None):
        task = {
            "id": self.next_id,
            "title": title,
            "priority": priority,
            "due_date": due_date,
            "completed": False,
            "created_at": time.time(),
        }
        self.next_id = self.next_id + 1
        self.tasks.append(task)
        return task["id"]

    def complete_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                return True
        return False

    def get_pending(self):
        result = []
        for task in self.tasks:
            if task["completed"] == False:
                result.append(task)
        return result

    def get_completed(self):
        result = []
        for task in self.tasks:
            if task["completed"] == True:
                result.append(task)
        return result

    def get_by_priority(self, priority):
        result = []
        for task in self.tasks:
            if task["priority"] == priority:
                result.append(task)
        return result

    def get_high_priority_pending(self):
        result = []
        for task in self.tasks:
            if task["completed"] == False:
                if task["priority"] == "high" or task["priority"] == "critical":
                    result.append(task)
        return result

    def get_stats(self):
        total = len(self.tasks)
        completed = 0
        pending = 0
        high = 0
        medium = 0
        low = 0

        for task in self.tasks:
            if task["completed"] == True:
                completed = completed + 1
            else:
                pending = pending + 1

            if task["priority"] == "high" or task["priority"] == "critical":
                high = high + 1
            elif task["priority"] == "medium":
                medium = medium + 1
            elif task["priority"] == "low":
                low = low + 1

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "high_priority": high,
            "medium_priority": medium,
            "low_priority": low,
            "completion_rate": completed / total if total > 0 else 0,
        }

    def delete_task(self, task_id):
        new_tasks = []
        found = False
        for task in self.tasks:
            if task["id"] == task_id:
                found = True
            else:
                new_tasks.append(task)
        self.tasks = new_tasks
        return found

    def search(self, keyword):
        result = []
        for task in self.tasks:
            if keyword.lower() in task["title"].lower():
                result.append(task)
        return result

import ast
import json


class TodoManager:
    def __init__(self):
        self.item: list[dict] = []

    def update(self,todos: list | str) -> str:
        if isinstance(todos, str):
            try:
                todos = json.loads(todos)
            except json.JSONDecodeError:
                try:
                    todos = ast.literal_eval(todos)
                except (SyntaxError, ValueError) as error:
                    raise ValueError("todos must be a list or JSON array string") from error
        if not isinstance(todos, list):
            raise ValueError("todos must be a list")
        if len(todos) > 20:
            raise ValueError("Max 20 todos allowed")


        validated = []
        in_progress_count = 0
        for index, todo in enumerate(todos):
            if not isinstance(todo, dict):
                raise ValueError(f"todos[{index}] must be an object")
            content = str(todo.get("content", "")).strip()
            status = str(todo.get("status", "pending")).lower()

            if not content:
                raise ValueError(f"todos[{index}] requires content")
            if status not in ("pending", "in_progress", "completed"):
                raise ValueError(f"todos[{index}] has invalid status '{status}'")
            if status == "in_progress":
                in_progress_count += 1
            validated.append({"content": content, "status": status})

        if in_progress_count > 1:
            raise ValueError("Only one todo can be in_progress at a time")

        self.items = validated
        return self.render()



    def render(self) -> str:
        if not self.item:
            return "No todos"
        lines = []
        markers = {"pending": "[ ]", "in_progress": "[>]", "completed": "[x]"}
        for todo in self.items:
            lines.append(f"{markers[todo['status']]} {todo['content']}")
        done = sum(todo["status"] == "completed" for todo in self.items)
        lines.append(f"\n({done}/{len(self.items)} completed)")
        return "\n".join(lines)
    

TODO = TodoManager()









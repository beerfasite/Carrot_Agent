

from .. import todo


DEFINITION = {
    "name": "todo_write",
    "description": "Create and manage a task list for your current coding session.",
    "input_schema": {
        "type": "object",
        "properties": {"todos": {
            "type": "array", "maxItems": 20,
            "items": {"type": "object",
                      "properties": {"content": {"type": "string", "minLength": 1},
                                     "status": {"type": "string",
                                                "enum": ["pending", "in_progress", "completed"]}},
                      "required": ["content", "status"]},
        }},
        "required": ["todos"],
    },
}




def run_todo_write(todos) -> str:
    try:
        output = todo.TODO.update(todos)
    except ValueError as error:
        return f"Error: {error}"
    print(f"\n\033[33m## Current Tasks\033[0m\n{output}")
    return output


def register(registry) -> None:
    registry.register(DEFINITION, run_todo_write)



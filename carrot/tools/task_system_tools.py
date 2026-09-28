
import json
from dataclasses import asdict

from .. import task_store


def run_create_task(subject: str, description: str = "") -> str:
    task = task_store.TASKS.create(subject, description)
    print(f"  [create] {task.subject}")
    return f"Created {task.id}: {task.subject}"


def run_update_task(task_id: str, addBlockedBy: list[str]) -> str:
    task = task_store.TASKS.update_dependencies(task_id, addBlockedBy)
    dependencies = ", ".join(task.blockedBy) or "(none)"
    print(f"  [update] {task.subject} blockedBy: {dependencies}")
    return f"Updated {task.id} blockedBy: {dependencies}"


def run_list_tasks() -> str:
    tasks = task_store.TASKS.list()
    if not tasks:
        return "No tasks. Use create_task to add some."
    markers = {"pending": "[ ]", "in_progress": "[>]", "completed": "[x]"}
    lines = []
    for task in tasks:
        marker = markers.get(task.status, "[?]")
        dependencies = f" (blockedBy: {', '.join(task.blockedBy)})" if task.blockedBy else ""
        owner = f" [{task.owner}]" if task.owner else ""
        lines.append(f"{marker} {task.id}: {task.subject} [{task.status}]{owner}{dependencies}")
    return "\n".join(lines)


def run_get_task(task_id: str) -> str:
    return json.dumps(asdict(task_store.TASKS.load(task_id)), indent=2)


def run_claim_task(task_id: str) -> str:
    return task_store.claim_task(task_id, owner="agent")


def run_complete_task(task_id: str) -> str:
    return task_store.complete_task(task_id, owner="agent")


DEFINITIONS = [
    {"name": "create_task", "description": "Create a task and return its runtime-generated ID.",
     "input_schema": {"type": "object",
                      "properties": {"subject": {"type": "string"}, "description": {"type": "string"}},
                      "required": ["subject"], "additionalProperties": False}},
    {"name": "update_task", "description": "Add dependencies using IDs returned by create_task.",
     "input_schema": {"type": "object",
                      "properties": {"task_id": {"type": "string", "pattern": "^task_[0-9a-f]{8}$"},
                                     "addBlockedBy": {"type": "array",
                                                      "items": {"type": "string", "pattern": "^task_[0-9a-f]{8}$"},
                                                      "minItems": 1}},
                      "required": ["task_id", "addBlockedBy"], "additionalProperties": False}},
    {"name": "list_tasks", "description": "List tasks with status, owner, and dependencies.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_task", "description": "Get a task by ID.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "string"}}, "required": ["task_id"]}},
    {"name": "claim_task", "description": "Claim a pending task whose dependencies are complete.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "string"}}, "required": ["task_id"]}},
    {"name": "complete_task", "description": "Complete the task claimed by this agent.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "string"}}, "required": ["task_id"]}},
]

HANDLERS = {
    "create_task": run_create_task,
    "update_task": run_update_task,
    "list_tasks": run_list_tasks,
    "get_task": run_get_task,
    "claim_task": run_claim_task,
    "complete_task": run_complete_task,
}


def register(registry) -> None:
    for definition in DEFINITIONS:
        registry.register(definition, HANDLERS[definition["name"]])

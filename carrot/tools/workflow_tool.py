
from ..workflow import runtime

DEFINITION = {
    "name": "Workflow",
    "description": "Run a saved workflow by name. Pass input in args.",


    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},

            "args": {"type": "object"},

            "resume_from_run_id": {"type": "string"},
        },
        "required": ["name"],
        "additionalProperties": False,
    },
}


def run_workflow_tool(name: str, args: dict | None = None, resume_from_run_id: str | None = None) -> str:

    return runtime.run_workflow_json(name, args, resume_from_run_id)


def register(registry) -> None:
    registry.register(DEFINITION, run_workflow_tool)

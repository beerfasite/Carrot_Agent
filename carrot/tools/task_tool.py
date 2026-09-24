"""task 工具（课程 s06：跑一个子代理，只回最终文本）。"""

from .. import subagent

DEFINITION = {
    "name": "task",
    "description": "Run a subagent with fresh conversation context and return its final text.",
    "input_schema": {
        "type": "object",
        "properties": {"prompt": {"type": "string", "minLength": 1}},
        "required": ["prompt"],
    },
}


def register(registry) -> None:
    registry.register(DEFINITION, subagent.run_subagent)

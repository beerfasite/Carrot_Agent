"""load_skill 工具（课程 s07：按名加载完整 SKILL.md）。"""

from .. import skills

DEFINITION = {
    "name": "load_skill",
    "description": "Load the full SKILL.md content by skill name.",
    "input_schema": {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    },
}


def register(registry) -> None:
    registry.register(DEFINITION, skills.SKILL_LOADER.load)

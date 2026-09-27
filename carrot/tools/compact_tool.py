"""compact 工具（课程 s08：请求压缩，实际压缩在 agent loop 里特殊处理）。"""

DEFINITION = {
    "name": "compact",
    "description": "Summarize earlier conversation to free context space.",
    "input_schema": {"type": "object", "properties": {}},
}


def run_compact() -> str:
    return "Compaction requested after this tool batch."


def register(registry) -> None:
    registry.register(DEFINITION, run_compact)

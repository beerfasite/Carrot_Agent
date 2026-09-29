"""workflow 运行时（s16 精髓：一次工具调用跑完一整套固定编排 + 断点续跑）。

断点续跑用 LangGraph 的 InMemorySaver + thread_id（笔记 03）：run_id 即 thread_id，
同 thread_id 续跑从上次 checkpoint 继续，已完成的节点不重跑。
"""

import json
import secrets

from langgraph.checkpoint.memory import InMemorySaver

from . import WORKFLOWS

# 进程内共享的 checkpointer（笔记强调：InMemorySaver 实例重建会清空 checkpoint，
# 所以必须保持单例，否则 resume 会丢失历史状态）
CHECKPOINTER = InMemorySaver()


def create_run_id(name: str) -> str:
    return f"wf_{name}_{secrets.token_hex(8)}"


def run_workflow(name: str, args: dict | None = None, resume_from_run_id: str | None = None) -> dict:
    if name not in WORKFLOWS:
        raise ValueError(f"unknown workflow '{name}'")

    meta, build_graph = WORKFLOWS[name]
    args = {**meta.get("default_args", {}), **(args or {})}

    graph = build_graph(CHECKPOINTER)
    run_id = resume_from_run_id or create_run_id(name)
    result = graph.invoke(args, config={"configurable": {"thread_id": run_id}})

    confirmed = sorted(
        result.get("confirmed", []),
        key=lambda f: {"high": 0, "medium": 1, "low": 2}.get(f.get("severity"), 3),
    )
    return {"run_id": run_id, "workflow": name, "confirmed": confirmed}


def run_workflow_json(name: str, args: dict | None = None, resume_from_run_id: str | None = None) -> str:
    try:
        return json.dumps(run_workflow(name, args, resume_from_run_id), ensure_ascii=False, default=str)
    except Exception as error:
        return f"Error: {error}"

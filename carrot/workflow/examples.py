"""示例 workflow：review-changes（s16 精髓，用笔记的 Send + MapReduce 表达）。

固定流程：对每个维度并行「审计」→ 汇聚 → 对每条发现并行「对抗验证」→ 只保留确认项。
计划写在图（代码）里，不是靠聊天一轮轮凑。
"""

from operator import add
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from .models import Findings, Verdict
from .nodes import structured_llm

DIMENSIONS = ["correctness", "security", "performance", "style"]

META = {
    "name": "review-changes",
    "description": "Review changed files across dimensions, verify each finding",
    "phases": ["Review", "Verify"],
    "default_args": {"dimensions": DIMENSIONS},
}

AUDIT_LLM = structured_llm(Findings)
VERIFY_LLM = structured_llm(Verdict)


class ReviewState(TypedDict):
    changes: str
    dimensions: list[str]
    audits: Annotated[list, add]
    confirmed: Annotated[list, add]


def audit_node(state) -> dict:
    dimension = state["dimension"]
    changes = state["changes"]
    result = AUDIT_LLM.invoke(
        f"Review this change context for {dimension} issues. "
        "Report only issues supported by the supplied text.\n\n"
        f"{changes}"
    )
    return {
        "audits": [
            {"dimension": dimension, **finding.model_dump()}
            for finding in result.findings
        ]
    }


def collect_node(state) -> dict:
    # 汇聚点：所有 audit 实例完成后执行一次，为 verify 层提供完整 findings
    return {}


def verify_node(state) -> dict:
    finding = state["finding"]
    changes = state["changes"]
    verdict = VERIFY_LLM.invoke(
        "Adversarially verify this finding against the supplied change context.\n\n"
        f"Change context:\n{changes}\n\n"
        f"Finding:\n{finding}"
    )
    if verdict.isReal:
        return {"confirmed": [{**finding, "reason": verdict.reason}]}
    return {}


def audit_router(state) -> list[Send]:
    return [
        Send("audit", {"dimension": dimension, "changes": state["changes"]})
        for dimension in state["dimensions"]
    ]


def verify_router(state) -> list[Send]:
    return [
        Send("verify", {"finding": finding, "changes": state["changes"]})
        for finding in state["audits"]
    ]


def build_review_changes_graph(checkpointer=None):
    builder = StateGraph(ReviewState)
    builder.add_node("audit", audit_node)
    builder.add_node("collect", collect_node)
    builder.add_node("verify", verify_node)
    builder.add_conditional_edges(START, audit_router, path_map=["audit"])
    builder.add_edge("audit", "collect")
    builder.add_conditional_edges("collect", verify_router, path_map=["verify"])
    builder.add_edge("verify", END)
    return builder.compile(checkpointer=checkpointer)

"""workflow 子代理输出的 Pydantic 模型（s16 结构化输出精髓，对应笔记 with_structured_output）。"""

from typing import Literal

from pydantic import BaseModel, Field


class Finding(BaseModel):
    title: str = Field(description="问题的简短标题")
    severity: Literal["high", "medium", "low"] = Field(description="严重程度")


class Findings(BaseModel):
    findings: list[Finding] = Field(description="审查发现的问题列表")


class Verdict(BaseModel):
    isReal: bool = Field(description="该问题是否真实存在")
    reason: str = Field(description="判断依据")

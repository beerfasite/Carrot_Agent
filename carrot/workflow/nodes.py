"""workflow 节点（s16 精髓 + 笔记 ChatOpenAI + with_structured_output）。

主循环模型用 openai SDK 直连厂商，workflow 节点模型用 langchain 的 ChatOpenAI
（base_url 指向同一厂商），两者共用 config.MODEL / OPENAI_API_KEY / OPENAI_BASE_URL。
"""

import os

from langchain_openai import ChatOpenAI

from .. import config


def structured_llm(output_model):
    """返回绑定结构化输出能力的 ChatOpenAI。

    笔记 with_structured_output 精髓：模型直接返回 Pydantic 对象，字段由
    Literal/Field 约束，不用再从自然语言里抠 JSON。
    """
    llm = ChatOpenAI(
        model=config.MODEL,
        api_key=os.environ.get("OPENAI_API_KEY") or "MISSING_API_KEY",
        base_url=os.environ.get("OPENAI_BASE_URL") or None,
    )
    return llm.with_structured_output(output_model)

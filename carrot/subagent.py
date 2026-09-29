
import json

from . import config, hooks
from .tools import ToolCall, build_base_registry, execute_tool

SUB_SYSTEM = (
    f"You are a coding agent at {config.WORKDIR}. "
    "Complete the given task, then return a concise final answer."
)


MAX_SUBAGENT_TURNS = 30




def run_subagent(prompt: str) -> str:
    print("\n\033[35m[Subagent started]\033[0m")

    messages = [
        {"role": "system", "content": SUB_SYSTEM},
        {"role": "user", "content": prompt},
    ]

    registry = build_base_registry()

    for _ in range(MAX_SUBAGENT_TURNS):
        response = config.client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=registry.openai_tools(),
            max_tokens=config.MAX_TOKENS,
        )
        message = response.choices[0].message

        if not message.tool_calls:
            #可能可以退出当前循环，对话结束
            messages.append({"role": "assistant", "content": message.content})
            force = hooks.trigger_hooks("Stop", messages)
            if force:
                messages.append({"role": "user", "content": force})
                continue
            print("\033[35m[Subagent done]\033[0m")
            return message.content or "(no summary)"

        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [tc.model_dump() for tc in message.tool_calls],
        })

        for tc in message.tool_calls:
            # 为什么要靠 tool_call_id 配对，而不是靠顺序：
            #   情况二（最致命）：工具完成顺序是不确定的。
            #     模型若按「第 1 条结果 = 第 1 个请求」来理解就会张冠李戴——
            #     比如最先回来的其实是第 2 个请求的结果。
            #   情况三：历史会被压缩 / 裁剪（compactor 的 snip_compact 会归档中间段）。
            #     靠「位置」配对，中间一旦被切掉，后面的位置全错位；靠 ID 则不受影响。

            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            output = execute_tool(ToolCall(name, args), registry.handlers)
            print(f"  \033[90m[sub] {name}: {output[:100]}\033[0m")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": output})

    print("\033[35m[Subagent stopped]\033[0m")
    return "Subagent stopped after 30 turns without a final answer."









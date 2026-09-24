from turtledemo.clock import hand
from typing import Callable

from .. import hooks


class ToolCall:
    """
    这个是模型返回后的toolcall，需要转换成统一格式
    一次工具调用的统一表示（name + args dict）。
    OpenAI 的 tool_call 结构是 id + function.name + function.arguments(JSON 字符串)，
    Anthropic 是 name + input。这里统一成 name + input(dict)，让 hook 和 handler
    都基于这个结构，屏蔽两种 SDK 的差异。
    """
    def __init__(self, name: str,input: dict):
        self.name = name
        self.input = input or {}


class ToolRegistry:
    """
    这个是发送给模型看的，需要统一成openai格式
    """
    def __init__(self):
        self.definitions : list[dict] = []          #定义
        self.handlers : dict[str , Callable] = {}   #工具名+工具的回调函数

    def register(self, definition: dict, handler: Callable) -> None:
        self.definitions.append(definition)
        self.handlers[definition["name"]] = handler

    def openai_tools(self):
        return [to_openai_tool(d) for d in self.definitions]


def to_openai_tool(definition: dict) -> dict:
    """Anthropic 的 {name, description, input_schema} → OpenAI function 格式。"""
    return {
        "type": "function",
        "function": {
            "name": definition["name"],
            "description": definition.get("description", ""),
            "parameters": definition.get("input_schema", {"type": "object", "properties": {}}),
        },
    }


def execute_tool(tool_call: ToolCall, handlers: dict) -> str:
    blocked = hooks.trigger_hooks("PreToolUse",tool_call)
    if blocked:
        return str(blocked)
    handler = handlers.get(tool_call.name) #handler是一个工具的回调函数
    try:
        output = handler(**tool_call.input) if handler else f"Unknown: {tool_call.name}"
    except Exception as error:
        output = f"Error: {error}"
    hooks.trigger_hooks("PostToolUse", tool_call,output)
    return str(output)


def build_registry() -> ToolRegistry:
    pass



def build_base_regitry() -> ToolRegistry:
    from . import files, shell

    registry = ToolRegistry()
    shell.register(registry)
    files.register(registry)
    return registry








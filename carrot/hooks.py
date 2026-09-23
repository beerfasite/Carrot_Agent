"""
Hook 系统
四个固定事件点，挂在 agent loop 之外：UserPromptSubmit / PreToolUse /
PostToolUse / Stop。trigger_hooks 返回第一个非 None 的结果，非 None 即表示
阻断（比如 PreToolUse 返回拒绝原因、Stop 返回强制续跑的追加消息）。
"""


#四个可能发生的地方
HOOK_EVENTS = ("UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop")

#hooks的注册表
HOOKS: dict[str, list] = {event: [] for event in HOOK_EVENTS}


#注册hooks注册表
def register_hook(event:str,callback) -> None:
    """event就是HOOK_EVENTS之中"""
    if event not in HOOKS:
        raise ValueError(f"Unknown hook event : {event}")
    HOOKS[event].append(callback)


#调用hooks位置的回调函数
def trigger_hooks(event : str, *args):
    for callback in HOOKS:
        result = callback(*args)
    if result is not None:
        return result
    return None












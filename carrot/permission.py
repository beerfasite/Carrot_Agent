"""
三闸门权限（课程 s03 精髓，s04 起包装成 PreToolUse hook）。
Gate 1 硬拒名单 → Gate 2 规则匹配（破坏性命令/越界路径）→ Gate 3 用户确认。
拒绝时返回原因字符串（hook 机制据此追加 "Permission denied" 的 tool_result，
而不是跳过，保证消息配对完整）。
"""

import re

from . import config, hooks

DENY_LIST = ["rm -rf /", "sudo", "shutdown", "reboot", "mkfs", "dd if="]
DESTRUCTIVE_COMMAND_WORD = re.compile(
    r"(?i)(?:^|[;&|()\n])\s*(?:rm|del)(?=\s|$|[;&|()])"
)
DESTRUCTIVE = ["rm ", "> /etc/", "chmod 777"]


def contains_destructive_command(command: str) -> bool:
    return bool(DESTRUCTIVE_COMMAND_WORD.search(command))


def permission_hook(block) -> str | None:
    if block.name == "bash":
        command = block.input.get("command", "")
        for pattern in DENY_LIST:
            if pattern in command:
                print(f"\n\033[31m[blocked] '{pattern}'\033[0m")
                return "Permission denied by deny list"
        if contains_destructive_command(command) or any(kw in command for kw in DESTRUCTIVE):
            print("\n\033[33m[permission] Potentially destructive command\033[0m")
            print(f"   Tool: {block.name}({block.input})")
            if input("   Allow? [y/N] ").strip().lower() not in ("y", "yes"):
                return "Permission denied by user"

    if block.name in ("read_file", "write_file", "edit_file"):
        path = block.input.get("path", "")
        if not (config.WORKDIR / path).resolve().is_relative_to(config.WORKDIR.resolve()):
            print("\n\033[33m[permission] Access outside workspace\033[0m")
            print(f"   Tool: {block.name}({block.input})")
            if input("   Allow? [y/N] ").strip().lower() not in ("y", "yes"):
                return "Permission denied by user"
    return None


def log_hook(block) -> None:
    preview = str(list(block.input.values())[:2])[:60]
    print(f"\033[90m[HOOK] {block.name}({preview})\033[0m")
    return None


def large_output_hook(block, output) -> None:
    if len(str(output)) > 100000:
        print(f"\033[33m[HOOK] Large output from {block.name}: {len(str(output))} chars\033[0m")
    return None


def context_hook(query: str) -> None:
    print(f"\033[90m[HOOK] UserPromptSubmit: working in {config.WORKDIR}\033[0m")
    return None


def summary_hook(messages: list) -> None:
    tool_count = sum(1 for message in messages if message.get("role") == "tool")
    print(f"\033[90m[HOOK] Stop: session used {tool_count} tool calls\033[0m")
    return None


def register_hooks() -> None:
    hooks.register_hook("UserPromptSubmit", context_hook)
    hooks.register_hook("PreToolUse", permission_hook)
    hooks.register_hook("PreToolUse", log_hook)
    hooks.register_hook("PostToolUse", large_output_hook)
    hooks.register_hook("Stop", summary_hook)

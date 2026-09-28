
import json

from . import config, hooks, memory, prompt
from .compactor import COMPACTOR
from .session import Session
from .tools import ToolCall, build_registry, execute_tool

MAX_REACTIVE_RETRIES = 1
TODO_REMINDER_ROUNDS = 3


class Agent:
    def __init__(self):
        self.registry = build_registry()
        self.compactor = COMPACTOR
        self.session = Session()

    def run(self, query: str) -> str:
        hooks.trigger_hooks("UserPromptSubmit", query)
        self.session.active_request = query
        self.session.messages.append({"role": "user", "content": query})

        relevant = memory.load_memories(self.session.messages)
        system = prompt.build_system(relevant)
        self._loop(system)

        for message in reversed(self.session.messages):
            if message.get("role") == "assistant" and message.get("content"):
                return message["content"]
        return ""

    def _loop(self, system: str) -> None:
        rounds_since_todo = 0
        reactive_retries = 0

        while True:
            self.session.messages = self.compactor.prepare(
                self.session.messages, self.session.active_request
            )
            full_messages = [{"role": "system", "content": system}] + self.session.messages
            try:
                response = config.client.chat.completions.create(
                    model=config.MODEL,
                    messages=full_messages,
                    tools=self.registry.openai_tools(),
                    max_tokens=config.MAX_TOKENS,
                )
                reactive_retries = 0
            except Exception as error:
                too_long = any(
                    text in str(error).lower()
                    for text in ("context length", "maximum context", "too many tokens")
                )
                if too_long and reactive_retries < MAX_REACTIVE_RETRIES:
                    print("[reactive compact]")
                    self.session.messages = self.compactor.reactive_compact(
                        self.session.messages, self.session.active_request
                    )
                    reactive_retries += 1
                    continue
                raise

            message = response.choices[0].message

            if not message.tool_calls:
                self.session.messages.append({"role": "assistant", "content": message.content})
                force = hooks.trigger_hooks("Stop", self.session.messages)
                if force:
                    self.session.messages.append({"role": "user", "content": force})
                    continue
                if memory.extract_memories(self.session.messages):
                    memory.consolidate_memories()
                return

            self.session.messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [tc.model_dump() for tc in message.tool_calls],
            })

            used_todo = False
            compact_requested = False
            for tc in message.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments or "{}")
                print(f"\033[36m> {name}\033[0m")
                if name == "compact":
                    output = "Compaction requested after this tool batch."
                    compact_requested = True
                else:
                    output = execute_tool(ToolCall(name, args), self.registry.handlers)
                    print(output[:200])
                if name == "todo_write":
                    used_todo = True
                self.session.messages.append({
                    "role": "tool", "tool_call_id": tc.id, "content": output,
                })

            rounds_since_todo = 0 if used_todo else rounds_since_todo + 1
            if rounds_since_todo >= TODO_REMINDER_ROUNDS:
                self.session.messages.append({
                    "role": "user", "content": "<reminder>Update your todos.</reminder>",
                })
                rounds_since_todo = 0

            if compact_requested:
                self.session.messages = self.compactor.compact_history(
                    self.session.messages, self.session.active_request
                )

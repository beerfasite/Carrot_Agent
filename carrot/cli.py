
import argparse
import os
import sys

try:
    import readline  # noqa: F401  # Windows 上通常不可用，降级为普通 input
except ImportError:
    pass

from . import config, permission
from .agent import Agent

# 像素萝卜：绿色叶子 + 橙色主体
GREEN = "\033[32m"
ORANGE = "\033[38;5;214m"
RESET = "\033[0m"

BANNER = (
    f"    {GREEN}██   ██   ██{RESET}\n"
    f"   {GREEN}████ ████ ████{RESET}\n"
    f"   {GREEN}██████████████{RESET}\n"
    f"  {ORANGE}████████████████{RESET}\n"
    f"  {ORANGE}████████████████{RESET}\n"
    f"  {ORANGE}████████████████{RESET}\n"
    f"   {ORANGE}██████████████{RESET}\n"
    f"    {ORANGE}████████████{RESET}\n"
    f"     {ORANGE}██████████{RESET}\n"
    f"      {ORANGE}████████{RESET}\n"
    f"       {ORANGE}██████{RESET}\n"
    f"        {ORANGE}████{RESET}\n"
    f"         {ORANGE}██{RESET}"
)


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Carrot — a coding agent learned from learn-claude-code")
    parser.add_argument("-d", "--dir", help="working directory (default: current directory)")
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("未检测到 OPENAI_API_KEY。请复制 .env.example 为 .env，填入厂商密钥和端点后重试。")
        return

    if args.dir:
        config.configure_workdir(args.dir)

    print(BANNER)
    print("Carrot: coding agent (loop + tools + permission + hooks + subagent + "
          "skill + memory + compact + task + workflow)")
    print("Enter a question, press Enter to send. Type q to quit.\n")

    permission.register_hooks()
    agent = Agent()

    while True:
        try:
            query = input("carrot >> ")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        result = agent.run(query)
        print(result)
        print()


if __name__ == "__main__":
    main()

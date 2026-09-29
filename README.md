# Carrot_Agent

一个**通用编程助手**：在终端里和它对话，它能执行 shell 命令、读写文件、规划任务、派子代理，以及运行提前写好的固定流程（workflow）。

本项目是**借鉴 [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) 的精髓思想二次开发**的成果——不是照抄，而是把课程 17 章里讲的核心机制提取出来，重构成一个结构清晰、能真正跑起来的 Python 工程。

一句话概括它的内核，就是课程开篇那句：

> `while True: LLM → tool → tool_result`，直到模型决定停止。

其余一切——权限、hook、计划、子代理、记忆、压缩、任务、workflow——都只是挂在这个循环周围的扩展点。

---

## 目录

- [核心特性](#核心特性)
- [机制对照（课程 → 本工程）](#机制对照课程--本工程)
- [安装](#安装)
- [配置](#配置)
- [运行](#运行)
- [工具列表](#工具列表)
- [项目结构](#项目结构)
- [Workflow 运行时](#workflow-运行时)
- [如何扩展](#如何扩展)
- [已知限制](#已知限制)

---

## 核心特性

| 特性 | 说明 |
|---|---|
| **多厂商可切换** | 走 OpenAI 兼容接口，改 `.env` 即可在 DeepSeek / Kimi / 通义千问 / 硅基流动之间切换 |
| **工具调用** | 16 个内置工具，新增工具无需改动主循环 |
| **三闸门权限** | 危险命令硬拒 + 规则匹配 + 用户确认，且**子代理也绕不过** |
| **可扩展点（hooks）** | 4 个固定时机，挂回调即可扩展，不侵入循环 |
| **子代理** | 独立上下文，只回最终文本，不能递归委派 |
| **技能加载** | 启动时只注入技能目录，用到时才展开全文 |
| **上下文压缩** | 五级递进，从"落盘可恢复"逐步到"有损摘要" |
| **长期记忆** | 跨会话持久化，按相关性召回 |
| **任务系统** | 磁盘持久化的任务依赖图，支持 claim / complete 解锁 |
| **Workflow** | 用 LangGraph 把固定流程写成图，支持**批量并行**与**断点续跑** |

---

## 机制对照（课程 → 本工程）

| 课程章节 | 精髓思想 | 本工程模块 |
|---|---|---|
| s01 Agent Loop | `while True`：模型 → 工具 → 结果 | `carrot/agent.py` |
| s02 Tool Use | 工具定义 + 分发，循环不动 | `carrot/tools/` |
| s03 Permission | 三闸门：硬拒 → 规则 → 确认 | `carrot/permission.py` |
| s04 Hooks | 扩展点挂循环外 | `carrot/hooks.py` |
| s05 TodoWrite | 先列计划再动手 + 忘就提醒 | `carrot/todo.py` |
| s06 Subagent | 独立 messages，只回最终文本 | `carrot/subagent.py` |
| s07 Skill Loading | 先扫目录，用到再展开 | `carrot/skills.py` |
| s08 Context Compact | 预算 → 裁剪 → 微压缩 → 摘要 | `carrot/compactor.py` |
| s09 Memory | 筛选 / 召回 / 抽取 / 合并 | `carrot/memory.py` |
| s10 Task System | 依赖图 + claim/complete 解锁 | `carrot/task_store.py` |
| s16 Workflow Runtime | 固定流程写进代码 + 批量并行 + 断点续跑 | `carrot/workflow/` |

> 未纳入：s11 后台任务、s12 cron、s13 agent 团队、s14 MCP、s17 目标闭环。

---

## 安装

需要 **Python 3.10+**（用到了 `glob.glob(root_dir=...)` 与 `Path.is_relative_to`）。

```bash
pip install -r requirements.txt
```

依赖仅 5 个：`openai`、`python-dotenv`、`pyyaml`、`langgraph`、`langchain-openai`。

---

## 配置

在项目根目录建一个 `.env`（已被 `.gitignore` 忽略，不会进版本库）：

```ini
# 厂商密钥
OPENAI_API_KEY=你的key

# 厂商的 OpenAI 兼容端点 + 模型名
OPENAI_BASE_URL=https://api.deepseek.com/v1
MODEL_ID=deepseek-chat
```

常用厂商配置：

| 厂商 | `OPENAI_BASE_URL` | `MODEL_ID` 示例 |
|---|---|---|
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| Kimi | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |
| 通义千问（百炼） | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| 硅基流动 | `https://api.siliconflow.cn/v1` | `deepseek-ai/DeepSeek-V3` |

**换厂商只改这三行，代码不用动。**

---

## 运行

```bash
python -m carrot                    # 在当前目录启动
python -m carrot -d /path/to/dir    # 指定工作目录
```

> 注意必须用 `python -m carrot`，不能直接跑 `python carrot/cli.py`——因为项目内部用了相对导入，只有以"包"的方式启动才有效。

终端出现像素萝卜后即可对话，输入 `q` 退出。

运行时产生的数据（记忆、任务、压缩产物）落在**工作目录**的 `.carrot/` 下。

---

## 工具列表

共 16 个：

| 类别 | 工具 |
|---|---|
| 命令 | `bash` |
| 文件 | `read_file`、`write_file`、`edit_file`、`glob` |
| 计划 | `todo_write` |
| 子代理 | `task` |
| 技能 | `load_skill` |
| 压缩 | `compact` |
| 任务系统 | `create_task`、`update_task`、`list_tasks`、`get_task`、`claim_task`、`complete_task` |
| 编排 | `Workflow` |

工具定义内部用 `{name, description, input_schema}` 保存，发送前由 `to_openai_tool()` 转成 OpenAI 的 `function` 格式——这是能对接各家厂商的关键一层。

---

## 项目结构

```
carrot/
├── config.py          # 环境变量、OpenAI 兼容 client、目录常量
├── cli.py             # REPL 入口（含启动横幅）
├── agent.py           # ★ 主循环（骨架）
├── session.py         # 会话状态：messages + 当前请求
├── prompt.py          # system prompt 组装
├── hooks.py           # hook 机制（4 个事件 + 注册/触发）
├── permission.py      # 三闸门权限（注册为 PreToolUse hook）
├── subagent.py        # 子代理（独立循环）
├── skills.py          # 技能加载
├── compactor.py       # 上下文压缩（五级递进）
├── memory.py          # 长期记忆
├── todo.py            # 计划清单
├── task_store.py      # 任务依赖图
├── tools/             # 全部工具（每个模块自己注册）
│   ├── __init__.py    #   ToolRegistry + execute_tool
│   ├── shell.py       #   bash
│   ├── files.py       #   文件四件套 + safe_path
│   ├── todo_tool.py   #   todo_write
│   ├── task_tool.py   #   task（→ subagent）
│   ├── skill_tool.py  #   load_skill
│   ├── compact_tool.py#   compact
│   ├── task_system_tools.py  # 任务系统 6 个
│   └── workflow_tool.py      # Workflow
└── workflow/          # Workflow 运行时（LangGraph）
    ├── __init__.py    #   registry 白名单
    ├── models.py      #   结构化输出声明（Pydantic）
    ├── nodes.py       #   「会按结构返回」的模型工厂
    ├── runtime.py     #   建图 / 跑 / 续跑
    └── examples.py    #   ★ 示例图 review-changes
skills/                # 技能目录（每个子目录一个 SKILL.md）
```

**数据流**：

```
用户输入
  → 召回记忆 + 组装 system prompt
  → 循环：压缩检查 → 请求模型
       有 tool_calls → 权限检查 → 执行工具 → 回填结果 → 继续循环
       无 tool_calls → 抽取记忆 → 返回最终答复
```

---

## Workflow 运行时

对**固定流程**，不需要让模型逐轮决定下一步，而是把编排写进图（代码）里，一次 `Workflow` 工具调用跑完整套。

### 三个保证

| 保证 | 靠什么实现 | 单靠 agent loop 能做到吗 |
|---|---|---|
| **顺序** | 边（`add_edge`） | ❌ 靠模型自觉，可能漏 |
| **批量并行** | `Send`（router 返回 N 个） | ❌ 一圈只能走一步 |
| **断点续跑** | checkpointer + `thread_id` | ❌ 没有 |

### 内置示例：`review-changes`

固定流程：**多维度并行审计 → 汇聚 → 逐条对抗验证 → 只留确认项**。

```
        START
          │  Send × 4（并行）
    ┌─────┼─────┬─────┐
    ▼     ▼     ▼     ▼
  audit audit audit audit      ← 4 个维度同时审
    └─────┼─────┴─────┘
          ▼  等齐
      collect
          │  Send × N
    ┌─────┼─────┐
    ▼     ▼     ▼
 verify verify verify           ← 每条发现各派一个验证
    └─────┼─────┘
          ▼  等齐
         END
```

> 注意：LangGraph 导出的**静态图看起来只是一条直线**（三个节点首尾相连）。因为"派几份"是运行时由 router 算出来的，静态图看不出来——真正的并行结构在运行时才展开。

### 触发方式

在 REPL 里说：

```
运行 review-changes workflow，审查这段代码：<把代码贴进来>
```

### 五个文件的职责

| 文件 | 职责 |
|---|---|
| `models.py` | 声明子代理必须按什么格式回话 |
| `nodes.py` | 造"会按结构返回"的模型（`with_structured_output`） |
| `examples.py` | 用节点拼出具体的图 |
| `__init__.py` | 登记白名单（哪些图可用） |
| `runtime.py` | 取图 → 编译 → 跑 → 管续跑 |

**加新 workflow 只需动两个文件**：`examples.py`（定义图）+ `__init__.py`（登记）。

---

## 如何扩展

### 加一个工具

在 `carrot/tools/` 下新建 `mytool.py`：

```python
DEFINITION = {
    "name": "my_tool",
    "description": "这个工具做什么（模型靠它判断何时使用）",
    "input_schema": {
        "type": "object",
        "properties": {"x": {"type": "string"}},
        "required": ["x"],
    },
}

def run_my_tool(x: str) -> str:
    return f"got {x}"

def register(registry) -> None:
    registry.register(DEFINITION, run_my_tool)
```

然后在 `carrot/tools/__init__.py` 的 `build_registry()` 里 import 并注册。**主循环零改动。**

### 加一个技能

在 `skills/` 下建目录 + `SKILL.md`（frontmatter 写 `name` 和 `description`，正文写指令）。启动时会自动进目录，模型用到时再 `load_skill` 展开全文。

### 加一个 workflow

1. 在 `carrot/workflow/examples.py` 里写一个建图函数（参考 `build_review_changes_graph`）
2. 在 `carrot/workflow/__init__.py` 的 `WORKFLOWS` 里加一行 `名字: (meta, build_graph)`

`runtime.py` 不用改——它不认识任何具体的图。

---

## 已知限制

诚实记录当前版本的边界：

| 限制 | 说明 |
|---|---|
| **模型不知道有哪些 workflow** | `prompt.py` 没有注入 workflow 目录，只有用户在对话里点名才能用起来。`Workflow` 工具的 description 也没列出有哪些流程 |
| **没有并发/限流控制** | 批量跑会一次性派 N 个任务，可能撞厂商 RPM 限制。课程 s16 里有个并发信号量，这里没移植 |
| **断点续跑是进程内的** | 用 `InMemorySaver`，进程退出后存档就没了。要跨进程需换 `PostgresSaver` |
| **`META` 里两个字段未使用** | `description` 和 `phases` 是预留字段，目前没有任何地方读它们 |
| **缺参数时报错不友好** | 调用 workflow 漏传必填参数时，错误会以 `Error: 'changes'` 这种形式返回 |
| **`subagent.py` 有一段字符串语句** | 不是注释而是表达式语句，功能无害但属于冗余代码 |
| **权限提示对文件工具无效** | 文件越界时权限层会问用户，但 `safe_path` 是无条件硬拒的，所以点了"允许"也过不去 |
| **未纳入的章节** | s11 后台任务、s12 cron、s13 agent 团队、s14 MCP、s17 目标闭环 |

---

## 说明

- 主循环模型调用用 `openai` SDK；workflow 节点用 langchain 的 `ChatOpenAI`（为了 `with_structured_output`）。两者都走 OpenAI 兼容协议，共用同一套密钥与端点配置。
- workflow 用到的 LangGraph API 限定在 `langgraph==1.1.2` 的范围内：`StateGraph` / `add_node` / `add_edge` / `add_conditional_edges` / `Send` / `InMemorySaver` / `with_structured_output`。

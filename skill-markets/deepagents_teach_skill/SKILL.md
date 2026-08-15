---
name: deepagents_teach_skill
version: 1.0.0
version: 1.0.0
description: "Teaches how to use the DeepAgents framework for building single or multi-agent systems with context management, file system tools, subagent delegation, skills, and MCP integration. This skill should be used when the user needs to create DeepAgents-based AI agents, implement subagent architectures, configure filesystem backends, set up permission controls, or understand DeepAgents API patterns. Triggers on: DeepAgents, create_deep_agent, SubAgent, deep agent, agent with tools, multi-agent delegation, filesystem agent, agent with memory."
intent: Teaches how to use the DeepAgents framework for building ...
category: orchestration
audience: [agent, designer]
---
# DeepAgents Teach Skill

## What is DeepAgents

DeepAgents is a production-grade AI agent framework in the LangChain ecosystem. It provides SubAgent delegation, built-in filesystem tools, multi-backend persistence, path-level permission control, Skills-based progressive context loading, and human-in-the-loop approval workflows — all through a single `create_deep_agent()` factory function.

## When to Use DeepAgents

Use DeepAgents when the project requires any of the following:

- **Multi-agent collaboration** — orchestrate specialized sub-agents (researcher -> coder -> reviewer pipelines)
- **Filesystem access** — agents that read/write/edit files on a local or virtual filesystem
- **Path-based permissions** — fine-grained allow/deny/interrupt rules on file operations
- **Progressive context management via Skills** — load domain knowledge on demand, not all at startup
- **Human-in-the-loop approval** — pause agent execution for human review before critical operations
- **Persistent memory across sessions** — checkpointing with SqliteSaver or PostgresSaver
- **Streaming output** — real-time agent responses for chat UIs via `astream()`

## Installation and Setup

```bash
pip install deepagents
# or from source:
# pip install git+https://github.com/langchain-ai/deepagents.git
```

```python
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

model = init_chat_model("claude-sonnet-4-20250514")
```

## Minimum Viable Agent

Three lines of code produce a fully functional agent with 9 built-in tools:

```python
from deepagents import create_deep_agent

agent = create_deep_agent(model=model, system_prompt="You are a helpful assistant.")
result = agent.invoke({"messages": [{"role": "user", "content": "Hello!"}]})
```

## Core Configuration Catalog

Listed in order of importance. All parameters are passed to `create_deep_agent()`:

| Parameter | Type | Purpose |
|-----------|------|---------|
| `model` | `BaseChatModel` | **Required.** The LLM backing the agent. |
| `system_prompt` | `str` | **Required.** The agent's role and behavior instructions. |
| `tools` | `list[BaseTool]` | Custom tools injected alongside built-in tools. |
| `subagents` | `list[SubAgent]` | Specialized sub-agents for task delegation via the `task` tool. |
| `middleware` | `list[AgentMiddleware]` | Custom middleware hooks (logging, retry, rate-limiting). |
| `backend` | `BackendProtocol` | Filesystem backend: `StateBackend`, `FilesystemBackend`, `StoreBackend`, `CompositeBackend`. |
| `permissions` | `list[FilesystemPermission]` | Path-level access control rules (allow/deny/interrupt). |
| `checkpointer` | `BaseCheckpointSaver` | Persistence engine: `MemorySaver`, `SqliteSaver`, `PostgresSaver`. |
| `skills` | `list[str]` | Paths to skill directories for progressive knowledge loading. |
| `interrupt_on` | `dict[str, bool]` | Human-in-the-loop: pause before specified tool calls. |
| `memory` | `list[str]` | File paths loaded into context at startup (e.g., `["AGENTS.md"]`). |
| `store` | `BaseStore` | Long-term cross-session memory via LangGraph Store. |

For complete API signatures, see `references/api-reference.md`.

## SubAgent Architecture

Sub-agents are the core delegation pattern. Each sub-agent has an isolated context — its intermediate reasoning does not pollute the main agent's message history.

```python
from deepagents import create_deep_agent, SubAgent

research_sub = SubAgent(
    name="researcher",
    description="Search and analyze technical information. Use for research tasks.",
    system_prompt="You are a technical researcher. Search, analyze, and produce structured reports.",
    tools=[web_search],
)

reviewer_sub = SubAgent(
    name="code-reviewer",
    description="Review code quality and suggest improvements.",
    system_prompt="You are a code review expert. Evaluate correctness, security, and maintainability.",
    tools=[code_analyzer],
)

agent = create_deep_agent(
    model=model,
    subagents=[research_sub, reviewer_sub],
    system_prompt="You are an orchestrator. Delegate tasks to specialized sub-agents via the task tool.",
)
```

**When to create a sub-agent:**
- The task requires a specialized persona or workflow
- The intermediate reasoning of the sub-task should not clutter the main context
- The sub-task needs its own set of tools distinct from the main agent
- The sub-task benefits from independent permission boundaries

**Context isolation principle:** Each sub-agent receives only its own `system_prompt` plus the delegated task description. It does not inherit the main agent's `system_prompt`, nor does the main agent see the sub-agent's internal tool calls. Only the final response is returned to the orchestrator.

For full `SubAgent` TypedDict fields, see `references/api-reference.md`.

## Built-in Tools (No Declaration Needed)

These 9 tools are automatically available to every DeepAgent. No manual tool declaration is required:

| Tool | Category | Purpose |
|------|----------|---------|
| `write_todos` | Planning | Task decomposition with status tracking (pending -> in_progress -> completed) |
| `task` | Delegation | Invoke a named sub-agent for specialized work |
| `ls` | Filesystem | List directory contents |
| `read_file` | Filesystem | Read file contents |
| `write_file` | Filesystem | Create or overwrite a file |
| `edit_file` | Filesystem | Perform exact string replacements in a file |
| `glob` | Filesystem | Find files by wildcard pattern |
| `grep` | Filesystem | Search file contents with regex |
| `execute` | Shell | Run shell commands (controlled by permissions/interrupt_on) |

## Skills: Progressive Knowledge Loading

Skills follow a three-level progressive disclosure model, minimizing context window consumption:

```
skills/
  code-review/
    SKILL.md          # L1+L2: name + description loaded at startup; full body on activation
    references/       # L3: loaded only when specific steps require it
    scripts/          # L3: executable helpers
    assets/           # L3: templates, images, etc.
```

**Loading levels:**
- **L1 (startup):** Only the YAML frontmatter (`name` + `description`) is injected into the system prompt. Agent knows what skills exist but not their content.
- **L2 (activation):** When the agent decides a skill is relevant, the full `SKILL.md` body is loaded into context.
- **L3 (execution):** Reference files, scripts, and assets are loaded on demand during execution.

```python
agent = create_deep_agent(
    model=model,
    skills=["./skills/"],
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    system_prompt="You have access to skills. Activate them when relevant tasks arise.",
)
```

**Skills vs Memory:**
- Skills = procedural knowledge (how to do something), loaded on demand
- Memory (via `memory=`) = declarative knowledge (what to know), loaded at startup

## Crucial Caveats and Traps

1. **Context isolation does not equal memory release** — Sub-agents still consume main process context. Each delegated task adds the sub-agent's final response to the orchestrator's message history.

2. **Limit sub-agents to 3-5** — Performance degrades sharply beyond 5 sub-agents. The model must evaluate all sub-agent descriptions for every delegation decision.

3. **Production must use SqliteSaver or PostgresSaver** — `MemorySaver` loses all state on process restart. For any deployment that matters, use a persistent checkpointer.

4. **FilesystemBackend requires `virtual_mode=True`** — Without it, the agent operates directly on the real filesystem, which is dangerous. Always sandbox.

5. **`mode="interrupt"` on permissions requires a checkpointer** — The interrupt mechanism needs a checkpointer to save state while waiting for human approval. Without one, interrupts will fail.

6. **Never create an agent without `system_prompt`** — The agent has no behavioral guidance without it. At minimum, provide a role description.

7. **Permission rules are order-dependent** — The first matching rule wins. Place specific rules (e.g., `/workspace/**`) before generic rules (e.g., `/**`).

8. **Sub-agents inherit parent permissions by default** — Unless explicitly overridden in the `SubAgent` definition, sub-agents use the parent agent's permission rules.

9. **Custom tools and MCP tools are NOT covered by FilesystemPermission** — Permission rules only apply to the built-in filesystem tools (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`). Custom tools need their own authorization logic.

10. **`astream()` requires an async runtime** — Use `asyncio.run()` or an async framework (FastAPI). Calling `astream()` in a sync context will fail.

## Quick Reference: When to Use Which Feature

```
Need task decomposition?          -> write_todos (built-in, no config)
Need specialized execution?       -> SubAgent (subagents= parameter)
Need file read/write?             -> FilesystemMiddleware (built-in, no config)
Need persistent memory?           -> StoreBackend or store= parameter
Need session continuity?          -> checkpointer=SqliteSaver()
Need approval workflow?           -> interrupt_on= or permissions mode="interrupt"
Need domain knowledge on demand?  -> skills= parameter
Need custom behavior injection?   -> middleware= parameter
Need path-based access control?   -> permissions= parameter
Need real-time output?            -> agent.astream(stream_mode="messages")
Need cost/performance monitoring? -> config={"callbacks": [observer]}
Need environment-based config?    -> YAML + component registry pattern
```

## Design Patterns

For production-proven architecture patterns, see `references/patterns.md`:
- Three-agent research-code-review pipeline
- Tiered permission model (read-only / write / approval zones)
- Long-term memory separation with CompositeBackend
- Progressive skill loading for large knowledge bases
- HITL approval flow with checkpoint recovery
- Streaming output with interrupt-resume

## API Reference

For complete parameter signatures, TypedDict definitions, backend constructors, and middleware hooks, see `references/api-reference.md`.

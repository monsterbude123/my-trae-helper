# DeepAgents API Reference

## `create_deep_agent()`

The single factory function for creating DeepAgent instances.

### Signature

```python
def create_deep_agent(
    model: str | BaseChatModel,
    system_prompt: str,
    *,
    tools: list[BaseTool] = [],
    subagents: list[SubAgent] = [],
    middleware: list[AgentMiddleware] = [],
    backend: BackendProtocol | None = None,
    permissions: list[FilesystemPermission] = [],
    checkpointer: BaseCheckpointSaver | None = None,
    skills: list[str] = [],
    interrupt_on: dict[str, bool] = {},
    memory: list[str] = [],
    store: BaseStore | None = None,
    model_config: dict[str, Any] | None = None,
    debug: bool = False,
    name: str = "DeepAgent",
) -> Runnable
```

### Parameters in Detail

#### `model` (required)
- **Type:** `str | BaseChatModel`
- The LLM model. Accepts a LangChain chat model instance or a model identifier string (e.g., `"openai:gpt-4o"`, `"claude-sonnet-4-20250514"`).
- Use `init_chat_model()` from `langchain.chat_models` for string identifiers.

#### `system_prompt` (required)
- **Type:** `str`
- **Default:** none (must be provided)
- The agent's behavioral instructions. Assembled as: USER (this parameter) -> BASE (SDK-injected tool/sub-agent docs) -> SUFFIX (from HarnessProfile).
- Always appears first in the final system prompt. Cannot be overridden by profiles.

#### `tools`
- **Type:** `list[BaseTool]`
- **Default:** `[]`
- Custom tools injected alongside the 9 built-in tools. Use `@tool` decorator or LangChain `StructuredTool`.
- Built-in tools (`write_todos`, `task`, `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `execute`) are always available regardless of this parameter.

#### `subagents`
- **Type:** `list[SubAgent]`
- **Default:** `[]`
- Specialized sub-agents for the `task` tool to delegate to.
- See SubAgent TypedDict below for full field definitions.

#### `middleware`
- **Type:** `list[AgentMiddleware]`
- **Default:** `[]`
- Custom middleware instances. Executed after built-in middleware (FilesystemMiddleware, SubAgentMiddleware, TodoListMiddleware, etc.).
- Execution order: built-in middleware -> custom middleware (in list order).
- See AgentMiddleware hooks below.

#### `backend`
- **Type:** `BackendProtocol | None`
- **Default:** `None` (defaults to `StateBackend()`)
- The filesystem backend implementation. Controls where file operations (ls/read/write/edit) actually store data.
- Available backends: `StateBackend`, `FilesystemBackend`, `StoreBackend`, `CompositeBackend`.

#### `permissions`
- **Type:** `list[FilesystemPermission]`
- **Default:** `[]`
- Path-level access control rules. Applied to built-in filesystem tools only.
- Rules are evaluated in order; the first match wins.
- See FilesystemPermission TypedDict below.

#### `checkpointer`
- **Type:** `BaseCheckpointSaver | None`
- **Default:** `None`
- Persistence engine for conversation state. Required for `interrupt_on` and multi-turn conversation memory.
- Available: `MemorySaver`, `SqliteSaver`, `PostgresSaver`.
- Thread isolation via `config={"configurable": {"thread_id": "..."}}`.

#### `skills`
- **Type:** `list[str]`
- **Default:** `[]`
- Paths to skill directories. Each directory must contain a `SKILL.md` with YAML frontmatter (name + description).
- Enables progressive disclosure: only name + description loaded at startup; full body loaded on activation.

#### `interrupt_on`
- **Type:** `dict[str, bool]`
- **Default:** `{}`
- Tool-name-based human-in-the-loop configuration. Pauses execution before the specified tool is called.
- Example: `{"write_file": True, "execute": True}`.
- Requires a `checkpointer` to function.

#### `memory`
- **Type:** `list[str]`
- **Default:** `[]`
- File paths loaded into the agent's context at startup via `MemoryMiddleware`.
- Common usage: `memory=["AGENTS.md"]` to inject project-level knowledge.

#### `store`
- **Type:** `BaseStore | None`
- **Default:** `None`
- Long-term cross-session memory via LangGraph's `BaseStore` interface.
- Supports `store.put()`, `store.get()`, `store.search()` for persistent key-value storage.
- Implementations: `InMemoryStore`, or any LangGraph-compatible store backend.

---

## SubAgent TypedDict

```python
from typing import TypedDict, NotRequired

class SubAgent(TypedDict):
    name: str                          # Unique identifier, displayed to the orchestrator
    description: str                   # When to use this sub-agent (used for matching)
    system_prompt: str                 # Sub-agent's behavioral instructions (ISOLATED from parent)
    tools: NotRequired[list[BaseTool]] # Tools available to this sub-agent
    permissions: NotRequired[list[FilesystemPermission]]  # Independent permission rules
    model: NotRequired[BaseChatModel]  # Optional: different model for this sub-agent
```

### Field Details

- **`name`** (required): Display name used by the orchestrator to reference this sub-agent. Must be unique within the subagents list.
- **`description`** (required): Natural language description of when this sub-agent should be delegated to. The orchestrator's LLM uses this to decide which sub-agent to invoke. Write this as "Use when..." or "Responsible for...".
- **`system_prompt`** (required): The sub-agent's own system prompt. Completely isolated from the parent agent's `system_prompt`. The sub-agent sees only this prompt plus the delegated task.
- **`tools`** (optional): List of tools for this sub-agent. If omitted, the sub-agent has access to built-in tools only.
- **`permissions`** (optional): FilesystemPermission rules specific to this sub-agent. If omitted, inherits the parent agent's permissions.
- **`model`** (optional): A different model for this sub-agent. Useful for cost optimization (e.g., use a cheaper model for simple tasks).

---

## FilesystemPermission TypedDict

```python
class FilesystemPermission(TypedDict):
    operations: list[str]   # ["read"] | ["write"] | ["read", "write"]
    paths: list[str]        # Glob patterns: "/workspace/**", "*.py", "/secrets/**"
    mode: str               # "allow" | "deny" | "interrupt"
```

### Field Details

- **`operations`**: Which file operations this rule applies to. Valid values: `"read"`, `"write"`. Can combine both.
- **`paths`**: Glob patterns for path matching. Supports `**` (recursive), `*` (single level), `{a,b}` (alternation). Examples: `"/**"`, `"/workspace/**"`, `"*.{py,js}"`.
- **`mode`**: Action to take when the rule matches:
  - `"allow"`: Permit the operation
  - `"deny"`: Block the operation (agent receives an error message)
  - `"interrupt"`: Pause execution for human approval (requires checkpointer)

### Rule Evaluation

Rules are evaluated in declaration order. The **first matching rule wins**. If no rule matches, the default is `allow`.

```python
# Example: workspace-only access
permissions=[
    FilesystemPermission(operations=["read", "write"], paths=["/workspace/**"], mode="allow"),
    FilesystemPermission(operations=["read", "write"], paths=["/**"], mode="deny"),
]
```

---

## Backend Types

### Import Paths

```python
from deepagents.backends import (
    StateBackend,
    FilesystemBackend,
    StoreBackend,
    CompositeBackend,
)
from deepagents.backends.utils import create_file_data
```

### StateBackend

In-memory, thread-local storage. The default backend.

```python
StateBackend()
```
- **Persistence:** Thread-local only. Lost on process restart unless paired with a checkpointer.
- **Use case:** Temporary work areas, prototyping, testing.
- **No constructor arguments.**

### FilesystemBackend

Real disk-backed storage.

```python
FilesystemBackend(
    root_dir: str,           # Root directory for file operations
    virtual_mode: bool = True,  # CRITICAL: always set True for sandbox isolation
)
```
- **`root_dir`**: Base directory on disk. All agent file paths are relative to this.
- **`virtual_mode`**: When `True`, agent sees a virtual filesystem rooted at `root_dir`. When `False`, agent has direct disk access (dangerous).
- **Use case:** Local development with real project files.

### StoreBackend

LangGraph Store-backed persistence. Cross-thread, cross-session.

```python
StoreBackend(
    namespace: Callable[[RunnableConfig], tuple[str, ...]],
)
```
- **`namespace`**: A function that takes runtime config and returns a namespace tuple. Used to isolate storage per user/session.
- **Use case:** Long-term memory, multi-tenant deployments.
- Example: `StoreBackend(namespace=lambda rt: ("memories",))`

### CompositeBackend

Route different path prefixes to different backends.

```python
CompositeBackend(
    default: BackendProtocol,                   # Fallback for unmatched paths
    routes: dict[str, BackendProtocol],         # Path prefix -> Backend mapping
)
```
- **`default`**: Backend used when no route matches. Typically `StateBackend()`.
- **`routes`**: Dict mapping path prefixes to backends. Prefixes should end with `/`.
- **Routing rule:** Longest prefix match. If path starts with `/memories/project/`, the `/memories/` route matches.

```python
backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/memories/": StoreBackend(namespace=lambda rt: ("agent",)),
        "/workspace/": FilesystemBackend(root_dir="./workspace", virtual_mode=True),
    },
)
```

---

## Checkpointer Types

### Import Paths

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.postgres import PostgresSaver
```

### MemorySaver

In-memory, process-local. **For prototyping only.**

```python
MemorySaver()
```
- Lost on process restart.
- No constructor arguments.

### SqliteSaver

SQLite file-backed persistence. **For single-machine deployments.**

```python
SqliteSaver.from_conn_string("checkpoints.db")
```
- Persistent across process restarts.
- Not suitable for concurrent access from multiple processes.

### PostgresSaver

PostgreSQL-backed persistence. **For production deployments.**

```python
DB_URI = "postgresql://user:pass@host:5432/deepagents"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()  # Creates tables on first run
    agent = create_deep_agent(model=model, checkpointer=checkpointer, ...)
```
- Concurrent-safe, supports HA, backups.
- Requires `checkpointer.setup()` on first run to create schema.
- Thread isolation via `config={"configurable": {"thread_id": "..."}}`.

### Usage Pattern

```python
config = {"configurable": {"thread_id": "user-123-session-abc"}}

# Multi-turn conversation: same thread_id accumulates context
agent.invoke({"messages": [HumanMessage(content="My name is Alice")]}, config=config)
agent.invoke({"messages": [HumanMessage(content="What's my name?")]}, config=config)
# Agent remembers "Alice"

# View history
for state in agent.get_state_history(config):
    print(state)
```

---

## AgentMiddleware Hooks

```python
from langchain.agents.middleware import AgentMiddleware

class AgentMiddleware:
    """Base class for custom middleware. Override hooks as needed."""

    def before_model(self, state: AgentState, runtime: Runtime) -> dict | None:
        """Called before each LLM invocation. Return a dict to merge into state."""
        pass

    def after_model(self, state: AgentState, runtime: Runtime) -> dict | None:
        """Called after each LLM response. Inspect/modify state before next step."""
        pass

    def before_agent(self, state: AgentState, runtime: Runtime) -> dict | None:
        """Called once before the agent loop starts."""
        pass

    def after_agent(self, state: AgentState, runtime: Runtime) -> dict | None:
        """Called once after the agent loop ends."""
        pass

    def on_tool_start(self, tool_name: str, tool_input: dict, runtime: Runtime) -> None:
        """Called before each tool invocation."""
        pass

    def on_tool_end(self, tool_name: str, tool_output: Any, runtime: Runtime) -> None:
        """Called after each tool invocation."""
        pass

    def on_error(self, error: Exception, runtime: Runtime) -> bool:
        """Called on LLM error. Return True to retry, False to propagate."""
        return False
```

### Hook Execution Order (Onion Model)

```
before_agent()
  -> before_model()
     -> LLM call
  -> after_model()
     -> before_model()
        -> LLM call (if tool calls made)
     -> after_model()
     -> ... (agent loop repeats)
  -> after_agent()
```

---

## HarnessProfile

```python
from deepagents import HarnessProfile, register_harness_profile, GeneralPurposeSubagentProfile

register_harness_profile(
    "openai:gpt-4o",  # "provider:model" or just "provider"
    HarnessProfile(
        base_system_prompt: str | None = None,         # Replace SDK default BASE prompt
        system_prompt_suffix: str | None = None,       # Append to end of system prompt
        tool_description_overrides: dict | None = None, # Override tool descriptions
        excluded_tools: set[str] = set(),               # Exclude specific tools
        excluded_middleware: set[str] = set(),           # Exclude specific middleware
        extra_middleware: list = [],                     # Additional middleware
        general_purpose_subagent: GeneralPurposeSubagentProfile | None = None,
    ),
)
```

---

## Store Interface

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Write
store.put(("memories",), "key_name", {"value": "data"})

# Read
item = store.get(("memories",), "key_name")

# Search
results = store.search(("memories",), query="search term")
```

---

## Streaming

```python
# Blocking
result = agent.invoke({"messages": [...]})

# Async streaming (requires async runtime)
async for msg, metadata in agent.astream(
    {"messages": [...]},
    config=config,
    stream_mode="messages",  # "messages" | "values" | "updates" | "debug"
):
    # msg is a LangChain message object
    content = getattr(msg, "content", "")
    tool_calls = getattr(msg, "tool_calls", None)
```

**Stream modes:**
- `"messages"`: Emit only new messages (recommended for chat UIs)
- `"values"`: Emit full state after each step (debugging)
- `"updates"`: Emit incremental state changes
- `"debug"`: Emit node name + timing (performance analysis)

Modes can be combined: `stream_mode=["messages", "values"]`.

---

## HITL: Human-in-the-Loop

### Configuration

```python
agent = create_deep_agent(
    model=model,
    checkpointer=MemorySaver(),  # REQUIRED for interrupt
    interrupt_on={
        "write_file": True,   # Pause before any file write
        "edit_file": True,    # Pause before any file edit
        "execute": True,      # Pause before shell commands
    },
    permissions=[
        FilesystemPermission(
            operations=["write"],
            paths=["/secrets/**"],
            mode="interrupt",  # Pause before writing to secrets
        ),
    ],
)
```

### Resume After Interrupt

```python
from langgraph.types import Command

# Approve
agent.invoke(Command(resume={"decision": "approve"}), config=config)

# Approve with modifications
agent.invoke(
    Command(resume={"decision": "approve", "modified": {"content": "corrected content"}}),
    config=config,
)

# Reject
agent.invoke(
    Command(resume={"decision": "reject", "reason": "Security policy violation"}),
    config=config,
)
```

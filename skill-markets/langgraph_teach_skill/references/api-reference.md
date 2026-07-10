# LangGraph API Reference

Complete API reference for LangGraph core classes and functions. All signatures follow LangGraph 0.2+.

---

## StateGraph

The primary graph builder. Constructs a stateful execution graph from nodes and edges.

### Constructor

```python
StateGraph(state_schema: Type[Any] | dict, config_schema: Type[Any] | None = None)
```

| Parameter | Description |
|-----------|-------------|
| `state_schema` | TypedDict or dict defining the shared state shape |
| `config_schema` | Optional TypedDict for runtime configuration (e.g., `thread_id`) |

### Methods

#### `add_node(name: str, action: Runnable | Callable) -> StateGraph`

Register a node function. The node receives the current state dict and returns a dict of state updates.

```python
builder.add_node("my_node", my_function)
builder.add_node("subgraph", compiled_subgraph)  # Subgraph as node
```

Returns `self` for chaining.

#### `add_edge(start: str, end: str) -> StateGraph`

Add a fixed edge from one node to another. Use `START` and `END` sentinels for graph boundaries.

```python
builder.add_edge(START, "first_node")
builder.add_edge("last_node", END)
```

Returns `self` for chaining.

#### `add_conditional_edges(source: str, path: Callable | Runnable, path_map: dict | list) -> StateGraph`

Add a conditional branch from `source`. The `path` function receives the current state and returns a key that matches one of the `path_map` entries.

```python
def route(state: State) -> str:
    if state["score"] > 0.8:
        return "approve"
    return "review"

builder.add_conditional_edges("classifier", route, {
    "approve": "approval_node",
    "review": "review_node",
    END: END,  # END can also be a target
})
```

| Parameter | Description |
|-----------|-------------|
| `source` | Name of the source node |
| `path` | Callable `(state) -> str` returning a route key |
| `path_map` | Dict mapping route keys to target node names (or `END`) |

**Critical**: The string returned by `path` must exactly match a key in `path_map`. Mismatches cause silent routing failure.

**Send API variant**: Return a list of `Send` objects for dynamic parallel fan-out:

```python
from langgraph.constants import Send

def route(state):
    return [Send("worker", {"task": t}) for t in state["tasks"]]

builder.add_conditional_edges("dispatcher", route, ["worker"])
```

When using `Send`, `path_map` is a list of allowed target node names (not a dict).

#### `compile(checkpointer=None, interrupt_before=None, interrupt_after=None) -> CompiledStateGraph`

Compile the graph into an executable `CompiledStateGraph`.

```python
from langgraph.checkpoint.memory import MemorySaver

graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["human_review"],
    interrupt_after=["tools"],
)
```

| Parameter | Description |
|-----------|-------------|
| `checkpointer` | Optional `BaseCheckpointSaver` instance for state persistence |
| `interrupt_before` | List of node names to pause execution before entering |
| `interrupt_after` | List of node names to pause execution after completing |

---

## CompiledStateGraph

The runnable graph produced by `StateGraph.compile()`.

### `invoke(input: dict, config: dict | None = None) -> dict`

Synchronous execution. Returns the final state dict after all nodes complete.

```python
result = graph.invoke(
    {"messages": [HumanMessage("Hello")]},
    config={"configurable": {"thread_id": "user-123"}},
)
```

### `ainvoke(input: dict, config: dict | None = None) -> dict`

Async version of `invoke`.

```python
result = await graph.ainvoke(input, config)
```

### `stream(input: dict, config: dict | None = None, stream_mode="values") -> Iterator`

Synchronous streaming. `stream_mode` controls what each chunk contains:

| Mode | Emits |
|------|-------|
| `"values"` | Full state after each super-step |
| `"updates"` | State delta after each node (default for some versions) |
| `"messages"` | Token-level LLM output chunks (requires `messages` key in state) |
| `"custom"` | Data emitted via `StreamWriter` from within nodes |
| `"debug"` | Detailed trace: node name, input, output, timing |

```python
for chunk in graph.stream(input, stream_mode="updates"):
    print(chunk)  # {"node_name": {"field": "update"}}
```

Multiple modes can be combined as a list: `stream_mode=["updates", "messages"]`.

### `astream(input: dict, config: dict | None = None, stream_mode="values") -> AsyncIterator`

Async version of `stream`.

```python
async for chunk in graph.astream(input, stream_mode="messages"):
    print(chunk)
```

### `aget_state(config: dict) -> StateSnapshot`

Retrieve the current state for a given thread, including pending interrupts.

```python
snapshot = await graph.aget_state({"configurable": {"thread_id": "user-123"}})
print(snapshot.values)       # Current state dict
print(snapshot.next)         # Tuple of next node names to execute
print(snapshot.interrupts)   # List of pending Interrupt objects
```

---

## Checkpointers

### MemorySaver

In-memory checkpoint storage. **Not for production**—data is lost on process restart.

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

### SqliteSaver

SQLite-backed persistent checkpoints. Suitable for single-server production.

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
graph = builder.compile(checkpointer=checkpointer)
```

### PostgresSaver

PostgreSQL-backed persistent checkpoints. Suitable for multi-server, high-availability deployments.

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@host:5432/db"
)
await checkpointer.setup()  # Create tables on first use
graph = builder.compile(checkpointer=checkpointer)
```

---

## Human-in-the-Loop: `interrupt()` and `Command`

### `interrupt(value: Any) -> Any`

Pause graph execution at the current node. The graph saves a checkpoint and waits for external input. When resumed, `interrupt()` returns the value passed via `Command(resume=...)`.

```python
def approval_node(state: State) -> dict:
    # Pause and show what needs approval
    decision = interrupt({"action": state["pending_action"], "reason": "Needs human review"})
    # decision will be the value from Command(resume=...)
    return {"approved": decision}
```

**Requirement**: The graph must be compiled with a checkpointer, or `interrupt()` raises a runtime error.

### `Command(resume: Any = None, update: dict | None = None) -> Command`

Used to resume a paused graph. Pass to `graph.invoke(Command(...), config)`.

```python
from langgraph.types import Command

# Resume with approval
await graph.ainvoke(
    Command(resume={"approved": True, "comment": "Looks good"}),
    config={"configurable": {"thread_id": "user-123"}},
)
```

| Field | Description |
|-------|-------------|
| `resume` | Value returned by the pending `interrupt()` call |
| `update` | Optional state update to apply before resuming |

---

## Send API

Dynamic parallel fan-out. Used inside a conditional edge's routing function to spawn multiple parallel invocations of the same node.

```python
from langgraph.constants import Send

def fan_out(state: State) -> list[Send]:
    return [
        Send("reviewer", {"file": f, "reviewer_id": i})
        for i, f in enumerate(state["files_to_review"])
    ]

builder.add_conditional_edges("planner", fan_out, ["reviewer"])
builder.add_node("reviewer", review_node)
builder.add_edge("reviewer", "aggregator")
```

Each `Send(node_name, arg)` creates an independent execution of `node_name` with `arg` as the state update. All parallel executions must complete before the graph continues past the fan-in point.

---

## LangGraph Platform Configuration

The `langgraph.json` file defines deployment configuration for LangGraph Platform.

### Schema

```json
{
  "graphs": {
    "agent": "./src/agent.py:graph",
    "reviewer": "./src/reviewer.py:workflow"
  },
  "dependencies": ["."],
  "env": ".env",
  "dockerfile_lines": [],
  "python_version": "3.12",
  "pip_config_file": null
}
```

| Field | Description |
|-------|-------------|
| `graphs` | Map of graph IDs to Python import paths (`module:variable`) |
| `dependencies` | List of paths to pip-installable directories |
| `env` | Path to environment file |
| `dockerfile_lines` | Additional Dockerfile instructions |
| `python_version` | Python version for deployment |
| `pip_config_file` | Optional pip config path |

### Deployment

```bash
langgraph up                    # Start local dev server
langgraph deploy                # Deploy to LangGraph Cloud
```

---

## Subgraph

A compiled `CompiledStateGraph` can be added as a node in another graph. The subgraph has its own independent state space.

```python
subgraph_builder = StateGraph(SubState)
# ... define subgraph nodes and edges ...
subgraph = subgraph_builder.compile()

main_builder = StateGraph(MainState)
main_builder.add_node("sub_processor", subgraph)
main_builder.add_edge(START, "sub_processor")
main_builder.add_edge("sub_processor", END)
main_graph = main_builder.compile()
```

**Important**: Field name collisions between parent and subgraph states cause unexpected behavior. Use distinct field names or map states at the boundary.

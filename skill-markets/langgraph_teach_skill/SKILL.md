---
name: langgraph_teach_skill
description: "Teaches how to use the LangGraph framework for building stateful, multi-actor agent systems with graphs, nodes, edges, checkpointing, streaming, and human-in-the-loop. This skill should be used when the user needs to build LangGraph-based agent workflows, implement multi-agent patterns (Supervisor/Swarm/Map-Reduce), configure checkpoints, set up streaming, or design stateful graph-based agents. Triggers on: LangGraph, StateGraph, agent graph, multi-agent workflow, checkpoint, streaming agent, human-in-the-loop, LangGraph Platform, langgraph.json."
intent: Teaches how to use the LangGraph framework for building s...
category: orchestration
audience: [agent, designer]
---
# LangGraph Teach Skill

## What is LangGraph

LangGraph is a graph-based orchestration framework within the LangChain ecosystem for building **stateful, multi-actor agent workflows**. It models agent decision-making and tool-calling loops through a **node-edge graph model**, where each node is a computation step and each edge defines data flow. Unlike linear chains, LangGraph supports conditional branching, loops, parallel fan-out, and human-in-the-loop interrupts—all backed by built-in checkpointing for persistence and recovery.

## When to Use LangGraph

- Need precise control over each step of an agent's execution flow
- Need to persist conversation state across sessions or interruptions (Checkpoint)
- Need to orchestrate multiple agents collaborating (Supervisor / Swarm / Map-Reduce)
- Need human-in-the-loop interrupts for approval or guidance
- Need streaming output and real-time progress feedback
- Need dynamic parallel task distribution (fan-out / fan-in)
- Need subgraph composition for modular, reusable workflows

## Installation and Setup

```bash
pip install langgraph langgraph-sdk
```

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langgraph.constants import Send
```

## Minimum Viable Graph

The smallest working LangGraph agent—a single chat node with a message state:

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chat_node(state: State) -> dict:
    # Replace with actual LLM call: model.invoke(state["messages"])
    response = f"Echo: {state['messages'][-1].content}"
    return {"messages": [AIMessage(content=response)]}

builder = StateGraph(State)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

graph = builder.compile()
result = graph.invoke({"messages": [HumanMessage(content="Hi")]})
```

Three things happen here: (1) a `StateGraph` is created with a typed state schema, (2) a single node is registered and connected from `START` to `END`, and (3) `compile()` produces a runnable graph that can be invoked with initial state.

## Core API Catalog

The LangGraph API surface, ranked by importance:

| API | Role |
|-----|------|
| **StateGraph** | Graph builder: `add_node`, `add_edge`, `add_conditional_edges`, `compile` |
| **State definition** | `TypedDict` + `Annotated` reducer (overwrite / append / custom) |
| **Checkpointer** | `MemorySaver` / `SqliteSaver` / `PostgresSaver` for state persistence |
| **interrupt + Command** | Human-in-the-loop: pause, review, resume with `Command(resume=...)` |
| **Send API** | Dynamic parallel fan-out: `Send(node, arg)` from conditional edge |
| **Subgraph** | Compose graphs: `builder.add_node("sub", subgraph)` |
| **stream / astream** | Streaming modes: `values`, `updates`, `messages`, `custom`, `debug` |
| **LangGraph Platform** | `langgraph.json` config + remote deployment + LangGraph Studio |

For full method signatures, see `references/api-reference.md`.

## State Definition Patterns

Three patterns for defining how node outputs merge into shared state:

### 1. Plain TypedDict (default overwrite)

```python
class State(TypedDict):
    counter: int          # Last write wins
    status: str           # Last write wins
```

Each node's return dict overwrites matching keys. Suitable for single-value fields like counters, flags, or configuration.

### 2. Annotated with add_messages (intelligent append)

```python
from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

`add_messages` appends new messages and handles `HumanMessage`/`AIMessage`/`ToolMessage` with deduplication by ID. This is the standard pattern for chat-based agents. **Requirement**: messages must be `BaseMessage` subclasses. Plain strings or dicts will not work—use a custom reducer if needed.

### 3. Annotated with custom reducer (custom merge logic)

```python
def merge_lists(left: list, right: list) -> list:
    return (left or []) + (right or [])

class State(TypedDict):
    logs: Annotated[list, merge_lists]
    scores: Annotated[dict, lambda l, r: {**l, **r}]
```

Custom reducers give full control over merge behavior—useful for aggregating logs, merging nested dicts, or deduplicating tool results.

## Agent Loop Pattern

The canonical agent loop—LLM decides whether to call tools or respond directly:

```
START → model_node ──[has tool_calls?]──→ tools_node → model_node
                    ──[no tool_calls]──→ END
```

```python
def should_continue(state: AgentState) -> str:
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return END

builder = StateGraph(AgentState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "model")
builder.add_conditional_edges("model", should_continue, {
    "tools": "tools",
    END: END,
})
builder.add_edge("tools", "model")
```

### Safety Valve

Prevent infinite loops with a max-turns guard:

```python
MAX_TURNS = 25

def should_continue(state: AgentState) -> str:
    if state.get("turn_count", 0) >= MAX_TURNS:
        return END
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return END
```

For full Agent Loop details including error handling, see `references/patterns.md`.

## Multi-Agent Patterns

### Supervisor (Central Router)

A supervisor agent routes tasks to specialized worker agents. Each worker is a compiled subgraph. The supervisor inspects state and decides which worker to invoke next.

```
Supervisor ──→ Worker A (search)
           ──→ Worker B (code)
           ──→ Worker C (summarize)
           ──→ END
```

Use when: tasks have clear categories, one decision-maker can route effectively, and workers are independent.

For implementation with subgraphs, see `references/patterns.md`.

### Swarm (Shared State + Direct Handoff)

Agents share a single state graph. Each agent node can directly hand off to another agent by updating a routing field. No central supervisor—agents self-organize.

```
Agent A ←→ Agent B ←→ Agent C
   ↕          ↕          ↕
     Shared State (messages, context)
```

Use when: agents need fluid, peer-to-peer interaction without a bottleneck.

For Swarm handoff implementation, see `references/patterns.md`.

### Map-Reduce (Dynamic Parallel Fan-Out)

Use the `Send` API to dynamically spawn parallel worker invocations, then collect results with a reducer node.

```python
from langgraph.constants import Send

def continue_to_jobs(state):
    return [Send("worker", {"task": t}) for t in state["tasks"]]

builder.add_conditional_edges("dispatcher", continue_to_jobs, ["worker"])
```

Use when: a list of independent items must be processed in parallel (e.g., reviewing multiple files, searching multiple sources).

For the full Map-Reduce pattern, see `references/patterns.md`.

## Crucial Caveats / Traps

1. **`add_messages` requires `BaseMessage` subclasses.** Passing plain strings or dicts will silently break. Use a custom reducer for non-message list types.

2. **Conditional edge route values must exactly match `path_map` keys.** A typo in the returned string causes silent failure—the graph continues but may route incorrectly. Always validate route functions with unit tests.

3. **`MemorySaver` is NOT production-safe.** It stores all checkpoints in RAM and loses them on process restart. Use `SqliteSaver` for single-server or `PostgresSaver` for multi-server deployments.

4. **`interrupt()` requires a checkpointer.** Calling `interrupt()` on a graph compiled without a checkpointer raises a runtime error. Always pass `checkpointer=your_saver` to `compile()`.

5. **State bloat is the #1 performance killer.** Storing large objects (full documents, images, embeddings) in graph state causes serialization overhead on every checkpoint. Store references in state and keep actual data in external storage (Redis, DB, S3).

6. **Subgraphs have independent state spaces.** A field name collision between parent and subgraph states causes unexpected overwrites. Use distinct field names or explicit state mapping at the boundary.

7. **Never use bare `asyncio.create_task` for graph execution.** LangGraph's concurrency safety relies on `graph.ainvoke()` and `graph.astream()` as the entry points. Directly spawning tasks bypasses internal synchronization.

8. **Streaming modes are not interchangeable.** `stream_mode="values"` emits full state after each super-step; `stream_mode="updates"` emits only the delta. Choose based on whether the consumer needs full context or just the change.

## LangGraph vs DeepAgents

- **LangGraph**: A low-level graph orchestration framework. Manually control every node and edge. Best for complex workflows requiring fine-grained control over branching, parallelism, and state transitions.
- **DeepAgents**: A high-level agent framework (built on LangGraph). Ships with built-in filesystem tools, sub-agent delegation, and middleware. Best for rapidly building multi-agent systems with less boilerplate.

Choose LangGraph when you need architectural control; choose DeepAgents when you need speed of development with opinionated defaults.

---

## References

- For full API signatures and parameter details: `references/api-reference.md`
- For design patterns with complete code examples: `references/patterns.md`

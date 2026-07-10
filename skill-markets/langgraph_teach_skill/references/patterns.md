# LangGraph Design Patterns

Production-ready design patterns for building LangGraph-based agent systems.

---

## 1. Agent Loop + Safety Valve

The foundational pattern: LLM calls tools in a loop until it produces a final answer.

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

MAX_TURNS = 25

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    turn_count: int

def call_model(state: AgentState) -> dict:
    response = model.bind_tools(tools).invoke(state["messages"])
    return {
        "messages": [response],
        "turn_count": state.get("turn_count", 0) + 1,
    }

def should_continue(state: AgentState) -> str:
    if state.get("turn_count", 0) >= MAX_TURNS:
        return END
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

graph = builder.compile(checkpointer=MemorySaver())
```

**Key design decisions**:
- `MAX_TURNS` prevents infinite tool-calling loops. Adjust based on expected complexity.
- The checkpointer enables recovery if the agent is interrupted mid-loop.
- `ToolNode` from `langgraph.prebuilt` handles `ToolMessage` construction automatically.

---

## 2. Supervisor Multi-Agent

A supervisor agent routes tasks to specialized worker subgraphs.

```python
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict, Literal

class SupervisorState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str

# ── Worker subgraphs (each is a compiled graph) ──

def make_search_agent():
    builder = StateGraph(AgentState)
    # ... define search agent ...
    return builder.compile()

def make_code_agent():
    builder = StateGraph(AgentState)
    # ... define code agent ...
    return builder.compile()

search_agent = make_search_agent()
code_agent = make_code_agent()

# ── Supervisor ──

def supervisor_node(state: SupervisorState) -> dict:
    response = model.invoke([
        SystemMessage(content="Route to: SEARCH, CODE, or FINISH."),
        *state["messages"],
    ])
    return {"messages": [response], "next_agent": response.content.strip()}

def route_to_agent(state: SupervisorState) -> str:
    return state["next_agent"]

builder = StateGraph(SupervisorState)
builder.add_node("supervisor", supervisor_node)
builder.add_node("search_agent", search_agent)
builder.add_node("code_agent", code_agent)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route_to_agent, {
    "SEARCH": "search_agent",
    "CODE": "code_agent",
    "FINISH": END,
})
# Workers loop back to supervisor
builder.add_edge("search_agent", "supervisor")
builder.add_edge("code_agent", "supervisor")

graph = builder.compile()
```

**When to use**: Tasks naturally fall into categories (search, code, analysis). One decision-maker can route effectively. Workers don't need direct communication.

**When not to use**: Workers need fluid back-and-forth (use Swarm). Too many workers create a supervisor bottleneck.

---

## 3. Swarm Handoff

Agents share a single state and hand off to each other directly via a routing field.

```python
from typing import Annotated, TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class SwarmState(TypedDict):
    messages: Annotated[list, add_messages]
    active_agent: str
    context: dict

def researcher_node(state: SwarmState) -> dict:
    response = model.invoke([
        SystemMessage(content="Research agent. Hand off to: WRITER or ANALYST."),
        *state["messages"],
    ])
    # Parse handoff from response
    next_agent = parse_handoff(response.content)
    return {
        "messages": [response],
        "active_agent": next_agent or "researcher",
    }

def writer_node(state: SwarmState) -> dict:
    response = model.invoke([
        SystemMessage(content="Writer agent. Hand off to: RESEARCHER or FINISH."),
        *state["messages"],
    ])
    next_agent = parse_handoff(response.content)
    return {
        "messages": [response],
        "active_agent": next_agent or "writer",
    }

def route_by_agent(state: SwarmState) -> str:
    return state["active_agent"]

builder = StateGraph(SwarmState)
builder.add_node("researcher", researcher_node)
builder.add_node("writer", writer_node)
builder.add_node("analyst", analyst_node)

builder.add_edge(START, "researcher")
builder.add_conditional_edges("researcher", route_by_agent, {
    "researcher": "researcher",
    "writer": "writer",
    "analyst": "analyst",
    "FINISH": END,
})
builder.add_conditional_edges("writer", route_by_agent, {
    "researcher": "researcher",
    "writer": "writer",
    "FINISH": END,
})
# Similar for analyst...

graph = builder.compile()
```

**Key design decisions**:
- `active_agent` is the single routing field—keep it simple.
- Agents share all state. For privacy, use subgraphs with isolated state instead.
- Handoff parsing should be robust. Consider structured output (JSON mode) for reliable routing.

---

## 4. Map-Reduce Parallel

Dynamically spawn parallel worker tasks, then aggregate results.

```python
from langgraph.constants import Send
from typing import Annotated, TypedDict

class ParallelState(TypedDict):
    tasks: list[str]
    results: Annotated[list, lambda l, r: (l or []) + (r or [])]
    final_summary: str

def dispatcher(state: ParallelState) -> list[Send]:
    """Fan out: create one worker invocation per task."""
    return [
        Send("worker", {"task": task, "index": i})
        for i, task in enumerate(state["tasks"])
    ]

def worker(state: dict) -> dict:
    """Process a single task. Receives {task, index} from Send."""
    result = process_task(state["task"])
    return {"results": [{"task": state["task"], "result": result}]}

def aggregator(state: ParallelState) -> dict:
    """Fan in: summarize all worker results."""
    summary = summarize(state["results"])
    return {"final_summary": summary}

builder = StateGraph(ParallelState)
builder.add_node("dispatcher", lambda s: {})
builder.add_node("worker", worker)
builder.add_node("aggregator", aggregator)

builder.add_edge(START, "dispatcher")
builder.add_conditional_edges("dispatcher", dispatcher, ["worker"])
builder.add_edge("worker", "aggregator")
builder.add_edge("aggregator", END)

graph = builder.compile()
```

**Execution flow**: `START -> dispatcher -> [worker, worker, worker...] -> aggregator -> END`. All workers run in parallel. The graph waits for all workers to complete before entering the aggregator.

**When to use**: Processing a list of independent items (files, search results, data rows). The reducer on `results` automatically collects all worker outputs.

---

## 5. Human-in-the-Loop (HITL) Approval Flow

Pause execution for human review, then resume with approval or rejection.

```python
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

def sensitive_action_node(state: State) -> dict:
    """Pause before executing a sensitive action."""
    # Show what's about to happen
    approval = interrupt({
        "action": state["pending_action"],
        "details": state["action_details"],
        "message": "Approve this action?",
    })
    if approval.get("approved"):
        result = execute_action(state["pending_action"])
        return {"action_result": result, "approved": True}
    return {"approved": False, "action_result": "Rejected by human"}

# Compile with interrupt point
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["sensitive_action_node"],  # Always pause here
)

# ── First invocation: runs until interrupt ──
config = {"configurable": {"thread_id": "session-1"}}
await graph.ainvoke(initial_input, config)
# Graph is now paused at sensitive_action_node

# ── Check pending interrupts ──
snapshot = await graph.aget_state(config)
for interrupt_data in snapshot.interrupts:
    print(interrupt_data.value)  # The dict passed to interrupt()

# ── Resume with approval ──
await graph.ainvoke(
    Command(resume={"approved": True, "comment": "Looks good"}),
    config,
)
```

**Key design decisions**:
- `interrupt_before` on `compile()` creates a guaranteed pause point—ideal for always-required approvals.
- `interrupt()` inside a node creates a conditional pause—ideal for situational approvals.
- The checkpointer is mandatory. Without it, the graph cannot save state before pausing.

---

## 6. Subgraph Composition

Reuse compiled graphs as nodes in larger workflows.

```python
# ── Define a reusable analysis subgraph ──

class AnalysisState(TypedDict):
    document: str
    analysis_result: str

def analyze(state: AnalysisState) -> dict:
    result = model.invoke(f"Analyze: {state['document']}")
    return {"analysis_result": result}

analysis_builder = StateGraph(AnalysisState)
analysis_builder.add_node("analyze", analyze)
analysis_builder.add_edge(START, "analyze")
analysis_builder.add_edge("analyze", END)
analysis_graph = analysis_builder.compile()

# ── Use in a main workflow ──

class MainState(TypedDict):
    documents: list[str]
    all_analyses: Annotated[list, merge_lists]
    final_report: str

def fan_to_analysis(state: MainState) -> list[Send]:
    return [
        Send("analyze_doc", {"document": doc})
        for doc in state["documents"]
    ]

main_builder = StateGraph(MainState)
main_builder.add_node("analyze_doc", analysis_graph)  # Subgraph as node
main_builder.add_node("report", report_node)
main_builder.add_edge(START, "analyze_doc")
main_builder.add_edge("analyze_doc", "report")
main_builder.add_edge("report", END)
main_graph = main_builder.compile()
```

**Key design decisions**:
- The subgraph has its own state (`AnalysisState`). Field names in `AnalysisState` do NOT automatically appear in `MainState`.
- If both states have a field named `result`, the subgraph writes to its own `result`, not the parent's.
- For parent-subgraph state bridging, use explicit field mapping at the boundary node.

---

## 7. Streaming with Interrupt Recovery

Stream agent output while supporting interruption and resumption.

```python
from langgraph.types import Command
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("agent.db")
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "session-1"}}

async def stream_with_interrupt():
    try:
        async for chunk in graph.astream(
            input_data, config, stream_mode="messages"
        ):
            # chunk is an AIMessageChunk with token-level content
            print(chunk.content, end="", flush=True)
    except Exception:
        # On reconnect, resume from last checkpoint
        async for chunk in graph.astream(
            None, config, stream_mode="messages"
        ):
            print(chunk.content, end="", flush=True)
```

**Key design decisions**:
- Use `SqliteSaver` or `PostgresSaver` for durable checkpoints across reconnects.
- Pass `None` as input on resume—the graph continues from the last checkpoint.
- `stream_mode="messages"` gives token-level chunks for real-time display.

---

## 8. State De-Bloating Pattern

Prevent state from growing unboundedly by storing references instead of data.

```python
# BAD: stores full document in state
class BloatedState(TypedDict):
    documents: list[str]  # Full text of every document
    messages: Annotated[list, add_messages]

# GOOD: stores references, fetches on demand
class LeanState(TypedDict):
    document_ids: list[str]  # IDs only
    messages: Annotated[list, add_messages]

def retrieval_node(state: LeanState) -> dict:
    # Fetch full documents from external storage when needed
    docs = fetch_from_db(state["document_ids"][-1])  # Only the current one
    context = format_docs(docs)
    return {"messages": [HumanMessage(content=context)]}
```

**Key design decisions**:
- State should contain identifiers, not large payloads.
- Use external storage (Redis, PostgreSQL, S3) for document bodies, embeddings, and images.
- Every checkpoint serializes the full state. A 10MB state with 50 checkpoints = 500MB in memory/storage.
- Consider a custom reducer that caps list length (e.g., keep last 50 messages only).

# DeepAgents Design Patterns

Production-proven architecture patterns for DeepAgents.

---

## Pattern 1: Three-Agent Research-Code-Review Pipeline

**Use when:** Building a system that researches, implements, and validates code.

**Architecture:**

```
User Request
    │
    ▼
┌──────────────┐    task("researcher")    ┌──────────────┐
│ Orchestrator │ ───────────────────────► │  Researcher   │
│  (Main Agent)│ ◄─────────────────────── │  (SubAgent)   │
│              │    research report       │  tools:       │
│  tools:      │                          │  web_search   │
│  write_todos │    task("coder")         └──────────────┘
│              │ ───────────────────────► ┌──────────────┐
│              │ ◄─────────────────────── │    Coder      │
│              │    code output           │  (SubAgent)   │
│              │                          │  tools:       │
│              │    task("reviewer")      │  write_file   │
│              │ ───────────────────────► ┌──────────────┐
│              │ ◄─────────────────────── │   Reviewer    │
│              │    review report         │  (SubAgent)   │
└──────────────┘                          │  tools:       │
                                          │  read_file    │
                                          │  grep         │
                                          └──────────────┘
```

**Implementation:**

```python
from deepagents import create_deep_agent, SubAgent

researcher = SubAgent(
    name="researcher",
    description="Search and analyze technical information. Use for research tasks.",
    system_prompt="You are a technical researcher. Search for information and produce structured reports.",
    tools=[web_search],
)

coder = SubAgent(
    name="coder",
    description="Write and implement code based on requirements. Use for coding tasks.",
    system_prompt="You are a software engineer. Write clean, well-documented code with error handling.",
    tools=[write_file, edit_file],
)

reviewer = SubAgent(
    name="reviewer",
    description="Review code for correctness, security, and best practices.",
    system_prompt="You are a code reviewer. Check for bugs, security issues, and style violations.",
    tools=[read_file, grep, glob],
)

agent = create_deep_agent(
    model=model,
    subagents=[researcher, coder, reviewer],
    system_prompt="""You are a project orchestrator. For any task:
1. Use write_todos to plan the work
2. Delegate research to the researcher first
3. Delegate implementation to the coder based on research
4. Delegate review to the reviewer after coding
5. Present the final results to the user""",
)
```

**Key benefits:**
- Each sub-agent has a focused, non-overlapping responsibility
- Context isolation prevents research details from polluting code generation
- Reviewer has read-only access (via permissions) for safety
- Pipeline is naturally sequential but each phase is independently traceable

---

## Pattern 2: Tiered Permission Model

**Use when:** Agents need different access levels to different parts of the filesystem.

**Three-tier model:**

```
Zone 1: /public/      -> allow read, allow write   (open workspace)
Zone 2: /workspace/   -> allow read, deny write    (reference only)
Zone 3: /secrets/     -> interrupt write           (approval required)
Zone 4: /**            -> deny all                  (catch-all deny)
```

**Implementation:**

```python
from deepagents import create_deep_agent, FilesystemPermission

permissions = [
    # Tier 1: Open workspace
    FilesystemPermission(
        operations=["read", "write"],
        paths=["/public/**"],
        mode="allow",
    ),
    # Tier 2: Reference-only (read but no write)
    FilesystemPermission(
        operations=["read"],
        paths=["/workspace/**"],
        mode="allow",
    ),
    FilesystemPermission(
        operations=["write"],
        paths=["/workspace/**"],
        mode="deny",
    ),
    # Tier 3: Approval-gated writes
    FilesystemPermission(
        operations=["read"],
        paths=["/secrets/**"],
        mode="allow",
    ),
    FilesystemPermission(
        operations=["write"],
        paths=["/secrets/**"],
        mode="interrupt",
    ),
    # Tier 4: Default deny
    FilesystemPermission(
        operations=["read", "write"],
        paths=["/**"],
        mode="deny",
    ),
]

agent = create_deep_agent(
    model=model,
    permissions=permissions,
    checkpointer=SqliteSaver.from_conn_string("checkpoints.db"),
)
```

**Sub-agent permission override:**

```python
readonly_auditor = SubAgent(
    name="auditor",
    description="Audit files without modifying them",
    system_prompt="You audit files for compliance. Never modify files.",
    permissions=[
        FilesystemPermission(operations=["read"], paths=["/**"], mode="allow"),
        FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
    ],
)
```

---

## Pattern 3: Long-Term Memory Separation with CompositeBackend

**Use when:** Separating temporary workspace files from persistent knowledge.

**Architecture:**

```
Agent File Operations
    │
    ▼
CompositeBackend
    ├── /memories/  ──► StoreBackend     (persistent, cross-session)
    ├── /workspace/ ──► FilesystemBackend (disk, project files)
    └── default      ──► StateBackend     (temporary, session-only)
```

**Implementation:**

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Pre-seed persistent memories
store.put(("agent",), "/memories/coding-style.md",
    create_file_data("# Coding Style\n- Use snake_case\n- Type hints required\n- Max 80 chars per line"))

agent = create_deep_agent(
    model=model,
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(namespace=lambda rt: ("agent",)),
            "/workspace/": FilesystemBackend(root_dir="./workspace", virtual_mode=True),
        },
    ),
    store=store,
    memory=["/memories/coding-style.md"],
    system_prompt="""You have three storage zones:
- /memories/ -> Persistent knowledge (survives restarts)
- /workspace/ -> Project files on disk
- Default -> Temporary scratch space (cleared each session)
Use /memories/ for rules and preferences. Use /workspace/ for code output.
Use default for intermediate calculations.""",
)
```

**Key benefits:**
- Memory files survive agent restarts (StoreBackend is persistent)
- Project files are on real disk for git integration
- Temporary files don't accumulate on disk
- Each zone has independent lifecycle management

---

## Pattern 4: Progressive Skill Loading

**Use when:** Agent needs access to large domain knowledge bases without consuming context window.

**Architecture:**

```
Startup:                    Activation:              Execution:
┌─────────────────┐        ┌─────────────────┐     ┌─────────────────┐
│ Skill Registry  │        │ SKILL.md body   │     │ references/     │
│ (name+desc only)│───────►│ (full content)  │────►│ scripts/        │
│                 │        │                 │     │ assets/         │
│ Token cost: ~50 │        │ Token cost: ~2k │     │ Token cost: ~5k │
│ per skill       │        │ per skill       │     │ per resource    │
└─────────────────┘        └─────────────────┘     └─────────────────┘
```

**Skill directory structure:**

```
skills/
  database-design/
    SKILL.md              # L1+L2: YAML frontmatter + design methodology
    references/
      normalization.md    # L3: Normalization rules
      indexing.md         # L3: Index strategy guide
      postgres-specific.md # L3: PostgreSQL specifics
    scripts/
      schema_validator.py # L3: Validation script
    assets/
      templates/          # L3: Schema templates
```

**SKILL.md format:**

```markdown
---
name: database-design
description: >
  Database schema design skill. Covers normalization, indexing,
  and query optimization. Activate when designing or reviewing
  database schemas, SQL queries, or data models.
---

# Database Design Skill

## Design Process
1. Gather requirements
2. Identify entities and relationships
3. Apply normalization (see references/normalization.md)
4. Design indexes (see references/indexing.md)
5. Generate DDL

## Platform-Specific
For PostgreSQL, see references/postgres-specific.md.
For validation, run scripts/schema_validator.py.
```

**Implementation:**

```python
agent = create_deep_agent(
    model=model,
    skills=["./skills/"],
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    system_prompt="You have domain skills. Activate relevant skills for specialized tasks.",
)
```

**Key benefits:**
- Dozens of skills can be registered without blowing up context
- Only the skills actually needed consume tokens
- References allow even deeper knowledge without always loading it
- Skills are version-controllable markdown files

---

## Pattern 5: HITL Approval Flow with Checkpoint Recovery

**Use when:** Critical operations require human approval before execution.

**Flow:**

```
Agent decides to write_file("/prod/config.yaml")
    │
    ▼
interrupt_on check: write_file=True
    │
    ▼
[EXECUTION PAUSED] ◄── State saved to checkpointer
    │
    ▼
Human reviews proposed change
    │
    ├── Approve  ──► Command(resume={"decision": "approve"})
    │                   │
    │                   ▼
    │               write_file executes
    │                   │
    │                   ▼
    │               Agent continues
    │
    ├── Edit     ──► Command(resume={"decision": "approve", "modified": {...}})
    │                   │
    │                   ▼
    │               write_file executes with modified content
    │
    └── Reject   ──► Command(resume={"decision": "reject", "reason": "..."})
                        │
                        ▼
                    Agent receives rejection, adjusts plan
```

**Implementation:**

```python
from deepagents import create_deep_agent, FilesystemPermission
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import Command

DB_URI = "postgresql://user:pass@host:5432/deepagents"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()

    agent = create_deep_agent(
        model=model,
        checkpointer=checkpointer,
        interrupt_on={
            "write_file": True,
            "edit_file": True,
            "execute": True,
        },
        permissions=[
            FilesystemPermission(
                operations=["write"],
                paths=["/prod/**", "/secrets/**"],
                mode="interrupt",
            ),
        ],
        system_prompt="""You are a cautious deployment agent.
Always explain what you're about to write and why before writing.
Wait for approval before making changes to production files.""",
    )

    # Usage in an approval service:
    config = {"configurable": {"thread_id": "deploy-2024-001"}}

    # First call: will be interrupted
    try:
        result = agent.invoke(
            {"messages": [HumanMessage(content="Update /prod/config.yaml with new settings")]},
            config=config,
        )
    except Exception as e:
        # Agent paused — present to human for approval
        pass

    # After human approves:
    result = agent.invoke(
        Command(resume={"decision": "approve"}),
        config=config,
    )
```

**Key benefits:**
- PostgresSaver ensures interrupt state survives process restarts
- Approval decisions are auditable via state history
- Modified approvals allow human correction without full rejection
- Same config works for both `interrupt_on` and `permissions(mode="interrupt")`

---

## Pattern 6: Streaming Output with Interrupt-Resume

**Use when:** Building a chat UI that shows agent progress in real time, with approval support.

**Architecture:**

```
Client (WebSocket)          Server (FastAPI)              DeepAgent
    │                            │                            │
    │── connect ────────────────►│                            │
    │◄── {"type": "connected"} ──│                            │
    │                            │                            │
    │── {"type": "message"} ────►│                            │
    │                            │── astream() ──────────────►│
    │                            │◄── chunk (thinking) ──────│
    │◄── {"type": "thinking"} ───│                            │
    │                            │◄── chunk (tool_call) ─────│
    │◄── {"type": "tool_call"} ──│                            │
    │                            │◄── INTERRUPT ─────────────│
    │◄── {"type": "approval_needed"} ──│                      │
    │                            │                            │
    │── {"type": "approve"} ────►│                            │
    │                            │── Command(resume=...) ────►│
    │                            │◄── chunk (response) ──────│
    │◄── {"type": "response"} ───│                            │
    │◄── {"type": "done"} ───────│                            │
```

**Implementation:**

```python
# server.py
from fastapi import FastAPI, WebSocket
from deepagents import create_deep_agent
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import Command
import json

app = FastAPI()

@app.websocket("/agent/stream")
async def agent_stream(ws: WebSocket):
    await ws.accept()
    thread_id = ws.query_params.get("thread_id", "default")

    agent = build_agent()  # Factory function
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        data = await ws.receive_text()
        msg = json.loads(data)

        if msg["type"] == "message":
            # Stream agent response
            try:
                async for chunk, metadata in agent.astream(
                    {"messages": [HumanMessage(content=msg["content"])]},
                    config=config,
                    stream_mode="messages",
                ):
                    content = getattr(chunk, "content", "")
                    tool_calls = getattr(chunk, "tool_calls", None)

                    if tool_calls:
                        await ws.send_json({
                            "type": "tool_call",
                            "tools": [t["name"] for t in tool_calls],
                        })
                    elif content:
                        await ws.send_json({
                            "type": "message",
                            "role": type(chunk).__name__,
                            "content": content,
                        })

                await ws.send_json({"type": "done"})

            except Exception as e:
                if "interrupt" in str(e).lower():
                    await ws.send_json({
                        "type": "approval_needed",
                        "detail": str(e),
                    })

        elif msg["type"] == "approve":
            # Resume after interrupt
            decision = msg.get("decision", "approve")
            resume_cmd = Command(resume={"decision": decision})

            if "modified" in msg:
                resume_cmd = Command(resume={
                    "decision": "approve",
                    "modified": msg["modified"],
                })

            async for chunk, metadata in agent.astream(
                resume_cmd, config=config, stream_mode="messages",
            ):
                content = getattr(chunk, "content", "")
                if content:
                    await ws.send_json({
                        "type": "message",
                        "role": type(chunk).__name__,
                        "content": content,
                    })

            await ws.send_json({"type": "done"})

        elif msg["type"] == "reject":
            resume_cmd = Command(resume={
                "decision": "reject",
                "reason": msg.get("reason", "Rejected by user"),
            })
            async for chunk, metadata in agent.astream(
                resume_cmd, config=config, stream_mode="messages",
            ):
                pass  # Agent processes rejection, may propose alternative
            await ws.send_json({"type": "done"})
```

**Key benefits:**
- Users see agent progress in real time (tool calls, thinking)
- Interrupts integrate naturally into the streaming flow
- Same WebSocket handles both streaming and approval
- Thread-based isolation keeps multiple users independent

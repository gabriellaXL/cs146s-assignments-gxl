# Week 5 Write-up — Agentic Development with Warp

## Overview

This week used the `week5/` FastAPI + SQLite starter as a playground for two
types of Warp automation: Warp Drive objects (project rule, saved prompts, MCP
server) and a multi-agent parallel development workflow using `git worktree`.

Two tasks from `TASKS.md` were completed:
- **Task 3** — Full Notes CRUD with optimistic UI updates (medium)
- **Task 4** — Action items: filters and bulk complete (medium)

Final state: 33/33 tests passing, lint clean, all changes merged to `main`.

---

## Part I — Warp Drive Automations

### Automation 1: Project Rule (`week5/WARP.md`)

**Goal:** Eliminate the need to re-explain project context at the start of every
agent session.

**How it works:** Warp auto-detects `WARP.md` (or `AGENTS.md`) in a project
directory and injects its contents as context before any agent message. No
manual steps needed after the file exists in the repo.

**Contents covered:**
- Scope: all changes stay within `week5/`
- Tech stack: FastAPI, SQLite, SQLAlchemy 2.x, Pydantic v2
- Directory layout with file-level annotations
- Conventions: where schemas, models, routers, services go
- Completion checklist: `make format` → `make lint` → `make test` → `docs/API.md`
- Database notes (default path, test isolation, seed behaviour)

**Before vs. After:**

Before: Each session required several context-setting turns before getting to
work. Agents would use wrong file locations, incompatible Pydantic syntax, or
skip the lint step. Two different sessions would produce inconsistent code styles.

After: The agent already knows the rules before the first message. The first
prompt can be a direct task instruction. Conventions are enforced consistently
across all sessions.

**Pain point resolved:** Context drift. Agents maintain no memory between
sessions; WARP.md compensates by front-loading all the project knowledge that
would otherwise be re-explained every time.

---

### Automation 2: Saved Prompt — Test Runner with Flaky-Test Re-run

**Name:** `week5 — Run Tests`

**Goal:** Wrap the full pytest QA cycle (run → diagnose → retry flaky tests →
summarise) into a single reusable invocation.

**Inputs:** None (runs against `week5/` current state).

**Steps the agent executes:**
1. `PYTHONPATH=. pytest -v backend/tests/ --tb=short`
2. For any FAILED test: quote the exact assertion error, file, and line number
3. If a failure has no assertion error (timeout, import error, OS lock) — likely
   flaky — re-run that test once with `--tb=long`
4. Output: "N passed, N failed, N skipped" with a one-liner per remaining failure

**Before vs. After:**

Before: After each code change, manually running `make test`, reading raw
pytest output, deciding whether to retry, manually copy-pasting errors to the
agent. On Windows, SQLite file-lock errors (`PermissionError: [WinError 32]`)
during test teardown caused false alarms that required manual investigation.

After: One prompt invocation produces a structured diagnosis with explicit
flakiness detection. The retry heuristic filtered out the Windows teardown
noise before it reached the developer.

**Pain point resolved:** The "is this failure real or transient?" decision loop
was manual and slow. Automating the retry with an explicit heuristic separates
environmental noise from real bugs.

**Reusability:** Works for any Python/pytest project — only the test path needs
adapting.

---

### Automation 3: Saved Prompt — Docs Sync (OpenAPI → `docs/API.md`)

**Name:** `week5 — Sync API Docs`

**Goal:** Keep `docs/API.md` current with the live API spec without running the
server.

**Inputs:** None (runs against `week5/` current state).

**Steps the agent executes:**
1. Extract the current OpenAPI spec by importing the FastAPI `app` object and
   calling `app.openapi()` — no running server required
2. Parse all routes: method, path, summary, parameters, request/response schemas
3. Compare against the existing `docs/API.md` and list additions, removals, and
   schema changes as a delta at the top
4. Rewrite `docs/API.md` in clean Markdown organised by router tag

**Before vs. After:**

Before: API documentation was written manually and became stale immediately
after any endpoint change. In practice it was skipped entirely in fast-moving
development.

After: Running this prompt after any backend change produces an up-to-date
reference in seconds. The delta report also catches accidental breaking changes
(e.g. a parameter type change that would break clients).

**Pain point resolved:** Documentation rot. FastAPI generates an OpenAPI spec
automatically, but it is not human-readable Markdown. This prompt bridges the
gap and keeps the docs in sync as a byproduct of normal development.

**Reusability:** Works for any FastAPI project; only the `app` import path
needs adapting.

---

### Automation 4: GitHub MCP Server

**Configuration:** Installed via Warp → Settings → MCP Servers. Full JSON
configuration archived in `week5/docs/warp-automations.md`.

**Goal:** Allow agents to interact with the repository autonomously — branch
creation, commit history inspection, PR drafting.

**Capabilities used:**
- Inspect commit history and branch status without leaving the agent session
- Write PR descriptions that summarise the diff between a feature branch and main
- Verify branch state after multi-agent work (used to confirm Task 4's commits
  were on the correct branch)

**Before vs. After:**

Before: All git operations were manual terminal commands. After the agent
finished coding, the developer still had to handle all version control work by
hand. Verifying what a separate agent had done required switching context to
a terminal.

After: The agent can query branch state, inspect commits, and prepare a PR
description as part of the same conversation that produced the code. In the
multi-agent scenario, GitHub MCP was used to verify Task 4's branch state
without leaving the integration session.

**Pain point resolved:** The "last mile" after coding — version control and
review preparation — is repetitive mechanical work. GitHub MCP makes it
agentic.

---

## Part II — Multi-Agent Workflow

### Setup: `git worktree`

Two isolated worktrees were created before starting either task:

```
git worktree add ..\wt-task3 -b feature/task3-notes-crud
git worktree add ..\wt-task4 -b feature/task4-action-filters
```

Each agent received a fully independent working directory and branch, while
sharing the underlying git object store. The SQLite database was also naturally
isolated (`data/app.db` relative to each worktree's `week5/`), so file locks
could not interfere between agents.

### Agent Roles

| Agent | Worktree | Branch | Responsibility |
|-------|----------|--------|---------------|
| Agent 1 | `wt-task3/week5/` | `feature/task3-notes-crud` | `PUT /notes/{id}`, `DELETE /notes/{id}`, Pydantic validation, frontend optimistic UI, 22 new tests |
| Agent 2 | `wt-task4/week5/` | `feature/task4-action-filters` | `GET /action-items?completed=`, `POST /action-items/bulk-complete`, filter UI, bulk select UI, 11 new tests |

Each agent was initialised with a startup prompt specifying:
- The exact worktree path to work in
- The branch name
- A reference to `WARP.md` for project rules
- The specific task requirements from `TASKS.md`

### Coordination Strategy

- Agents worked **fully concurrently** with no synchronisation during implementation.
- Task boundaries were designed to minimise overlap: Task 3 owned
  `notes.py` and `test_notes.py`; Task 4 owned `action_items.py` and
  `test_action_items.py`. Shared files (`schemas.py`, `conftest.py`, `app.js`,
  `styles.css`) were treated as merge-time concerns.
- Integration was deferred to a dedicated merge step on `main` after both
  agents completed independently.

### Concurrency Wins

**Wall-clock time:** Task 3 and Task 4 were implemented simultaneously. The
total elapsed time was comparable to implementing one task, not two.

**Isolated testing:** Each agent ran `make test` independently with no risk of
interfering with the other's database state or uncommitted changes.

**Clean commit history:** Each task produced a self-contained, well-described
commit on its own branch before merging, making the final history legible:

```
ea0381a  merge task3 into main — notes full CRUD, optimistic UI, validation
4ff06dd  Merge feature/task4-action-filters into main
aa16a77  feat(week5): task4 — action-items filters and bulk-complete
ac5b3b8  feat(week5): task3 — notes full CRUD with optimistic UI and validation
```

### Risks and Failures

**Agent self-reporting inaccuracy.** The Task 4 agent reported making changes
"directly in the main repo" rather than in `wt-task4`. Investigation via
`git log` showed the agent had actually committed correctly to
`feature/task4-action-filters`. The self-report was wrong; the actual state was
correct. Lesson: always verify agent-reported state with `git status` / `git log`
rather than trusting the agent's verbal description.

**Merge conflicts on shared files.** Resolving six files required understanding
the intent of both branches simultaneously. This was the most significant cost
of the parallel approach:

| File | Conflict | Resolution |
|------|----------|------------|
| `schemas.py` | Task 3: `StringConstraints`; Task 4: deprecated `class Config` | Task 3's approach everywhere + Task 4's `BulkComplete*` schemas |
| `app.js` | Task 3: full rewrite; Task 4: additions to original | Task 3's rewrite as base, Task 4's action items section integrated |
| `conftest.py` | Both added `engine.dispose()`; Task 4 also added `dependency_overrides.clear()` | Kept both (Task 4 more complete) |
| `styles.css` | Task 3: readable expanded style; Task 4: compact + filter/bulk styles | Task 3 base + Task 4 action items styles |
| `notes.py` | Empty blank line in HEAD vs Task 3 full implementation | Task 3 version |
| `API.md` | Both created the file independently | Merged best of both |

**Lesson:** Frontend files (`app.js`, `styles.css`) and shared infrastructure
(`schemas.py`, `conftest.py`) are high-conflict zones in multi-agent workflows.
The more precisely task boundaries map to file ownership, the less integration
work is needed. A future improvement would be to pre-agree on shared file
conventions before agents start (e.g. "Task 3 owns the Notes section of app.js;
Task 4 owns the Action Items section").

---

## Autonomy Levels

### Task 3 and Task 4 (feature branch development)

**Permissions:** Full file read/write within `week5/`, shell command execution
for tests and lint.

**Why this level:** Each agent operated on an isolated feature branch in its
own worktree. The worst-case outcome of a bad action was a commit on a throwaway
branch — easily reverted with `git reset` or by simply not merging.

**Supervision model:** Agent ran autonomously. Checkpoints were:
1. Code review after implementation (read output, check for obvious issues)
2. Test results inspection (33/33 pass was the acceptance gate)
3. Review of commit content before merging to main

No line-by-line approval was required during generation.

### Integration (merging to main, conflict resolution)

**Permissions:** File read/write on main branch, git merge/add/commit.

**Why higher supervision:** Changes to main are immediately visible to everyone.
Conflict resolution requires understanding the intent of both branches; wrong
choices could silently break the merged product.

**Supervision model:** Every conflict resolution was inspected before staging.
`make test` (33/33) served as the automated acceptance gate before committing.

---

## Summary

| Without automation | With automation |
|---|---|
| Re-explain context every session | `WARP.md` injected automatically |
| Manual test run + manual retry decisions | Test Runner prompt: run → diagnose → retry → report |
| API docs written manually, immediately stale | Docs Sync regenerates `API.md` with delta in seconds |
| Manual git operations after coding | GitHub MCP: agent-driven branch/commit/PR |
| Sequential task implementation (N hours) | Concurrent agents with `git worktree` (~N/2 hours) |

The highest-ROI automation was **WARP.md** — it permanently improved every
subsequent agent interaction by eliminating context drift. The most technically
interesting automation was the **multi-agent + worktree** pattern: it
demonstrated genuine concurrency wins for tasks with independent code surfaces,
and clearly surfaced the integration cost of shared files as the primary risk.
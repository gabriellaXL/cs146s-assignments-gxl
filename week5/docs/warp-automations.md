# Warp Drive Automations — week5

This file archives the Warp Drive saved prompts and MCP server configurations
created for this project. Use it as a reference when setting up Warp Drive,
and as source material for the writeup.

---

## 1. Project Rule: WARP.md

**How it works**: Warp automatically detects `WARP.md` (or `AGENTS.md`) in a
project directory and injects it as context for every agent session within that
project. No manual setup needed — the rule is live as soon as the file exists.

**Location**: `week5/WARP.md` (already created in repo)

**Pain point it solves**: Without a project rule, you'd have to re-explain the
tech stack, directory layout, and coding conventions at the start of every agent
session. With WARP.md, the agent already knows the rules before you say a word.

---

## 2. Saved Prompt: Test Runner with Flaky-Test Re-run

**Name in Warp Drive**: `week5 — Run Tests`

**To create**: In Warp, open Warp Drive → click `+` → Prompt → paste the text below.

**Prompt text**:
```
Run the week5 test suite and report results.

Steps:
1. From the week5/ directory, run:
   PYTHONPATH=. pytest -v backend/tests/ --tb=short 2>&1

2. Show the full output: which tests passed, failed, or were skipped.

3. For any FAILED test, quote:
   - The exact assertion error or exception
   - The file path and line number

4. If a failure looks potentially flaky (no assertion error — e.g. timeout,
   import error, database connection issue, OS-level error), re-run that
   specific test once more with long tracebacks:
   PYTHONPATH=. pytest -v <test_file>::<test_name> --tb=long 2>&1

5. Final summary line:
   "N passed, N failed, N skipped."
   If failures remain: list each by test name + one-line error description.
```

**Why it's valuable**:
- Wraps a repeatable, multi-step QA workflow into a single invocation
- The flaky-test re-run heuristic avoids false alarms from transient errors
- Works for any Python/pytest project — not just week5
- Beats running tests manually, reading raw output, and deciding whether to retry

---

## 3. Saved Prompt: Docs Sync (OpenAPI → API.md)

**Name in Warp Drive**: `week5 — Sync API Docs`

**To create**: In Warp, open Warp Drive → click `+` → Prompt → paste the text below.

**Prompt text**:
```
Generate or update the API reference documentation for the week5 FastAPI backend.

Steps:
1. From the week5/ directory, extract the current OpenAPI spec by running:
   python -c "
   import json, sys
   sys.path.insert(0, '.')
   from backend.app.main import app
   print(json.dumps(app.openapi(), indent=2))
   "

2. Parse all routes from the spec. For each endpoint collect:
   - HTTP method and path
   - Summary and description (if present)
   - Path and query parameters with types
   - Request body schema (if present)
   - Response schema for the 200/201 response

3. Check whether week5/docs/API.md already exists:
   - If YES: compare current routes against what is documented and list
     additions (new routes), removals (deleted routes), and modifications
     (changed params or schemas) as a delta section at the top of the file.
   - If NO: note "Creating fresh API.md".

4. Write a clean Markdown API reference to week5/docs/API.md organized by
   router tag (Notes, Action Items), with one subsection per endpoint showing
   method, path, description, parameters, and example response shape.

5. Report what changed, or confirm "API.md is up to date" if nothing changed.
```

**Why it's valuable**:
- Eliminates manual API doc writing after every endpoint change
- Works without a running server — imports the FastAPI app object directly
- The delta report catches accidental breaking changes between sessions
- Applicable to any FastAPI project with minimal adaptation

---

## 4. MCP Server: GitHub

**Why**: Lets the Warp agent interact with GitHub autonomously — create branches,
commit, open PRs, fetch issue details, summarize changes. Turns "write code" into
a complete "write code → commit → PR" pipeline with no manual git commands.

**Pain point it solves**: Without this, every commit and PR is a separate manual
step. With GitHub MCP, the agent can handle the full git workflow after finishing
a coding task, and you can review the PR rather than type git commands.

### Option A — GitHub Copilot SSE (simplest, no install needed)

Requires: A GitHub account with Copilot access.

```json
{
  "GitHub": {
    "url": "https://api.githubcopilot.com/mcp/"
  }
}
```

### Option B — Docker-based (official GitHub MCP server)

Requires: Docker Desktop installed and running.

```json
{
  "GitHub": {
    "command": "docker",
    "args": [
      "run", "-i", "--rm",
      "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
      "ghcr.io/github/github-mcp-server"
    ],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "<your_github_pat>"
    }
  }
}
```

### How to add to Warp (both options)

1. Open Warp → **Settings** → **MCP Servers** (or Warp Drive → Personal → MCP Servers)
2. Click **+ Add**
3. Paste the JSON block above (choose Option A or B)
4. For Option B: replace `<your_github_pat>` with a GitHub Personal Access Token
   that has `repo` and `pull_requests` scopes
   (create one at: github.com → Settings → Developer settings → Personal access tokens)
5. Click **Start** — the server will appear as running in the list

### Example agent commands once connected
- "Create a branch `feature/task3-notes-crud` and push it"
- "Show the open PRs on this repo"
- "Write a PR description summarizing the changes in the current branch vs main"
- "Create a commit with message 'feat: add PUT /notes/{id} endpoint'"

---

## Setup Checklist

| Item | Status | Notes |
|------|--------|-------|
| `week5/WARP.md` project rule | ✅ Done | Auto-detected by Warp |
| Test Runner prompt | ⬜ Pending | Paste text above into Warp Drive |
| Docs Sync prompt | ⬜ Pending | Paste text above into Warp Drive |
| GitHub MCP server | ⬜ Pending | Add JSON config in Warp Settings |

# Repository Guidance

## Scope
- Default to work in `week4/` unless the user explicitly asks for another week.
- Treat `week4/` as a small production-style app: backend, frontend, tests, docs, and writeup should stay in sync.

## Week4 Navigation
- Backend app: `week4/backend/app`
- Routers: `week4/backend/app/routers`
- Schemas and models: `week4/backend/app/schemas.py`, `week4/backend/app/models.py`
- Frontend: `week4/frontend`
- Tests: `week4/backend/tests`
- Seed data: `week4/data/seed.sql`
- Project tasks: `week4/docs/TASKS.md`
- API reference: `week4/docs/API.md`
- Assignment writeup: `week4/writeup.md`

## Preferred Workflow
1. Read the existing router, tests, and frontend code for the feature area.
2. Extend tests or add missing coverage before finalizing implementation.
3. Implement the smallest backend and frontend change set that satisfies the task.
4. Run `make test` and `make lint` from `week4/`.
5. Update docs and `week4/writeup.md` when behavior changes.

## Automation To Use First
- Use `/feature-notes-crud` when planning or implementing note editing, deletion, and validation changes.
- Use `/verify-week4` before calling the work complete.
- Use the SubAgents under `.claude/agents/` for task planning, implementation, and verification handoffs.

## Agent Workflow
- For multi-step `week4/` work, follow this default sequence:
  1. `PlannerAgent`
  2. `BackendAgent`
  3. `TestDocsAgent`
- Use `PlannerAgent` when the request needs scoping, affected files, or acceptance criteria.
- Use `BackendAgent` only after the task is scoped and ready for implementation.
- Use `TestDocsAgent` after implementation to update tests, verify the result, and sync `week4/docs/API.md` and `week4/writeup.md`.
- The main Claude thread should orchestrate the workflow and hand off between agents explicitly instead of expecting one agent to complete all phases.
- If a task is very small and clearly scoped, it is acceptable to skip `PlannerAgent`, but do not skip final verification and doc sync when behavior changes.

## Safety Rails
- Do not use destructive git commands.
- Do not remove tests to make the suite pass.
- Do not change seed data or API behavior without updating docs.
- Keep commands idempotent and prefer `make test` and `make lint` over ad hoc checks.

## Completion Gate
- New or changed API behavior has backend test coverage.
- Frontend changes are wired to the existing endpoints and handle backend errors.
- `week4/docs/API.md` and `week4/writeup.md` reflect the final behavior.

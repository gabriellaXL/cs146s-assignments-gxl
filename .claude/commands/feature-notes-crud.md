# /feature-notes-crud

Use this command when working on note editing, deletion, or validation features in `week4/`.

## Inputs
- Optional scope in `$ARGUMENTS`, for example: `edit endpoint`, `frontend delete flow`, or `validation`.

## Workflow
1. Inspect the relevant files in `week4/backend/app/routers/notes.py`, `week4/backend/app/schemas.py`, `week4/frontend/app.js`, and `week4/backend/tests/test_notes.py`.
2. Restate the requested scope and list the exact files likely to change.
3. Propose the smallest implementation plan that keeps backend, frontend, tests, docs, and writeup aligned.
4. Implement the changes.
5. Run the week4 verification gate:
   - `make test`
   - `make lint`
6. Summarize:
   - changed files
   - new or updated endpoints
   - tests added or updated
   - follow-up doc or writeup items

## Expected Output
- A scoped implementation plan
- Code changes for the requested notes feature
- A concise verification summary with next steps if something fails

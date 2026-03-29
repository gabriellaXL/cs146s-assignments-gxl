# Week 7 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## Task 1: Add more endpoints and validations
a. Links to relevant commits/issues
> Pending. Add the Task 1 branch, commit(s), and PR link after opening the PR.

b. PR Description
> This PR expands the Week 7 starter API with stronger validation, clearer error handling, and a more complete resource surface for notes and action items.
>
> Problem:
> The starter app already had basic list/create/update behavior, but its API surface was still incomplete for a robust CRUD workflow. It was also missing strong request validation, relied on repeated router-level lookup/sort logic, and still used some outdated framework patterns. The test fixture was also flaky on Windows because the temporary SQLite file was not always released before cleanup.
>
> Approach:
> I tightened the API contract and used that as the foundation for the rest of the task:
> - Added stricter Pydantic v2 validation for create/update payloads, including whitespace stripping and explicit length bounds.
> - Restricted `sort` to an explicit allowlist instead of silently accepting invalid fields.
> - Added missing endpoints for `GET /action-items/{id}`, `DELETE /notes/{id}`, and `DELETE /action-items/{id}`.
> - Added `POST /notes/{id}/extract-action-items` so extraction logic can be exercised through an API endpoint rather than only through an internal helper.
> - Extracted shared `get_or_404` and `apply_sort` helpers to reduce duplication across routers.
> - Modernized the FastAPI app startup path from deprecated `on_event` usage to lifespan.
> - Updated timestamp defaults to timezone-aware UTC values.
> - Fixed the test fixture to use `TemporaryDirectory` and dispose the SQLAlchemy engine cleanly on teardown.
>
> Testing:
> - Ran `PYTHONPATH=. poetry run pytest -q backend/tests`
> - Result: `5 passed`
> - Expanded tests to cover:
>   - successful create/get/list/patch/delete flows
>   - extraction endpoint behavior
>   - validation failures for blank or invalid payloads
>   - invalid pagination and sort parameters
>   - `404` behavior for missing resources
>
> Notable tradeoffs / follow-ups:
> - I used allowlisted sort fields to keep behavior predictable and testable. This is stricter than silently falling back to a default sort, but it produces a better API contract.
> - The extraction endpoint currently returns extracted strings without persisting them. That keeps Task 1 focused on API shape and validation; richer extraction behavior can evolve in Task 2.

c. Graphite Diamond generated code review
> Pending. Add screenshots or quoted review comments from Graphite Diamond after the PR is opened and reviewed.

## Task 2: Extend extraction logic
a. Links to relevant commits/issues
> Pending. Add the Task 2 branch, commit(s), and PR link after opening the PR.

b. PR Description
> This PR upgrades the note-to-action-item extraction flow from a demo heuristic into a rule-based, structured analysis pipeline.
>
> Problem:
> The original extraction logic only recognized a few exact patterns (`TODO:`, `ACTION:`, and lines ending with `!`). It did not distinguish why something was extracted, could not surface metadata such as source line or due-date hints, and was too brittle to support realistic note-taking patterns.
>
> Approach:
> I replaced the ad hoc extractor with a structured rule engine that keeps the implementation deterministic and easy to test:
> - Added a dedicated `analyze_action_items()` pipeline that returns structured extraction results rather than only raw strings.
> - Preserved a simple `extract_action_items()` wrapper for callers that only need normalized text.
> - Expanded supported patterns to include:
>   - tagged action lines such as `TODO:`, `ACTION:`, `FOLLOW-UP:`, and `NEXT STEP:`
>   - unchecked checklist items like `[ ] prepare demo`
>   - request/commitment phrasing such as `Please send the recap by Friday`
>   - imperative task statements such as `Review the API contract`
> - Added normalization and deduplication so repeated action lines do not produce duplicate extracted items.
> - Added lightweight analysis metadata for each item:
>   - `source_line`
>   - `trigger`
>   - `confidence`
>   - optional `due_hint`
>   - optional `assignee_hint`
> - Updated the extraction API to return structured extraction records instead of opaque strings.
>
> Testing:
> - Ran `PYTHONPATH=. poetry run pytest -q backend/tests`
> - Result: `7 passed`
> - Added tests for:
>   - multiple extraction patterns in one note
>   - metadata generation for triggers, due dates, and assignees
>   - deduplication of repeated tasks
>   - rejection of completed or non-actionable lines
>   - note extraction API behavior with structured responses
>
> Notable tradeoffs / follow-ups:
> - The extractor remains intentionally rule-based instead of using an LLM so behavior stays predictable, cheap, and easy to regression-test.
> - The current analysis only emits lightweight hints rather than full task parsing. If needed later, this can be extended with richer fields such as priority or owner normalization without changing the core extraction architecture.

c. Graphite Diamond generated code review
> Pending. Add screenshots or quoted review comments from Graphite Diamond after the PR is opened and reviewed.

## Task 3: Try adding a new model and relationships
a. Links to relevant commits/issues
> Pending. Add the Task 3 branch, commit(s), and PR link after opening the PR.

b. PR Description
> This PR introduces a new `Project` model and connects it to `ActionItem` through a one-to-many relationship.
>
> Problem:
> Before this change, action items were all standalone records. The app had no way to group related work, inspect tasks by project, or exercise model relationships in either the API or the UI. The existing SQLite setup also had no migration path for adding a new foreign key column to older local databases.
>
> Approach:
> I added a `Project -> ActionItem` relationship and updated the application across the stack:
> - Added a new `Project` model with `name`, `description`, timestamps, and a relationship back to `ActionItem`.
> - Added `project_id` and `project` support to action item schemas and endpoints.
> - Added a new `/projects` router with:
>   - list
>   - create
>   - get detail with nested action items
>   - patch
>   - delete
> - Added action-item support for:
>   - assigning a project when creating an action item
>   - reassigning or clearing the project in PATCH
>   - filtering action items by `project_id`
>   - returning project metadata alongside action item responses
> - Added a lightweight schema update path for SQLite so older databases can receive the new `project_id` column and index without a full migration framework.
> - Updated seed data and the static frontend so projects can be created and assigned through the app UI.
>
> Testing:
> - Ran `PYTHONPATH=. poetry run pytest -q backend/tests`
> - Result: `9 passed`
> - Added and updated tests to cover:
>   - project CRUD behavior
>   - nested relationship reads
>   - assigning and unassigning action items to projects
>   - project uniqueness validation
>   - action item filtering by `project_id`
>   - deleting a project and clearing the child action items' assignment
>
> Notable tradeoffs / follow-ups:
> - I chose a single `Project -> ActionItem` relationship rather than a more complex many-to-many design to keep the model easy to reason about and easy to test.
> - The current database evolution path is intentionally lightweight. It is appropriate for this assignment-sized app, but a production system would want real migrations through Alembic or an equivalent tool.

c. Graphite Diamond generated code review
> Pending. Add screenshots or quoted review comments from Graphite Diamond after the PR is opened and reviewed.

## Task 4: Improve tests for pagination and sorting
a. Links to relevant commits/issues
> Pending. Add the Task 4 branch, commit(s), and PR link after opening the PR.

b. PR Description
> This PR strengthens test coverage for pagination and sorting behavior across the application.
>
> Problem:
> The earlier tests verified that list endpoints returned successful responses, but they did not strongly validate ordering, page boundaries, or the interaction between filters and pagination. That left several important regressions uncaught, such as incorrect sort order, offset mistakes, empty-page handling, or filtering being applied in the wrong sequence.
>
> Approach:
> I added a dedicated pagination/sorting regression suite that uses deterministic test data and asserts concrete list behavior instead of only status codes:
> - Added focused list-behavior tests for:
>   - `/notes/`
>   - `/action-items/`
>   - `/projects/`
> - Used stable string-based sort fields (`title`, `description`, `name`) instead of relying on timestamp ordering that can be brittle in fast test runs.
> - Verified:
>   - ascending and descending sort order
>   - `skip`/`limit` pagination slices
>   - search/filter combinations with sorting
>   - empty-page behavior when offsets exceed available rows
>   - action item filtering by both `completed` and `project_id`
>   - project list summaries still reporting correct `action_item_count` values under sorted/paginated reads
>
> Testing:
> - Ran `PYTHONPATH=. poetry run pytest -q backend/tests`
> - Result: `12 passed`
> - Also ran `poetry run ruff check backend`
>
> Notable tradeoffs / follow-ups:
> - These tests focus on API behavior rather than query implementation details, which keeps them resilient to internal refactors.
> - I intentionally avoided overfitting tests to timestamp precision. If the app later needs stronger guarantees around chronological ordering, that should be tested with explicit timestamp control rather than assuming database insertion timing.

c. Graphite Diamond generated code review
> Pending. Add screenshots or quoted review comments from Graphite Diamond after the PR is opened and reviewed.

## Brief Reflection 
a. The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
> TODO 

b. A comparison of **your** comments vs. **Graphite’s** AI-generated comments for each PR.
> TODO

c. When the AI reviews were better/worse than yours (cite specific examples)
> TODO

d. Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.
>TODO 

# Week 4 Write-up

Tip: To preview this markdown file

- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **GXL**  
SUNet ID:  
Citations: **Anthropic, "Claude Code best practices"; Anthropic Docs, "SubAgents overview"**

This assignment took me about **4** hours to do.

## YOUR RESPONSES

### Automation #1

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)

> I used the Claude Code best-practices guidance to keep repository instructions concise, actionable, and centered on repeated work. The main idea I borrowed was that automation should reduce developer friction on every change, not just help on one task once.

b. Design of each automation, including goals, inputs/outputs, steps

> Automation #1 is a repository-level `CLAUDE.md` file. Its goal is to make Claude immediately effective in `week4/` by documenting the project map, the preferred implementation workflow, the verification gate, and the automations to use first. The input is any user request that touches `week4/`, and the output is more consistent planning and execution because Claude starts with the same repo-specific operating instructions every time.

c. How to run it (exact commands), expected outputs, and rollback/safety notes

> `CLAUDE.md` is read automatically by Claude Code at conversation start, so there is no separate shell command to invoke it. The expected output is better-scoped work: inspect the relevant files first, make the smallest coherent change, run `make test` and `make lint`, then sync docs and writeup. It is safe to roll back because it only changes guidance, not runtime code.

d. Before vs. after (i.e. manual workflow vs. automated workflow)

> Before `CLAUDE.md`, each session had to rediscover where the routers, tests, docs, and validation gates lived. After adding it, the default workflow became explicit and repeatable. That reduced prompt overhead and made it much less likely that testing or documentation would be skipped.

e. How you used the automation to enhance the starter application

> I used `CLAUDE.md` as the project runbook while implementing note update/delete support and request validation. It kept the work focused on the right backend, frontend, test, and doc files and enforced the final verification step before I treated the feature as done. As a result, the starter app moved from basic note creation/listing to a more production-like version with note editing, note deletion, validation constraints, clearer 400/404 responses, and synchronized docs.

### Automation #2

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)

> I designed the slash commands around the best-practices idea that high-value automations should target repeated workflows. Instead of making generic prompts, I created one command for feature delivery and one command for final verification because those are the two loops I expect to reuse most on a small app like this.

b. Design of each automation, including goals, inputs/outputs, steps

> Automation #2 is a pair of custom slash commands in `.claude/commands/`.
>
> The first command, `/feature-notes-crud`, standardizes note-related feature work. Its goal is to guide Claude through inspecting the relevant router, schema, frontend, and test files; scoping the change; implementing the smallest coherent diff; and then running the week4 checks.
>
> The second command, `/verify-week4`, standardizes release-style verification. Its goal is to check tests, lint, API docs, and writeup completeness before considering the task complete.
>
> Together, the inputs are an optional scoped argument such as `validation` or `notes crud`, and the outputs are a structured implementation summary or a pass/blocked verification report.

c. How to run it (exact commands), expected outputs, and rollback/safety notes

> Example invocations:
>
> - `/feature-notes-crud validation`
> - `/feature-notes-crud frontend delete flow`
> - `/verify-week4 notes crud`
>
> The expected output is not just code, but a repeatable workflow summary: affected files, required checks, and any remaining gaps. These commands are safe because they only define scoped workflows in Markdown. Rolling them back means deleting the files from `.claude/commands/`.

d. Before vs. after (i.e. manual workflow vs. automated workflow)

> Before the slash commands, feature implementation and final verification depended on remembering the right file set and quality gate manually. Afterward, there was a reusable entry point for note-related development and a reusable exit gate for delivery. That made the process faster and more repeatable.

e. How you used the automation to enhance the starter application

> I used the feature command as the template for implementing the note update/delete flow, including the backend routes, frontend edit/delete UI, and test updates. I then used the verification command's checklist to make sure the tests, lint status, API reference, and writeup all matched the final implementation. In practice, these commands helped turn a vague goal like "upgrade notes" into a repeatable workflow that produced concrete app improvements instead of one-off edits.

### *(Optional) Automation #3*

*If you choose to build additional automations, feel free to detail them here!*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)

> I used the SubAgents overview as the main design reference. The useful lesson was that agent specialization matters most when each role has a clear boundary and a clear handoff, not when the workflow is split into as many agents as possible.

b. Design of each automation, including goals, inputs/outputs, steps

> Automation #3 is a three-agent workflow documented in `.claude/agents/`.
>
> `PlannerAgent` turns a requested change into a concrete plan, file impact list, and acceptance criteria.
>
> `BackendAgent` takes that scoped plan and implements the backend/frontend code changes with the smallest coherent diff.
>
> `TestDocsAgent` adds or updates tests, runs the week4 verification commands, and syncs `week4/docs/API.md` and `week4/writeup.md` with the final behavior.
>
> The flow is intentionally linear: plan first, implement second, verify and document third.

c. How to run it (exact commands), expected outputs, and rollback/safety notes

> These agents are invoked from Claude Code by selecting the appropriate role for the current phase of work. The expected output is a cleaner workflow with less context drift: one role plans, one role builds, and one role verifies. This is safe because the agent files only contain role-specific guidance and can be edited or removed without affecting the app itself.

d. Before vs. after (i.e. manual workflow vs. automated workflow)

> Before introducing the three roles, planning, coding, and verification were mixed together, which made it easier to miss acceptance criteria or forget documentation updates. After adding the SubAgents, each phase had a clear owner and handoff, which improved focus and reduced skipped work.

e. How you used the automation to enhance the starter application

> I used the three-agent workflow to implement the `notes` enhancements. The planner scoped the task as note update/delete plus validation and error handling. The implementation role then added the new endpoints, frontend edit/delete interactions, and clearer feedback messages. The testing/documentation role added validation coverage, updated `week4/docs/API.md`, and recorded how the automations were used in this writeup.
>
> This improved both the app and the workflow. On the app side, users can now update and delete notes from the UI, invalid requests return clearer errors, and action item creation is validated as well. On the workflow side, the planning, implementation, and verification stages were separated cleanly enough that I could make the feature larger without losing track of tests or docs.

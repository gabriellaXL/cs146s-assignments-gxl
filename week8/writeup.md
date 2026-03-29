# Week 8 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **[Fill in your name]** \
SUNet ID: **[Fill in your SUNet ID]** \
Citations: **Bolt support docs (project export / database setup), Supabase docs, Django docs, FastAPI docs, plus local lint/typecheck/test/audit outputs used during implementation review**

This assignment took me about **[Fill in your actual hours]** hours to do. 


## App Concept 
```
Developer Control Center is a lightweight note-management web app centered around one primary resource: notes. In every version of the app, users can create notes, browse a list of notes, open a single note in detail, update existing notes, and delete notes with a confirmation step. Each note stores a title, content body, status, and timestamps.

The app is intentionally scoped around full CRUD, persistence, validation, and a simple but usable UI rather than advanced multi-user features. This keeps the product definition stable across all three implementations while still making it large enough to compare different stacks, AI generation workflows, and debugging/review practices.
```


## Version #1 Description
```
APP DETAILS:
===============
Folder name: version1-fastapi
AI app generation platform: None
Tech Stack: FastAPI + SQLAlchemy + SQLite + static HTML/CSS/JavaScript frontend
Persistence: Local SQLite database stored in the project data directory
Frameworks/Libraries Used: FastAPI, SQLAlchemy, Pydantic, Uvicorn, pytest
(Optional but recommended) Screenshots of core flows: Add screenshots here if you want visual evidence of the list/detail/create/edit/delete flows

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
I did not want to reuse week7 blindly because week8 needed a cleaner one-resource implementation that aligned with the shared app spec used by the Django and Bolt versions. I therefore reused only the proven FastAPI patterns from week7, then rebuilt this version around a single `Note` resource with the same fields used elsewhere: title, content, status, created_at, and updated_at. The main issues were making the app self-contained, keeping path handling stable regardless of working directory, and keeping the frontend simple without losing core CRUD flows. I resolved those by creating a dedicated week8 project folder, using absolute project-relative paths in the FastAPI app, and adding a lightweight static UI with create/view/edit/delete flows instead of trying to build a separate JS frontend stack.

I also did a normal engineering review pass rather than treating this as just a code copy. I ran backend tests, used `ruff` for static analysis, verified that the application imported and started cleanly, and checked that the API behavior matched the Django/Bolt product definition. This version ended in a cleaner state than the original week7 foundation because it was deliberately narrowed to one primary resource and revalidated from scratch.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
This version was primarily built through direct code implementation rather than AI app generation, so prompting was not the primary workflow. The main “guidance” challenge was internal: keeping the implementation disciplined enough that it stayed aligned with the other two versions instead of drifting back toward the broader week7 app.

c. Approximate time-to-first-run and time-to-feature metrics:
Time-to-first-run was relatively short because the FastAPI stack and tooling were already familiar. Time-to-feature completion was longer than the first runnable API because I still needed to add the static frontend, align the data model with the other versions, and re-run testing/static checks to make sure the project was submission-ready rather than just minimally functional.
```

## Version #2 Description
```
APP DETAILS:
===============
Folder name: version2-bolt
AI app generation platform: bolt.new
Tech Stack: React 18 + TypeScript + Vite + Tailwind CSS + Supabase PostgreSQL
Persistence: Supabase-hosted PostgreSQL database with SQL migrations
Frameworks/Libraries Used: React, Vite, TypeScript, Tailwind CSS, @supabase/supabase-js, Lucide React, ESLint
(Optional but recommended) Screenshots of core flows: Add screenshots here if you want visual evidence of the list/detail/create/edit/delete flows

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
The generated project was a strong CRUD starting point, but it was not ready to submit as-is. After export, I found several quality gaps: the README relied on a private local `.env`, the generated TypeScript database types were not strict enough for `npm run typecheck`, the service layer passed lint/build only partially, and the original SQL migration enforced `status` but not the title/content length rules stated in the app spec. I manually reviewed the routing, CRUD flow, environment handling, and migration files, then fixed the issues by tightening the Supabase types, splitting route parsing into a separate helper, adding a second SQL migration for database-level validation and automatic `updated_at` maintenance, rewriting the README around `.env.example`, and rerunning lint/typecheck/build until all three passed.

I also ran dependency scanning with `npm audit`. The initial audit surfaced 15 vulnerabilities in the generated dependency tree. Running `npm audit fix` reduced this to 6 remaining low/moderate issues, mostly in dev tooling such as Vite/esbuild/eslint. I kept the project on the current non-breaking versions rather than forcing a major-version upgrade immediately.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
Bolt responded well when the prompt clearly constrained the product to one primary resource, real persistence, full CRUD, and no extra auth or collaboration features. It generated the core pages, routing, and Supabase integration quickly. What worked less well was the last mile of engineering quality: local reproducibility, defensive database constraints, exact TypeScript correctness, and submission-ready documentation still required manual follow-up. In practice, Bolt was most effective as a first-pass full-stack generator, not as a one-shot final submission tool.

c. Approximate time-to-first-run and time-to-feature metrics:
Approximate time-to-first-generated app in Bolt was on the order of minutes. Approximate time-to-local-run after export was one setup/debug cycle once dependencies and Supabase configuration were in place. Approximate time-to-submission-quality was meaningfully longer because it included manual code review, lint/typecheck/build cleanup, SQL migration hardening, README cleanup, and dependency auditing.
```

## Version #3 Description
```
APP DETAILS:
===============
Folder name: version3-django
AI app generation platform: None
Tech Stack: Django + SQLite + Django templates
Persistence: Local SQLite database stored in the Django project directory
Frameworks/Libraries Used: Django, SQLite, Django ORM, Django forms, Django templates
(Optional but recommended) Screenshots of core flows: Add screenshots here if you want visual evidence of the list/detail/create/edit/delete flows

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them:
The main challenge in the Django version was keeping the app intentionally scoped and aligned with the other two versions. Django makes it easy to keep adding features, but for week8 I wanted this version to stay centered on the same `Note` CRUD experience as the FastAPI and Bolt implementations. I therefore built the project around one model and a clean set of list/detail/create/edit/delete pages rather than adding unrelated resources.

Another challenge was making the project stable enough to act as the most traditional implementation in the comparison. I resolved that by using Django's built-in strengths rather than fighting the framework: model definitions for persistence, forms for validation, class-based views for CRUD structure, templates for the UI, and automated Django tests for the main flows. After implementation, I verified this version with `manage.py check` and `manage.py test`, which helped confirm that the project was not just feature-complete but also internally consistent.

b. Prompting (e.g. what required additional guidance; what worked poorly/well):
This version was primarily hand-built rather than AI-generated, so prompting was not a major part of the workflow. The most important “guidance” choice was architectural rather than prompt-based: deciding to use Django templates instead of pairing Django with React. That kept the stack clearly non-JavaScript on the application side, reduced moving parts, and made it easier to produce a stable CRUD app with good validation and predictable page flows.

c. Approximate time-to-first-run and time-to-feature metrics:
Time-to-first-run was relatively fast once the Django project skeleton existed, since SQLite and Django's built-in tooling make local setup straightforward. Time-to-feature completion was longer because I still needed to build the full sequence of list/detail/create/edit/delete pages, design the note form and validation behavior, and run test/check passes so this version could serve as a stable comparison point against the Bolt and FastAPI versions.
```

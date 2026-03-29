# Developer Control Center

This is the Bolt-generated Week 8 implementation of the shared notes application. It uses a React frontend with Supabase-backed persistence and was manually refined after generation to improve validation, typing, and submission-readiness.

## Tech Stack

- Frontend: React 18 + TypeScript
- Build tool: Vite
- Styling: Tailwind CSS
- Persistence: Supabase PostgreSQL
- Database client: `@supabase/supabase-js`

## Core Features

- Create notes with `title`, `content`, and `status`
- View all notes in a list with empty-state handling
- View a single note in detail
- Edit existing notes
- Delete notes with a confirmation dialog
- Validate title and content lengths before writes
- Persist data in a real hosted PostgreSQL database

## Data Model

Each note contains:

- `id` - UUID primary key
- `title` - required, minimum 3 characters
- `content` - required, minimum 10 characters
- `status` - `active`, `blocked`, or `archived`
- `created_at` - creation timestamp
- `updated_at` - last update timestamp

## Validation

Validation happens in two places:

- Client-side service validation before create/update requests
- Database-level constraints in Supabase migrations for status and minimum trimmed lengths

## Prerequisites

- Node.js 18+ and npm
- A Supabase account and project

## Local Setup

1. Move into the project directory:

```bash
cd week8/version2-bolt
```

2. Install dependencies:

```bash
npm install
```

3. Copy the environment template:

```bash
cp .env.example .env
```

4. Fill in your Supabase values in `.env`:

```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

5. Create a Supabase project and apply the SQL files in `supabase/migrations/` in order.

You can do this either:

- in the Supabase SQL editor by pasting the migration files one by one
- or with the Supabase CLI if you already use it

6. Start the development server:

```bash
npm run dev
```

7. Open `http://localhost:5173`

## Build and Checks

```bash
npm run build
npm run lint
npm run typecheck
```

## Project Structure

```text
src/
  components/
    ui/                    shared UI primitives
  pages/                   notes list, detail, create, and edit views
  services/notes.ts        CRUD operations and client-side validation
  lib/supabase.ts          Supabase client setup
  lib/database.types.ts    typed database schema
  lib/router.tsx           hash-based router provider
  lib/route-utils.ts       route parsing helper
  App.tsx                  app shell and route selection
  main.tsx                 application entry point

supabase/migrations/
  20260329110307_create_notes_table.sql
  20260329195000_harden_notes_constraints.sql
```

## Key Files

- `src/App.tsx` - high-level route selection
- `src/pages/NotesList.tsx` - notes list and empty state
- `src/pages/NoteDetail.tsx` - detail view and delete flow
- `src/pages/NoteForm.tsx` - create/edit form
- `src/services/notes.ts` - CRUD service logic and validation
- `src/lib/supabase.ts` - Supabase client initialization
- `supabase/migrations/` - schema, policies, constraints, and timestamp trigger

## Manual Fixes After Generation

- Tightened Supabase TypeScript schema definitions so `npm run typecheck` can pass
- Split route parsing into a standalone helper to keep React fast-refresh lint output clean
- Added a second SQL migration for database-level validation and automatic `updated_at` maintenance
- Reworked setup instructions around `.env.example` instead of relying on a private local `.env`

## Security Notes

- RLS is enabled, but this class project intentionally allows public CRUD with the anon role for simplicity
- Do not reuse these public policies in a real production application
- Do not commit real Supabase credentials; use `.env.example` as the shared template

## Known Limitations

- No authentication
- Notes are effectively public within the configured Supabase project
- Basic hash-based routing rather than browser-history routing
- No pagination or filtering
- Persistence depends on a configured Supabase project rather than a purely local database

## Development Review Workflow

This version was not accepted as-generated. It was reviewed and refined with:

- manual code review of routing, CRUD flows, and environment handling
- `npm run lint`
- `npm run typecheck`
- `npm run build`
- `npm audit` to scan dependency vulnerabilities

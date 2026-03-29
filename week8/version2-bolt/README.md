# Developer Control Center

A full-stack note management application built with React, TypeScript, Vite, and Supabase.

## Features

- **Create Notes**: Add new notes with title, content, and status
- **View Notes**: Browse all notes in a list or view individual note details
- **Edit Notes**: Update existing notes
- **Delete Notes**: Remove notes with confirmation
- **Validation**: Client-side and server-side validation for data integrity
- **Persistent Storage**: Real database-backed storage using Supabase PostgreSQL

## Tech Stack

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Icons**: Lucide React

## Data Model

Each note contains:
- `id` - Unique identifier (UUID)
- `title` - Note title (required, min 3 characters)
- `content` - Note content (required, min 10 characters)
- `status` - Note status: active, blocked, or archived
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## Validation Rules

- **Title**: Required, minimum 3 characters
- **Content**: Required, minimum 10 characters
- **Status**: Must be one of: active, blocked, archived

## Prerequisites

- Node.js 18+ and npm
- A Supabase account and project

## Setup Instructions

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd developer-control-center
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Environment Variables

The project includes a `.env` file with Supabase credentials. Ensure it contains:

```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 4. Database Setup

The database migration has already been applied. The `notes` table includes:
- Row Level Security (RLS) enabled
- Public access policies for local development
- Check constraints for status values
- Indexes for optimal performance

### 5. Run the Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### 6. Build for Production

```bash
npm run build
```

The production build will be in the `dist` directory.

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Base UI components (Button, Input, Modal, etc.)
│   ├── Layout.tsx      # Main layout with header and navigation
│   └── DeleteConfirmation.tsx  # Delete confirmation modal
├── pages/              # Page components
│   ├── NotesList.tsx   # Notes list page
│   ├── NoteDetail.tsx  # Note detail page
│   └── NoteForm.tsx    # Create/edit note form
├── services/           # Business logic and API calls
│   └── notes.ts        # Notes CRUD operations and validation
├── lib/                # Core utilities
│   ├── supabase.ts     # Supabase client configuration
│   ├── database.types.ts  # TypeScript types for database
│   └── router.tsx      # Simple hash-based routing
├── App.tsx             # Main app component with routing
└── main.tsx            # Application entry point

supabase/
└── migrations/         # Database migrations
    └── create_notes_table.sql
```

## Key Files

### Frontend
- `src/App.tsx` - Main application component with routing logic
- `src/pages/NotesList.tsx` - Notes list view with empty state
- `src/pages/NoteDetail.tsx` - Individual note view
- `src/pages/NoteForm.tsx` - Create and edit form

### Backend/Database
- `src/services/notes.ts` - All database operations (CRUD)
- `src/lib/supabase.ts` - Supabase client singleton
- `supabase/migrations/create_notes_table.sql` - Database schema

### Database Logic
- All persistence is handled through Supabase PostgreSQL
- Service layer validates data before database operations
- Row Level Security policies allow public access for local development

## Usage

1. **Create a Note**: Click "New Note" button, fill in the form, and click "Create Note"
2. **View Notes**: The home page lists all notes
3. **View Details**: Click on any note to view full details
4. **Edit a Note**: Click "Edit" on the detail page
5. **Delete a Note**: Click "Delete" on the detail page and confirm

## Known Limitations

- **No Authentication**: The app does not include user authentication. All notes are public.
- **Single User**: Designed for single-user local development
- **No Real-time Updates**: Changes don't sync automatically across tabs
- **Basic Routing**: Uses hash-based routing instead of browser history API
- **No Pagination**: All notes load at once (fine for small datasets)

## Security Notes

- RLS is enabled with public access policies for local development
- In production, you should implement proper authentication and restrict RLS policies
- Never commit real credentials to version control

## Development

### Type Checking

```bash
npm run typecheck
```

### Linting

```bash
npm run lint
```

## Future Enhancements

Potential features that could be added:
- User authentication and authorization
- Note filtering and search
- Tags or categories
- Rich text editor
- Export functionality
- Dark mode

## License

MIT

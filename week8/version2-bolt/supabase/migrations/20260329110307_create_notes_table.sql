/*
  # Create notes table for Developer Control Center

  1. New Tables
    - `notes`
      - `id` (uuid, primary key) - Unique identifier for each note
      - `title` (text, required) - Note title with minimum 3 characters
      - `content` (text, required) - Note content with minimum 10 characters
      - `status` (text, required) - Note status: active, blocked, or archived
      - `created_at` (timestamptz) - Timestamp when note was created
      - `updated_at` (timestamptz) - Timestamp when note was last updated

  2. Security
    - Enable RLS on `notes` table
    - Add policies for public access to all operations (no authentication required)
    - This is intentional for local development usage

  3. Constraints
    - Status field limited to: active, blocked, archived
    - Default status is 'active'
*/

CREATE TABLE IF NOT EXISTS notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  content text NOT NULL,
  status text NOT NULL DEFAULT 'active',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  CONSTRAINT valid_status CHECK (status IN ('active', 'blocked', 'archived'))
);

ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to notes"
  ON notes
  FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Allow public insert access to notes"
  ON notes
  FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "Allow public update access to notes"
  ON notes
  FOR UPDATE
  TO anon
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete access to notes"
  ON notes
  FOR DELETE
  TO anon
  USING (true);

CREATE INDEX IF NOT EXISTS notes_created_at_idx ON notes(created_at DESC);
CREATE INDEX IF NOT EXISTS notes_status_idx ON notes(status);
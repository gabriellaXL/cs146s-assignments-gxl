/*
  # Harden notes validation and timestamps

  1. Validation
    - Enforce minimum title length after trimming whitespace
    - Enforce minimum content length after trimming whitespace

  2. Server-side timestamps
    - Keep `updated_at` maintained by the database on every update
*/

ALTER TABLE notes
  ADD CONSTRAINT notes_title_min_length
    CHECK (char_length(btrim(title)) >= 3),
  ADD CONSTRAINT notes_content_min_length
    CHECK (char_length(btrim(content)) >= 10);

CREATE OR REPLACE FUNCTION set_notes_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS notes_set_updated_at ON notes;

CREATE TRIGGER notes_set_updated_at
BEFORE UPDATE ON notes
FOR EACH ROW
EXECUTE FUNCTION set_notes_updated_at();

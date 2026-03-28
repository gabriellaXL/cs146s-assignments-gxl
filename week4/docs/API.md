# Week 4 API Reference

## Notes

### `GET /notes/`
- Returns all notes.

### `POST /notes/`
- Creates a note.
- Request body:
  - `title`: string, minimum 3 characters
  - `content`: string, minimum 5 characters

### `GET /notes/search/?q=...`
- Returns matching notes (case-insensitive match against `title` and `content`).
- When `q` is omitted, returns all notes.

### `GET /notes/{note_id}`
- Returns a single note.
- Returns `404` when the note does not exist.

### `PUT /notes/{note_id}`
- Partially updates a note. Both `title` and `content` are optional; omitted fields retain their current values.
- Validation rules for provided fields are the same as `POST /notes/` (e.g. `title` min 3 chars, `content` min 5 chars); invalid values return `400`.
- Returns `404` when the note does not exist.

### `DELETE /notes/{note_id}`
- Deletes a note.
- Returns status `204` on success.
- Returns `404` when the note does not exist.

## Action Items

### `GET /action-items/`
- Returns all action items.

### `POST /action-items/`
- Creates an action item.
- Request body:
  - `description`: string, minimum 3 characters

### `PUT /action-items/{item_id}/complete`
- Marks an action item complete.
- Returns `404` when the action item does not exist.

## Validation Errors
- Invalid request payloads return `400`.
- Error responses include a `detail` field with validation messages.

# API Reference — week5

> Auto-generated from `/openapi.json` after Task 3 (Notes full CRUD).
> Re-run the *Docs Sync* saved prompt after any API changes to keep this up to date.

---

## Notes

Base path: `/notes`

### `GET /notes/`
List all notes.

**Response 200** — `NoteRead[]`
```json
[{ "id": 1, "title": "...", "content": "..." }]
```

---

### `POST /notes/`
Create a new note.

**Request body** — `NoteCreate`
| Field | Type | Constraints |
|-------|------|-------------|
| `title` | string | required, 1–200 chars, whitespace stripped |
| `content` | string | required, min 1 char, whitespace stripped |

**Response 201** — `NoteRead`
**Response 422** — validation error

---

### `GET /notes/search/`
Search notes by title or content (case-insensitive substring match).

**Query params**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `q` | string | `null` | Search term. If omitted, returns all notes. |

**Response 200** — `NoteRead[]`

---

### `GET /notes/{note_id}`
Get a single note by ID.

**Path params**: `note_id` (integer, required)

**Response 200** — `NoteRead`
**Response 404** — note not found

---

### `PUT /notes/{note_id}`
Full replacement update (PUT semantics). All fields are required.

**Path params**: `note_id` (integer, required)

**Request body** — `NoteUpdate`
| Field | Type | Constraints |
|-------|------|-------------|
| `title` | string | required, 1–200 chars, whitespace stripped |
| `content` | string | required, min 1 char, whitespace stripped |

**Response 200** — `NoteRead` (updated)
**Response 404** — note not found
**Response 422** — validation error

---

### `DELETE /notes/{note_id}`
Delete a note. Idempotency note: a second call on the same ID returns 404.

**Path params**: `note_id` (integer, required)

**Response 204** — No Content (empty body)
**Response 404** — note not found

---

## Action Items

Base path: `/action-items`

### `GET /action-items/`
List all action items.

**Response 200** — `ActionItemRead[]`
```json
[{ "id": 1, "description": "...", "completed": false }]
```

---

### `POST /action-items/`
Create a new action item.

**Request body** — `ActionItemCreate`
| Field | Type | Constraints |
|-------|------|-------------|
| `description` | string | required, min 1 char, whitespace stripped |

**Response 201** — `ActionItemRead`
**Response 422** — validation error

---

### `PUT /action-items/{item_id}/complete`
Mark an action item as completed. Idempotent (calling twice is safe).

**Path params**: `item_id` (integer, required)

**Response 200** — `ActionItemRead` (with `completed: true`)
**Response 404** — item not found

---

## Schemas

### `NoteRead`
```json
{ "id": 1, "title": "string", "content": "string" }
```

### `NoteCreate` / `NoteUpdate`
```json
{ "title": "string (1–200 chars)", "content": "string (min 1 char)" }
```

### `ActionItemRead`
```json
{ "id": 1, "description": "string", "completed": false }
```

### `ActionItemCreate`
```json
{ "description": "string (min 1 char)" }
```

### Validation error (422)
```json
{
  "detail": [
    { "loc": ["body", "title"], "msg": "String should have at least 1 character", "type": "string_too_short" }
  ]
}
```

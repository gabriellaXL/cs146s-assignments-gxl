# API Reference — week5

> Generated from `/openapi.json`. Re-run the *Docs Sync* saved prompt after any API changes.
> Interactive docs: `http://localhost:8000/docs`

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
Delete a note. A second call on the same ID returns 404.

**Path params**: `note_id` (integer, required)

**Response 204** — No Content (empty body)
**Response 404** — note not found

---

## Action Items

Base path: `/action-items`

### `GET /action-items/`
List action items, optionally filtered by completion status.

**Query params**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `completed` | bool | omit | `true` → done only; `false` → open only; omit → all |

**Response 200** — `ActionItemRead[]`
```json
[{ "id": 1, "description": "Ship it", "completed": false }]
```

---

### `POST /action-items/`
Create a new action item (always starts incomplete).

**Request body** — `ActionItemCreate`

| Field | Type | Constraints |
|-------|------|-------------|
| `description` | string | required, min 1 char, whitespace stripped |

**Response 201** — `ActionItemRead`
**Response 422** — validation error

---

### `PUT /action-items/{item_id}/complete`
Mark a single action item as completed. Idempotent (calling twice is safe).

**Path params**: `item_id` (integer, required)

**Response 200** — `ActionItemRead` (with `completed: true`)
**Response 404** — item not found

---

### `POST /action-items/bulk-complete`
Mark multiple action items as completed in a single atomic transaction.

- Deduplicates IDs before processing.
- **All-or-nothing**: if any ID does not exist, the whole operation is rolled back and `404` is returned.

**Request body** — `BulkCompleteRequest`

| Field | Type | Constraints |
|-------|------|-------------|
| `ids` | `list[int]` | Non-empty; duplicates are deduplicated |

```json
{ "ids": [1, 2, 3] }
```

**Response 200** — `BulkCompleteResponse`
```json
{ "updated": 3, "ids": [1, 2, 3] }
```

**Response 404** — one or more IDs not found; nothing was persisted.
```json
{ "detail": "Action items not found: [99]" }
```

**Response 422** — validation error (e.g. empty `ids` list).

---

## Schemas

### `NoteRead`
```json
{ "id": 1, "title": "string", "content": "string" }
```

### `NoteCreate` / `NoteUpdate`
```json
{ "title": "string (1-200 chars)", "content": "string (min 1 char)" }
```

### `ActionItemRead`
```json
{ "id": 1, "description": "string", "completed": false }
```

### `ActionItemCreate`
```json
{ "description": "string (min 1 char)" }
```

### `BulkCompleteRequest`
```json
{ "ids": [1, 2, 3] }
```

### `BulkCompleteResponse`
```json
{ "updated": 3, "ids": [1, 2, 3] }
```

### Validation error (422)
```json
{
  "detail": [
    { "loc": ["body", "title"], "msg": "String should have at least 1 character", "type": "string_too_short" }
  ]
}
```
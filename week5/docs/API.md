# API Reference — Week 5 Backend

Base URL: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

---

## Notes

### `GET /notes/`
Return all notes.

**Response** `200`
```json
[
  { "id": 1, "title": "My note", "content": "Hello world" }
]
```

---

### `POST /notes/`
Create a note.

**Body**
```json
{ "title": "string", "content": "string" }
```

**Response** `201`
```json
{ "id": 2, "title": "string", "content": "string" }
```

---

### `GET /notes/{note_id}`
Get a single note by ID.

**Path param** `note_id: int`

**Response** `200` — `NoteRead` object  
**Response** `404` — `{ "detail": "Note not found" }`

---

### `GET /notes/search/`
Search notes by title or content (case-insensitive substring match).

**Query params**
| Param | Type | Description |
|-------|------|-------------|
| `q` | `string` (optional) | Search term; omit to return all |

**Response** `200` — list of `NoteRead`

---

## Action Items

### `GET /action-items/`
Return action items, optionally filtered by completion status.

**Query params**
| Param | Type | Description |
|-------|------|-------------|
| `completed` | `bool` (optional) | `true` → only done items; `false` → only open items; omit → all |

**Response** `200`
```json
[
  { "id": 1, "description": "Ship it", "completed": false }
]
```

---

### `POST /action-items/`
Create a new action item (always starts incomplete).

**Body**
```json
{ "description": "string" }
```

**Response** `201`
```json
{ "id": 3, "description": "string", "completed": false }
```

---

### `PUT /action-items/{item_id}/complete`
Mark a single action item as completed.

**Path param** `item_id: int`

**Response** `200` — `ActionItemRead` with `completed: true`  
**Response** `404` — `{ "detail": "Action item not found" }`

---

### `POST /action-items/bulk-complete`
Mark multiple action items as completed in a single atomic transaction.

- Deduplicates IDs before processing.
- **All-or-nothing**: if any ID does not exist the whole operation is rolled back and `404` is returned.

**Body**
```json
{ "ids": [1, 2, 3] }
```

| Field | Type | Constraints |
|-------|------|-------------|
| `ids` | `list[int]` | Non-empty; duplicates are ignored |

**Response** `200`
```json
{ "updated": 3, "ids": [1, 2, 3] }
```

**Response** `404` — one or more IDs were not found; nothing was persisted.
```json
{ "detail": "Action items not found: [99]" }
```

**Response** `422` — validation error (e.g. empty `ids` list).

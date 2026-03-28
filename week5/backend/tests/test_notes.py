# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create(client, title="Test Note", content="Some content"):
    """Create a note and return its JSON payload."""
    r = client.post("/notes/", json={"title": title, "content": content})
    assert r.status_code == 201, r.text
    return r.json()


# ---------------------------------------------------------------------------
# Create & list
# ---------------------------------------------------------------------------


def test_create_and_list_notes(client):
    note = _create(client, title="Test", content="Hello world")
    assert note["title"] == "Test"
    assert note["id"] is not None

    r = client.get("/notes/")
    assert r.status_code == 200
    assert any(n["id"] == note["id"] for n in r.json())


def test_create_note_strips_whitespace(client):
    note = _create(client, title="  Padded  ", content="  spaced  ")
    assert note["title"] == "Padded"
    assert note["content"] == "spaced"


def test_create_note_empty_title_rejected(client):
    r = client.post("/notes/", json={"title": "", "content": "ok"})
    assert r.status_code == 422


def test_create_note_whitespace_only_title_rejected(client):
    r = client.post("/notes/", json={"title": "   ", "content": "ok"})
    assert r.status_code == 422


def test_create_note_empty_content_rejected(client):
    r = client.post("/notes/", json={"title": "Title", "content": ""})
    assert r.status_code == 422


def test_create_note_title_too_long_rejected(client):
    r = client.post("/notes/", json={"title": "x" * 201, "content": "ok"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


def test_search_notes_no_query_returns_all(client):
    _create(client, title="Alpha", content="first")
    _create(client, title="Beta", content="second")
    r = client.get("/notes/search/")
    assert r.status_code == 200
    assert len(r.json()) >= 2


def test_search_notes_by_title(client):
    _create(client, title="Unique-XYZ", content="irrelevant")
    r = client.get("/notes/search/", params={"q": "Unique-XYZ"})
    assert r.status_code == 200
    assert any("Unique-XYZ" in n["title"] for n in r.json())


def test_search_notes_by_content(client):
    _create(client, title="Whatever", content="hello-world-content")
    r = client.get("/notes/search/", params={"q": "hello-world-content"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_search_notes_no_match_returns_empty(client):
    r = client.get("/notes/search/", params={"q": "zzz-no-match-zzz"})
    assert r.status_code == 200
    assert r.json() == []


# ---------------------------------------------------------------------------
# Update (PUT)
# ---------------------------------------------------------------------------


def test_update_note_success(client):
    note = _create(client, title="Original", content="Old content")
    r = client.put(f"/notes/{note['id']}", json={"title": "Updated", "content": "New content"})
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == note["id"]  # id unchanged
    assert data["title"] == "Updated"
    assert data["content"] == "New content"


def test_update_note_persists(client):
    """Verify the update is durable — a subsequent GET returns the new values."""
    note = _create(client)
    client.put(f"/notes/{note['id']}", json={"title": "Persisted", "content": "Yes"})
    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "Persisted"


def test_update_note_not_found(client):
    r = client.put("/notes/99999", json={"title": "X", "content": "Y"})
    assert r.status_code == 404


def test_update_note_empty_title_rejected(client):
    note = _create(client)
    r = client.put(f"/notes/{note['id']}", json={"title": "", "content": "ok"})
    assert r.status_code == 422


def test_update_note_whitespace_title_rejected(client):
    note = _create(client)
    r = client.put(f"/notes/{note['id']}", json={"title": "   ", "content": "ok"})
    assert r.status_code == 422


def test_update_note_empty_content_rejected(client):
    note = _create(client)
    r = client.put(f"/notes/{note['id']}", json={"title": "ok", "content": ""})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


def test_delete_note_success(client):
    note = _create(client)
    r = client.delete(f"/notes/{note['id']}")
    assert r.status_code == 204
    assert r.content == b""  # 204 has no body


def test_delete_note_removes_from_list(client):
    """Deleted note must not appear in subsequent list or get responses."""
    note = _create(client)
    client.delete(f"/notes/{note['id']}")

    r = client.get("/notes/")
    assert all(n["id"] != note["id"] for n in r.json())

    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/99999")
    assert r.status_code == 404


def test_delete_note_idempotent_second_call_returns_404(client):
    """Deleting an already-deleted note should 404, not 500."""
    note = _create(client)
    client.delete(f"/notes/{note['id']}")
    r = client.delete(f"/notes/{note['id']}")
    assert r.status_code == 404

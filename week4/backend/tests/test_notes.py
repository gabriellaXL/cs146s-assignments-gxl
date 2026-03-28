def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_update_and_delete_note(client):
    payload = {"title": "Draft note", "content": "Longer draft body"}
    created = client.post("/notes/", json=payload)
    note_id = created.json()["id"]

    update_payload = {"title": "Updated note", "content": "Updated note body"}
    r = client.put(f"/notes/{note_id}", json=update_payload)
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "Updated note"

    fetched = client.get(f"/notes/{note_id}")
    assert fetched.status_code == 200
    assert fetched.json()["content"] == "Updated note body"

    deleted = client.delete(f"/notes/{note_id}")
    assert deleted.status_code == 204, deleted.text

    missing = client.get(f"/notes/{note_id}")
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Note not found"


def test_note_validation_and_missing_note_errors(client):
    invalid_payload = {"title": "No", "content": "tiny"}
    r = client.post("/notes/", json=invalid_payload)
    assert r.status_code == 400
    assert "title" in r.json()["detail"][0]

    update_payload = {"title": "Valid title", "content": "Valid content body"}
    missing = client.put("/notes/999", json=update_payload)
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Note not found"


def test_search_case_insensitive(client):
    # Create a note with lowercase text
    client.post("/notes/", json={"title": "hello python", "content": "learning about loops"})

    # Search with uppercase keyword that matches the lowercase title
    r = client.get("/notes/search/", params={"q": "PYTHON"})
    assert r.status_code == 200
    items = r.json()
    assert any("python" in item["title"].lower() for item in items)

    # Search with mixed-case keyword matching content
    r = client.get("/notes/search/", params={"q": "Loops"})
    assert r.status_code == 200
    items = r.json()
    assert any("loops" in item["content"].lower() for item in items)


def test_partial_put_title_only(client):
    created = client.post("/notes/", json={"title": "Original title", "content": "Original content body"})
    assert created.status_code == 201
    note_id = created.json()["id"]
    original_content = created.json()["content"]

    r = client.put(f"/notes/{note_id}", json={"title": "New title only"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["title"] == "New title only"
    # Content must remain unchanged
    assert data["content"] == original_content


def test_partial_put_content_only(client):
    created = client.post("/notes/", json={"title": "Stable title here", "content": "Old content body"})
    assert created.status_code == 201
    note_id = created.json()["id"]
    original_title = created.json()["title"]

    r = client.put(f"/notes/{note_id}", json={"content": "Completely new content body"})
    assert r.status_code == 200, r.text
    data = r.json()
    # Title must remain unchanged
    assert data["title"] == original_title
    assert data["content"] == "Completely new content body"


def test_partial_put_invalid_title_too_short(client):
    created = client.post("/notes/", json={"title": "Valid long title", "content": "Valid long content"})
    assert created.status_code == 201
    note_id = created.json()["id"]

    # Title shorter than min_length=3 should fail validation
    r = client.put(f"/notes/{note_id}", json={"title": "Hi"})
    assert r.status_code == 400, r.text


def test_post_content_too_short(client):
    # content must be at least 5 characters
    r = client.post("/notes/", json={"title": "Valid title", "content": "abc"})
    assert r.status_code == 400, r.text


def test_delete_nonexistent_note_returns_404(client):
    r = client.delete("/notes/99999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Note not found"

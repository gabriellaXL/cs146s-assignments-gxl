def test_create_get_extract_patch_and_delete_notes(client):
    payload = {
        "title": "Test",
        "content": "Hello world\nTODO: write tests\nPlease send the recap by Friday.",
    }
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"
    assert "created_at" in data and "updated_at" in data

    note_id = data["id"]
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["content"] == payload["content"]

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/", params={"q": "Hello", "limit": 10, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.post(f"/notes/{note_id}/extract-action-items")
    assert r.status_code == 200
    extracted = r.json()
    assert extracted["note_id"] == note_id
    assert extracted["count"] == 2
    assert extracted["items"][0]["text"] == "write tests"
    assert extracted["items"][0]["trigger"] == "tagged"
    assert extracted["items"][0]["confidence"] == "high"
    assert extracted["items"][1]["text"] == "send the recap by Friday"
    assert extracted["items"][1]["due_hint"] == "by Friday"

    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["title"] == "Updated"

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204
    assert r.text == ""

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404
    assert r.json() == {"detail": "Note not found"}


def test_note_validation_and_query_errors(client):
    r = client.post("/notes/", json={"title": "   ", "content": "Hello"})
    assert r.status_code == 422

    r = client.post("/notes/", json={"title": "Valid", "content": "Body"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.patch(f"/notes/{note_id}", json={"content": "   "})
    assert r.status_code == 422

    r = client.get("/notes/", params={"skip": -1})
    assert r.status_code == 422

    r = client.get("/notes/", params={"sort": "-unknown"})
    assert r.status_code == 422

    r = client.post("/notes/999/extract-action-items")
    assert r.status_code == 404
    assert r.json() == {"detail": "Note not found"}

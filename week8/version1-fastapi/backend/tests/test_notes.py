def test_create_get_list_patch_and_delete_notes(client):
    payload = {
        "title": "Ship week 8",
        "content": "Finish the FastAPI implementation with stable CRUD flows.",
        "status": "active",
    }

    response = client.post("/notes/", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["status"] == payload["status"]
    assert "created_at" in data and "updated_at" in data

    note_id = data["id"]

    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["content"] == payload["content"]

    response = client.get("/notes/")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1

    response = client.get("/notes/", params={"q": "FastAPI", "limit": 10, "sort": "-updated_at"})
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.patch(
        f"/notes/{note_id}",
        json={"title": "Updated title", "status": "blocked"},
    )
    assert response.status_code == 200
    patched = response.json()
    assert patched["title"] == "Updated title"
    assert patched["status"] == "blocked"

    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == 204
    assert response.text == ""

    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Note not found"}


def test_validation_and_query_errors(client):
    response = client.post("/notes/", json={"title": "Hi", "content": "short", "status": "active"})
    assert response.status_code == 422

    response = client.post(
        "/notes/",
        json={
            "title": "Valid title",
            "content": "This note body is long enough.",
            "status": "active",
        },
    )
    assert response.status_code == 201
    note_id = response.json()["id"]

    response = client.patch(f"/notes/{note_id}", json={"content": "tiny"})
    assert response.status_code == 422

    response = client.patch(f"/notes/{note_id}", json={"status": "invalid"})
    assert response.status_code == 422

    response = client.get("/notes/", params={"skip": -1})
    assert response.status_code == 422

    response = client.get("/notes/", params={"sort": "-unknown"})
    assert response.status_code == 422

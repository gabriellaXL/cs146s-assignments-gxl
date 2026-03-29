def test_create_get_complete_list_patch_and_delete_action_item(client):
    r = client.post("/projects/", json={"name": "Frontend Polish", "description": "UI cleanup"})
    assert r.status_code == 201
    project_id = r.json()["id"]

    payload = {"description": "Ship it", "project_id": project_id}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False
    assert item["project_id"] == project_id
    assert item["project"]["name"] == "Frontend Polish"
    assert "created_at" in item and "updated_at" in item

    item_id = item["id"]
    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 200
    assert r.json()["description"] == payload["description"]
    assert r.json()["project"]["name"] == "Frontend Polish"

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/", params={"completed": True, "limit": 5, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.patch(f"/action-items/{item['id']}", json={"description": "Updated", "project_id": None})
    assert r.status_code == 200
    patched = r.json()
    assert patched["description"] == "Updated"
    assert patched["project_id"] is None

    r = client.delete(f"/action-items/{item_id}")
    assert r.status_code == 204
    assert r.text == ""

    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 404
    assert r.json() == {"detail": "Action item not found"}


def test_action_item_validation_and_query_errors(client):
    r = client.post("/action-items/", json={"description": "   "})
    assert r.status_code == 422

    r = client.post("/action-items/", json={"description": "Ship release"})
    assert r.status_code == 201
    item_id = r.json()["id"]

    r = client.patch(f"/action-items/{item_id}", json={"description": ""})
    assert r.status_code == 422

    r = client.get("/action-items/", params={"limit": 0})
    assert r.status_code == 422

    r = client.get("/action-items/", params={"sort": "priority"})
    assert r.status_code == 422

    r = client.patch(f"/action-items/{item_id}", json={"project_id": 999})
    assert r.status_code == 404
    assert r.json() == {"detail": "Project not found"}

    r = client.patch("/action-items/999", json={"completed": True})
    assert r.status_code == 404
    assert r.json() == {"detail": "Action item not found"}

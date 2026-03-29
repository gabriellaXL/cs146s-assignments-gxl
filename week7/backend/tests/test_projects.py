def test_create_get_patch_and_delete_project_with_relationships(client):
    r = client.post(
        "/projects/",
        json={"name": "Platform Refresh", "description": "Coordinate the starter upgrade"},
    )
    assert r.status_code == 201, r.text
    project = r.json()
    assert project["name"] == "Platform Refresh"
    assert project["action_item_count"] == 0

    project_id = project["id"]

    r = client.post(
        "/action-items/",
        json={"description": "Review migration plan", "project_id": project_id},
    )
    assert r.status_code == 201, r.text
    action_item = r.json()
    assert action_item["project_id"] == project_id
    assert action_item["project"]["name"] == "Platform Refresh"

    r = client.get(f"/projects/{project_id}")
    assert r.status_code == 200
    detail = r.json()
    assert detail["name"] == "Platform Refresh"
    assert len(detail["action_items"]) == 1
    assert detail["action_items"][0]["description"] == "Review migration plan"

    r = client.patch(f"/projects/{project_id}", json={"description": "Updated scope"})
    assert r.status_code == 200
    assert r.json()["description"] == "Updated scope"
    assert r.json()["action_item_count"] == 1

    r = client.delete(f"/projects/{project_id}")
    assert r.status_code == 204

    r = client.get(f"/action-items/{action_item['id']}")
    assert r.status_code == 200
    assert r.json()["project_id"] is None
    assert r.json()["project"] is None

    r = client.get(f"/projects/{project_id}")
    assert r.status_code == 404
    assert r.json() == {"detail": "Project not found"}


def test_project_validation_uniqueness_and_filters(client):
    r = client.post("/projects/", json={"name": "Course Ops", "description": "Run the release"})
    assert r.status_code == 201
    project_id = r.json()["id"]

    r = client.post("/projects/", json={"name": "Course Ops", "description": "Duplicate"})
    assert r.status_code == 409
    assert r.json() == {"detail": "Project name already exists"}

    r = client.post("/action-items/", json={"description": "Ship release", "project_id": project_id})
    assert r.status_code == 201

    r = client.get("/projects/", params={"q": "Course", "sort": "name"})
    assert r.status_code == 200
    projects = r.json()
    assert len(projects) == 1
    assert projects[0]["action_item_count"] == 1

    r = client.get("/action-items/", params={"project_id": project_id})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["project"]["name"] == "Course Ops"

    r = client.post("/action-items/", json={"description": "Broken", "project_id": 999})
    assert r.status_code == 404
    assert r.json() == {"detail": "Project not found"}

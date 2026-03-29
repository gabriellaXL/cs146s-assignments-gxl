def _create_note(client, title: str, content: str) -> dict:
    response = client.post("/notes/", json={"title": title, "content": content})
    assert response.status_code == 201, response.text
    return response.json()


def _create_project(client, name: str, description: str | None = None) -> dict:
    response = client.post("/projects/", json={"name": name, "description": description})
    assert response.status_code == 201, response.text
    return response.json()


def _create_action_item(
    client,
    description: str,
    *,
    project_id: int | None = None,
    completed: bool = False,
) -> dict:
    response = client.post(
        "/action-items/",
        json={"description": description, "project_id": project_id},
    )
    assert response.status_code == 201, response.text
    item = response.json()
    if completed:
        response = client.patch(f"/action-items/{item['id']}", json={"completed": True})
        assert response.status_code == 200, response.text
        item = response.json()
    return item


def test_notes_list_supports_stable_sorting_and_pagination(client):
    _create_note(client, "Gamma", "release follow-up")
    _create_note(client, "Alpha", "architecture notes")
    _create_note(client, "Beta", "release checklist")

    response = client.get("/notes/", params={"sort": "title", "limit": 10})
    assert response.status_code == 200
    titles = [item["title"] for item in response.json()]
    assert titles == ["Alpha", "Beta", "Gamma"]

    response = client.get("/notes/", params={"sort": "-title", "skip": 1, "limit": 1})
    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == ["Beta"]

    response = client.get("/notes/", params={"q": "release", "sort": "title"})
    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == ["Beta", "Gamma"]

    response = client.get("/notes/", params={"sort": "title", "skip": 10, "limit": 5})
    assert response.status_code == 200
    assert response.json() == []


def test_action_items_list_combines_sorting_pagination_and_filters(client):
    platform = _create_project(client, "Platform")
    release = _create_project(client, "Release")

    _create_action_item(client, "Gamma deploy", project_id=platform["id"], completed=True)
    _create_action_item(client, "Alpha audit", project_id=platform["id"], completed=False)
    _create_action_item(client, "Beta checklist", project_id=release["id"], completed=True)

    response = client.get("/action-items/", params={"sort": "description", "limit": 10})
    assert response.status_code == 200
    descriptions = [item["description"] for item in response.json()]
    assert descriptions == ["Alpha audit", "Beta checklist", "Gamma deploy"]

    response = client.get(
        "/action-items/",
        params={"completed": True, "sort": "-description", "skip": 1, "limit": 1},
    )
    assert response.status_code == 200
    items = response.json()
    assert [item["description"] for item in items] == ["Beta checklist"]

    response = client.get(
        "/action-items/",
        params={"project_id": platform["id"], "sort": "description"},
    )
    assert response.status_code == 200
    items = response.json()
    assert [item["description"] for item in items] == ["Alpha audit", "Gamma deploy"]
    assert {item["project"]["name"] for item in items} == {"Platform"}

    response = client.get(
        "/action-items/",
        params={"project_id": platform["id"], "completed": False, "sort": "description"},
    )
    assert response.status_code == 200
    assert [item["description"] for item in response.json()] == ["Alpha audit"]

    response = client.get(
        "/action-items/",
        params={"project_id": platform["id"], "completed": False, "skip": 5, "limit": 5},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_projects_list_supports_sorting_search_and_page_boundaries(client):
    _create_project(client, "Zebra", "Operations follow-up")
    alpha = _create_project(client, "Alpha", "Core platform")
    meteor = _create_project(client, "Meteor", "Release planning")

    _create_action_item(client, "Project Alpha kickoff", project_id=alpha["id"])
    _create_action_item(client, "Project Alpha QA", project_id=alpha["id"])
    _create_action_item(client, "Meteor dry run", project_id=meteor["id"])

    response = client.get("/projects/", params={"sort": "name"})
    assert response.status_code == 200
    projects = response.json()
    assert [item["name"] for item in projects] == ["Alpha", "Meteor", "Zebra"]
    assert [item["action_item_count"] for item in projects] == [2, 1, 0]

    response = client.get("/projects/", params={"sort": "-name", "skip": 1, "limit": 1})
    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Meteor"]

    response = client.get("/projects/", params={"q": "e", "sort": "name"})
    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Meteor", "Zebra"]

    response = client.get("/projects/", params={"skip": 10, "limit": 10})
    assert response.status_code == 200
    assert response.json() == []

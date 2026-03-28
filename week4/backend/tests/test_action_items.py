def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1


def test_action_item_validation_and_missing_item(client):
    invalid = client.post("/action-items/", json={"description": "no"})
    assert invalid.status_code == 400
    assert "description" in invalid.json()["detail"][0]

    missing = client.put("/action-items/999/complete")
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Action item not found"

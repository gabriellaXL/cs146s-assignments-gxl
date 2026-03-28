# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create(client, description: str) -> dict:
    """Create an action item and return its JSON payload."""
    r = client.post("/action-items/", json={"description": description})
    assert r.status_code == 201, r.text
    return r.json()


def _complete_one(client, item_id: int) -> dict:
    """Complete a single item via the existing PUT endpoint."""
    r = client.put(f"/action-items/{item_id}/complete")
    assert r.status_code == 200, r.text
    return r.json()


# ---------------------------------------------------------------------------
# Original happy-path (kept for regression)
# ---------------------------------------------------------------------------


def test_create_and_complete_action_item(client):
    item = _create(client, "Ship it")
    assert item["completed"] is False

    done = _complete_one(client, item["id"])
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    assert len(r.json()) == 1


# ---------------------------------------------------------------------------
# Filter tests — GET /action-items/?completed=true|false
# ---------------------------------------------------------------------------


def test_filter_no_param_returns_all(client):
    """Omitting the query param returns every item."""
    a = _create(client, "open task")
    b = _create(client, "done task")
    _complete_one(client, b["id"])

    r = client.get("/action-items/")
    assert r.status_code == 200
    ids = {i["id"] for i in r.json()}
    assert {a["id"], b["id"]} == ids


def test_filter_completed_false_returns_only_open(client):
    """completed=false returns only incomplete items."""
    open_item = _create(client, "still open")
    done_item = _create(client, "already done")
    _complete_one(client, done_item["id"])

    r = client.get("/action-items/", params={"completed": "false"})
    assert r.status_code == 200
    items = r.json()
    ids = {i["id"] for i in items}
    assert open_item["id"] in ids
    assert done_item["id"] not in ids
    assert all(not i["completed"] for i in items)


def test_filter_completed_true_returns_only_done(client):
    """completed=true returns only completed items."""
    open_item = _create(client, "still open")
    done_item = _create(client, "already done")
    _complete_one(client, done_item["id"])

    r = client.get("/action-items/", params={"completed": "true"})
    assert r.status_code == 200
    items = r.json()
    ids = {i["id"] for i in items}
    assert done_item["id"] in ids
    assert open_item["id"] not in ids
    assert all(i["completed"] for i in items)


def test_filter_returns_empty_list_when_no_match(client):
    """Filter returns an empty list (not 404) when no items match."""
    _create(client, "open task")  # no completed items exist

    r = client.get("/action-items/", params={"completed": "true"})
    assert r.status_code == 200
    assert r.json() == []


# ---------------------------------------------------------------------------
# Bulk-complete tests — POST /action-items/bulk-complete
# ---------------------------------------------------------------------------


def test_bulk_complete_all_valid_ids(client):
    """All valid IDs are marked complete; response contains correct count and IDs."""
    a = _create(client, "task A")
    b = _create(client, "task B")
    c = _create(client, "task C")

    r = client.post("/action-items/bulk-complete", json={"ids": [a["id"], b["id"], c["id"]]})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["updated"] == 3
    assert sorted(body["ids"]) == sorted([a["id"], b["id"], c["id"]])

    # Verify persistence via filter endpoint
    r = client.get("/action-items/", params={"completed": "false"})
    assert r.json() == []


def test_bulk_complete_subset_of_items(client):
    """Only the requested subset is completed; others remain open."""
    a = _create(client, "task A")
    b = _create(client, "task B")
    c = _create(client, "task C")

    r = client.post("/action-items/bulk-complete", json={"ids": [a["id"], c["id"]]})
    assert r.status_code == 200
    assert r.json()["updated"] == 2

    # b must still be open
    r = client.get("/action-items/", params={"completed": "false"})
    open_ids = {i["id"] for i in r.json()}
    assert b["id"] in open_ids
    assert a["id"] not in open_ids
    assert c["id"] not in open_ids


def test_bulk_complete_idempotent(client):
    """Completing already-completed items is fine (idempotent)."""
    a = _create(client, "task A")
    _complete_one(client, a["id"])  # already done

    r = client.post("/action-items/bulk-complete", json={"ids": [a["id"]]})
    assert r.status_code == 200
    assert r.json()["updated"] == 1


def test_bulk_complete_deduplicates_ids(client):
    """Duplicate IDs in the request are deduplicated; updated count is 1."""
    a = _create(client, "task A")

    r = client.post("/action-items/bulk-complete", json={"ids": [a["id"], a["id"], a["id"]]})
    assert r.status_code == 200
    body = r.json()
    assert body["updated"] == 1
    assert body["ids"] == [a["id"]]


def test_bulk_complete_unknown_id_returns_404(client):
    """A single unknown ID causes a 404; the transaction is rolled back."""
    a = _create(client, "real task")
    nonexistent_id = 99999

    r = client.post("/action-items/bulk-complete", json={"ids": [nonexistent_id]})
    assert r.status_code == 404
    assert str(nonexistent_id) in r.text

    # `a` must remain incomplete (rollback confirmed)
    r = client.get("/action-items/", params={"completed": "false"})
    open_ids = {i["id"] for i in r.json()}
    assert a["id"] in open_ids


def test_bulk_complete_mixed_valid_invalid_rolls_back(client):
    """Mix of valid + invalid IDs → 404 and no items are persisted as complete."""
    a = _create(client, "real task A")
    b = _create(client, "real task B")
    nonexistent_id = 99999

    r = client.post(
        "/action-items/bulk-complete",
        json={"ids": [a["id"], nonexistent_id, b["id"]]},
    )
    assert r.status_code == 404

    # Both real items must remain incomplete
    r = client.get("/action-items/", params={"completed": "false"})
    open_ids = {i["id"] for i in r.json()}
    assert a["id"] in open_ids
    assert b["id"] in open_ids


def test_bulk_complete_empty_list_returns_422(client):
    """An empty ids list is rejected by Pydantic validation (422)."""
    r = client.post("/action-items/bulk-complete", json={"ids": []})
    assert r.status_code == 422

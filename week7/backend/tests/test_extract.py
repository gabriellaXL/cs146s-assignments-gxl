from backend.app.services.extract import analyze_action_items, extract_action_items


def test_extract_action_items_supports_multiple_patterns():
    text = """
    This is a note
    - TODO: write tests
    - [ ] prepare demo
    Please send the recap by Friday.
    Assign release checklist to Alice Johnson by 2026-04-01.
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert items == [
        "write tests",
        "prepare demo",
        "send the recap by Friday",
        "Assign release checklist to Alice Johnson by 2026-04-01",
    ]


def test_analyze_action_items_returns_metadata_and_deduplicates():
    text = """
    TODO: review the API contract
    - review the API contract
    [ ] schedule launch review on Tuesday
    Assign rollout plan to Bob Smith by 2026-04-01.
    """.strip()

    items = analyze_action_items(text)

    assert len(items) == 3
    assert items[0].text == "review the API contract"
    assert items[0].trigger == "tagged"
    assert items[0].confidence == "high"
    assert items[0].source_line == 1

    assert items[1].text == "schedule launch review on Tuesday"
    assert items[1].trigger == "checkbox"
    assert items[1].due_hint == "on Tuesday"

    assert items[2].text == "Assign rollout plan to Bob Smith by 2026-04-01"
    assert items[2].trigger == "imperative"
    assert items[2].assignee_hint == "Bob Smith"
    assert items[2].due_hint == "by 2026-04-01"


def test_analyze_action_items_skips_completed_or_non_actionable_lines():
    text = """
    [x] already deployed
    Done: notify the team
    Summary: the migration succeeded
    Review the follow-up checklist
    """.strip()

    items = analyze_action_items(text)

    assert len(items) == 1
    assert items[0].text == "Review the follow-up checklist"
    assert items[0].trigger == "imperative"

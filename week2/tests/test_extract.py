import json

from ..app.services import extract
from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items

# ai generated
def test_extract_action_items_llm_empty():#空输入测试
    """Test LLM extraction with empty or whitespace-only input."""
    assert extract_action_items_llm("") == []
    assert extract_action_items_llm("   \n  ") == []


def test_extract_action_items_llm_bullet_list(monkeypatch):#列表输入测试
    """LLM extraction should normalize bullet/checklist style inputs."""
    captured = {}

    class _FakeResponse:
        class message:
            content = json.dumps({"items": ["Fix database migration", "Write integration tests"]})

    def _fake_chat(**kwargs):
        captured.update(kwargs)
        return _FakeResponse()

    monkeypatch.setattr(extract, "chat", _fake_chat)

    text = """
    - [ ] Fix database migration
    * Write integration tests
    """.strip()

    items = extract_action_items_llm(text)

    assert items == ["Fix database migration", "Write integration tests"]
    assert captured["model"] == "llama3.1:8b"
    assert captured["options"]["temperature"] == 0.0


def test_extract_action_items_llm_keyword_prefixed_lines(monkeypatch):#关键词前缀输入测试 覆盖 TODO: / ACTION: 形式输入
    """LLM extraction should handle TODO/ACTION style prefixes."""
    class _FakeResponse:
        class message:
            content = json.dumps({"items": ["Update README", "Email project mentor"]})

    monkeypatch.setattr(extract, "chat", lambda **kwargs: _FakeResponse())

    text = """
    TODO: Update README
    ACTION: Email project mentor
    FYI: The weather is nice.
    """.strip()

    items = extract_action_items_llm(text)
    assert items == ["Update README", "Email project mentor"]


def test_extract_action_items_llm_implicit_tasks_in_prose(monkeypatch):#自然语言隐藏任务提取 测试
    """LLM extraction should find tasks hidden in natural language prose, which heuristic fails to do."""
    class _FakeResponse:
        class message:
            content = json.dumps({"items": ["schedule a follow-up meeting with design team", "buy more coffee for the office"]})

    monkeypatch.setattr(extract, "chat", lambda **kwargs: _FakeResponse())

    text = """
    The meeting went well. John mentioned that we really need to schedule a follow-up meeting with design team next week.
    Also, please remember to buy more coffee for the office, we are running out.
    """.strip()

    items = extract_action_items_llm(text)
    assert items == ["schedule a follow-up meeting with design team", "buy more coffee for the office"]


def test_extract_action_items_llm_fallback_to_heuristic_on_chat_error(monkeypatch):#错误输入测试 异常回退测试 当 chat() 抛错时，验证会回退到 extract_action_items() 启发式逻辑
    """If chat fails, extractor should fall back to heuristic extraction."""
    def _raise_chat_error(**kwargs):
        raise RuntimeError("Ollama unavailable")

    monkeypatch.setattr(extract, "chat", _raise_chat_error)

    text = """
    TODO: Update README
    - [ ] Write tests
    """.strip()

    items = extract_action_items_llm(text)
    assert items == ["TODO: Update README", "Write tests"]

if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main(["-v", __file__]))

import re
from dataclasses import dataclass

LIST_MARKER_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s*")
TAGGED_ACTION_RE = re.compile(
    r"^(?P<label>todo|action|follow[- ]up|next step)\s*:\s*(?P<body>.+)$",
    re.IGNORECASE,
)
UNCHECKED_CHECKBOX_RE = re.compile(r"^\[\s\]\s+(?P<body>.+)$")
COMMITMENT_RE = re.compile(
    r"^(?:need to|needs to|should|must|can you|could you|let's)\s+(?P<body>.+)$",
    re.IGNORECASE,
)
IMPERATIVE_RE = re.compile(
    r"^(?P<body>(?:"
    r"review|write|update|send|prepare|schedule|follow up|follow-up|create|fix|"
    r"investigate|document|test|deploy|ship|confirm|coordinate|email|call|draft|"
    r"finalize|clean up|check|summarize|refactor|assign"
    r")\b.+)$",
    re.IGNORECASE,
)
NON_ACTIONABLE_PREFIX_RE = re.compile(
    r"^(?:done|completed|fyi|for your information|note|summary|background|context)\b",
    re.IGNORECASE,
)
DUE_HINT_RE = re.compile(
    r"\b(?P<hint>(?:by|before|on)\s+(?:today|tomorrow|monday|tuesday|wednesday|thursday|"
    r"friday|saturday|sunday|eod|\d{4}-\d{2}-\d{2}|[A-Z][a-z]+(?:\s+\d{1,2})?))\b",
    re.IGNORECASE,
)
ASSIGNEE_HINT_RE = re.compile(
    r"\b(?:owner|assignee)\s*:\s*(?P<hint>[A-Za-z][\w .-]*)",
    re.IGNORECASE,
)
ASSIGN_TO_RE = re.compile(
    r"\bassign\s+.+?\s+to\s+"
    r"(?P<hint>[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)"
    r"(?=\s+(?:by|before|on)\b|[.!?]?$)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ExtractedActionItem:
    text: str
    source_line: int
    trigger: str
    confidence: str
    due_hint: str | None = None
    assignee_hint: str | None = None


def analyze_action_items(text: str) -> list[ExtractedActionItem]:
    seen: set[str] = set()
    results: list[ExtractedActionItem] = []

    for source_line, raw_line in enumerate(text.splitlines(), start=1):
        candidate = _prepare_candidate(raw_line)
        if not candidate:
            continue

        match = _match_action(candidate)
        if match is None:
            continue

        item_text = _normalize_action_text(match["body"])
        if not item_text or NON_ACTIONABLE_PREFIX_RE.match(item_text):
            continue

        dedupe_key = _normalize_for_dedup(item_text)
        if dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        results.append(
            ExtractedActionItem(
                text=item_text,
                source_line=source_line,
                trigger=match["trigger"],
                confidence=match["confidence"],
                due_hint=_extract_due_hint(item_text),
                assignee_hint=_extract_assignee_hint(candidate),
            )
        )

    return results


def extract_action_items(text: str) -> list[str]:
    return [item.text for item in analyze_action_items(text)]


def _prepare_candidate(raw_line: str) -> str:
    stripped = raw_line.strip()
    if not stripped:
        return ""
    return LIST_MARKER_RE.sub("", stripped).strip()


def _match_action(candidate: str) -> dict[str, str] | None:
    tagged = TAGGED_ACTION_RE.match(candidate)
    if tagged:
        return {
            "body": tagged.group("body"),
            "trigger": "tagged",
            "confidence": "high",
        }

    unchecked = UNCHECKED_CHECKBOX_RE.match(candidate)
    if unchecked:
        return {
            "body": unchecked.group("body"),
            "trigger": "checkbox",
            "confidence": "high",
        }

    if candidate.lower().startswith("please "):
        body = candidate[7:].strip()
        if _is_imperative(body):
            return {
                "body": body,
                "trigger": "commitment",
                "confidence": "medium",
            }

    commitment = COMMITMENT_RE.match(candidate)
    if commitment:
        return {
            "body": commitment.group("body"),
            "trigger": "commitment",
            "confidence": "medium",
        }

    if _is_imperative(candidate):
        return {
            "body": candidate,
            "trigger": "imperative",
            "confidence": "medium",
        }

    return None


def _normalize_action_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned.rstrip(" .;:")


def _normalize_for_dedup(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _extract_due_hint(text: str) -> str | None:
    match = DUE_HINT_RE.search(text)
    return match.group("hint") if match else None


def _extract_assignee_hint(text: str) -> str | None:
    tagged_hint = ASSIGNEE_HINT_RE.search(text)
    if tagged_hint:
        return tagged_hint.group("hint").strip()

    assigned_hint = ASSIGN_TO_RE.search(text)
    if assigned_hint:
        return assigned_hint.group("hint").strip()

    return None


def _is_imperative(text: str) -> bool:
    return IMPERATIVE_RE.match(text) is not None

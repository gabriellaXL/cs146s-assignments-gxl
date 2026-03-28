from __future__ import annotations

import json
import logging
import re
from typing import List

from dotenv import load_dotenv
from ollama import chat
from pydantic import BaseModel

load_dotenv()
logger = logging.getLogger(__name__)

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


# 正则化/启发式提取
def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


# ai-generated,由ai驱动的提取方案，使用 Ollama 通过大语言模型来做行动项提取。 可以提取出没有[ ]前缀的纯文本行，这是比原来的正则启发式更智能的地方之一。
# 在后面的TODO中，LLM提取会是一个新的独立API接口，会有两种提取方式可选，与正则化提取函数不冲突。
class ActionItemList(BaseModel):
    items: List[str]  # Pydantic 模型，用于结构化输出


def extract_action_items_llm(text: str) -> List[str]:
    """
    Extract action items from text using an LLM.
    Returns a list of extracted action items.
    """
    if not text.strip():
        return []

    prompt = f"""
    Extract all action items, tasks, and to-dos from the following text.
    Return them as a list of strings.
    If there are no action items, return an empty list.
    Remove any bullet points, checkboxes, or prefixes (like '- [ ]', 'TODO:', etc.) from the extracted items.

    Text:
    {text}
    """

    try:
        # AI-generated (TODO3): harden LLM JSON parsing and keep graceful fallback behavior.
        response = chat(
            model="llama3.1:8b",
            messages=[{"role": "user", "content": prompt}],
            format=ActionItemList.model_json_schema(),  # 结构化输出，让LLM返回严格匹配 schema 的 JSON。
            options={"temperature": 0.0},
        )

        result_dict = json.loads(response.message.content)
        items = result_dict.get("items", [])
        if not isinstance(items, list):
            return []
        return [str(item).strip() for item in items if str(item).strip()]
    except Exception as e:
        logger.warning("LLM extraction failed, fallback to heuristic extractor: %s", e)
        # Fallback to the heuristic method if LLM fails
        return extract_action_items(text)

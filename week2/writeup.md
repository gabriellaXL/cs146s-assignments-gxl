# Week 2 Write-up

Tip: To preview this markdown file

- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **guo xinlei** \
SUNet ID: **（SUNet ID）** \
Citations: **https://ollama.com/blog/structured-outputs, https://ollama.com/library**

This assignment took me about **4** hours to do.

## YOUR RESPONSES

For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature

Prompt:

```
在week2的作业中，TODO 1是：搭建一个新功能（Scaffold a New Feature）： 
 分析 `week2/app/services/extract.py` 中现有的 `extract_action_items()` 函数。它当前用预先定义的启发式规则（heuristics）来提取行动项。 
 你的任务是实现一个由 **LLM 驱动** 的替代方案 `extract_action_items_llm()`：使用 Ollama 通过大语言模型来做行动项提取。 
 一些提示： 
 - 如需输出结构化结果（例如 JSON 的字符串数组），参考文档：< `https://ollama.com/blog/structured-outputs>` 
 - 如需浏览可用的 Ollama 模型，参考文档：< `https://ollama.com/library。注意更大的模型会更耗资源，建议先从小模型开始。拉取并运行模型：` `ollama> run {MODEL\_NAME}\` 
 
 那么我现在要来完成TODO1,要求写一个extract_action_items_llm()函数，使用 Ollama 通过大语言模型来做行动项提取，输出是结构化的结果。

 你使用ollama来输出结构化结果了吗
 extract.py文件里有两个提取的函数，一个LLM提取、一个正则化提取，会冲突吗
 那我现在在网页使用到的是正则化提取函数呢还是LLM提取函数呢
```

Generated Code Snippets:

```
week2/app/services/extract.py
- Added Pydantic schema for structured output (`ActionItemList`): lines 95-97
- Added `extract_action_items_llm(...)` with Ollama structured output + fallback: lines 99-134
```

### Exercise 2: Add Unit Tests

Prompt:

```
完成TODO2
你读一下现在的test_extract.py，检查完成程度和质量如何，然后给出删除或修改或添加完善的意见
```

Generated Code Snippets:

```
week2/tests/test_extract.py
- Added unit tests for `extract_action_items_llm` using monkeypatch/mocked chat responses: lines 21-107
```

### Exercise 3: Refactor Existing Code for Clarity

Prompt:

```
做TODO3，按照要求，充分、全面、严谨地实现。并解释你所作的改动和效果

还记得完成TODO3时具体修改的地方吗？能不能在那些地方补充上注释，标明ai生成的具体代码段落
```

Generated/Modified Code Snippets:

```
week2/app/schemas.py
- Added typed request/response API contracts (Pydantic models): lines 1-49
- Added AI-generated marker comment for TODO3: line 8

week2/app/config.py
- Added centralized app settings model and loader: lines 1-21
- Added AI-generated marker comments for TODO3 sections: lines 8 and 16

week2/app/db.py
- Added database-layer custom exception (DatabaseError): lines 13-15
- Refactored connection/bootstrap with explicit FK pragma and guarded DB init: lines 21-62
- Wrapped CRUD operations with consistent sqlite error mapping: lines 64-145
- Changed mark_action_item_done(...) to return bool for 404 semantics: lines 134-145
- Added AI-generated marker comments on key TODO3 refactor blocks: lines 13, 22, 34, 135

week2/app/main.py
- Replaced import-time init_db() with FastAPI lifespan startup init: lines 20-24
- Added global DatabaseError exception handler for uniform 500 responses: lines 28-35
- Switched app/static/index path wiring to config-backed settings: lines 17, 25, 39, 47
- Added AI-generated marker comments on TODO3 blocks: lines 22 and 30

week2/app/routers/notes.py
- Migrated from Dict payloads to strict schemas for request/response: lines 6, 12-30
- Added stronger post-create consistency check and explicit HTTP behavior: lines 20-22
- Added AI-generated marker comments on TODO3 blocks: lines 14 and 27

week2/app/routers/action_items.py
- Migrated endpoints to schema-driven request/response contracts: lines 9-16, 22-60
- Added 404 behavior when marking non-existent action item as done: lines 57-60
- Added AI-generated marker comments on TODO3 blocks: lines 24, 42, 56

week2/app/services/extract.py
- Refactored imports and logging usage for cleaner error handling: lines 3-14
- Hardened LLM JSON parsing and normalized extracted list typing: lines 118-131
- Added AI-generated marker comment for TODO3 parsing/fallback block: line 118
```

### Exercise 4: Use Agentic Mode to Automate a Small Task

Prompt:

```
继续做TODO4

好的，继续把 writeup.md 里的 Exercise 4 部分也按这次真实改动直接补完整
```

Generated Code Snippets:

```
week2/app/routers/action_items.py
- Added a shared extraction helper `_extract_with(...)` to avoid duplicated persistence logic for multiple extraction modes: lines 22-39
- Kept existing heuristic endpoint and routed through shared helper: lines 42-45
- Added new LLM endpoint `POST /action-items/extract-llm` for frontend "Extract LLM" button: lines 48-51
- Imported `extract_action_items_llm` and `Callable` typing support for extractor injection: lines 3, 8

week2/app/routers/notes.py
- Added new endpoint `GET /notes` to list all notes for frontend "List Notes" button: lines 26-30

week2/frontend/index.html
- Added new buttons in UI: "Extract LLM" and "List Notes": lines 28-29
- Added dedicated notes display section: lines 34-35
- Refactored frontend JS to support two extraction paths via `runExtract(endpoint)`: lines 65-85
- Wired "Extract" to `/action-items/extract` and "Extract LLM" to `/action-items/extract-llm`: lines 84-85
- Implemented "List Notes" click handler to call `GET /notes` and render results: lines 87-104
```

### Exercise 5: Generate a README from the Codebase

Prompt:

```
把TODO5完成
@week2/README.md 再生成一版中文的、可以更详细
```

Generated Code Snippets:

```
README.md
```

## SUBMISSION INSTRUCTIONS

1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields.
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope.

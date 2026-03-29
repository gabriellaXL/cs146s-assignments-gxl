# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **gxl** \
SUNet ID: **** \
Citations: ****

This assignment took me about **4** hours to do. 


## Brief findings overview

**SAST（静态代码分析）**：Semgrep 在后端 Python 代码中共发现 8 条 SAST 安全告警，涵盖 SQL 注入、任意代码执行（eval）、命令注入（subprocess shell=True）、路径穿越（任意文件读取）、SSRF（动态 urllib）、弱加密（MD5）、CORS 过于宽松，以及前端 JavaScript 中 1 条 XSS（不安全的 innerHTML 写入）。

**Secrets**：本次扫描未报告任何 Secrets 类 finding（`week6/backend/app/services/extract.py` 中的硬编码 API Token 未被 CI 规则命中）。

**SCA（供应链/依赖分析）**：本次扫描未报告 SCA finding（`requirements.txt` 中的过时依赖未被命中）。

**已忽略的误报（False Positives）**：
- Finding IDs 734764973 / 734764972 / 734764970 / 734764969：Semgrep 将 `skip` 整数参数流入 `.offset()` 标记为 SQL 注入。实际上 FastAPI 的类型注解已将 `skip` 强制为 `int`，SQLAlchemy ORM 的 `.offset()` 对整数参数不存在注入风险，Semgrep 自身的分诊系统也将其 provisionally ignore，属于规则误报，已忽略。
- Finding ID 734764964（`subprocess-shell-true`）：该规则被 provisionally ignored，但同一位置的 `tainted-os-command` 规则（ID 734764965）仍为 Open True Positive，两者指向相同缺陷，实际漏洞存在，本次不在修复范围（选择了更高优先级的三个问题）。

## Fix #1
a. File and line(s)
> `week6/backend/app/routers/notes.py`, lines 69–92（修复后为 69–78）

b. Rule/category Semgrep flagged
> - `python.fastapi.db.sqlalchemy-fastapi.sqlalchemy-fastapi` (ID 734764968, Critical) — line 72：在 SQLAlchemy `text()` 中使用了用户输入
> - `python.fastapi.db.generic-sql-fastapi.generic-sql-fastapi` (ID 734764971, Critical) — line 80：不可信输入流入数据库查询执行点
> - `python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text` (ID 734764963, High) — line 71：使用了裸 `sqlalchemy.text()` 构造 SQL

c. Brief risk description
> `unsafe_search` 端点将查询参数 `q` 通过 Python f-string 直接拼入 SQL 字符串后传给 `text()` 执行。攻击者可以构造如 `q = ' OR '1'='1` 的输入绕过过滤条件，或注入 `; DROP TABLE notes;--` 等破坏性语句，从而实现未授权数据访问、数据篡改或删除。

d. Your change (short code diff or explanation, AI coding tool usage)
> 使用 Warp Oz AI 辅助完成修复。将整个函数体从裸 SQL 改写为 SQLAlchemy ORM 参数化查询，同时移除不再使用的 `text` import：
>
> ```diff
> -from sqlalchemy import asc, desc, select, text
> +from sqlalchemy import asc, desc, select
>
> -@router.get("/unsafe-search", response_model=list[NoteRead])
> -def unsafe_search(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:
> -    sql = text(
> -        f"""
> -        SELECT id, title, content, created_at, updated_at
> -        FROM notes
> -        WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
> -        ORDER BY created_at DESC
> -        LIMIT 50
> -        """
> -    )
> -    rows = db.execute(sql).all()
> -    results: list[NoteRead] = []
> -    for r in rows:
> -        results.append(
> -            NoteRead(
> -                id=r.id, title=r.title, content=r.content,
> -                created_at=r.created_at, updated_at=r.updated_at,
> -            )
> -        )
> -    return results
> +@router.get("/unsafe-search", response_model=list[NoteRead])
> +def unsafe_search(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:
> +    stmt = (
> +        select(Note)
> +        .where((Note.title.contains(q)) | (Note.content.contains(q)))
> +        .order_by(desc(Note.created_at))
> +        .limit(50)
> +    )
> +    rows = db.execute(stmt).scalars().all()
> +    return [NoteRead.model_validate(row) for row in rows]
> ```

e. Why this mitigates the issue
> SQLAlchemy ORM 的 `.contains()` 方法内部使用参数绑定（prepared statement）：用户输入 `q` 仅作为 `LIKE` 子句的绑定值传递给数据库驱动，永远不会被拼接进 SQL 字符串本身。无论 `q` 包含什么字符（引号、分号、SQL 关键词），数据库都将其视为纯文本数据而非 SQL 语法，从根本上切断了注入路径。同时移除了 `text()` 的使用，消除了绕过 ORM 安全层的可能性。

## Fix #2
a. File and line(s)
> `week6/backend/app/routers/notes.py`, line 89–91（修复后为 89–95）

b. Rule/category Semgrep flagged
> - `python.fastapi.code.tainted-code-stdlib-fastapi.tainted-code-stdlib-fastapi` (ID 734764974, Critical) — line 104（原始行号）：不可信输入流入 `eval()`，可导致任意代码执行
> - `python.lang.security.audit.eval-detected.eval-detected` (ID 734764960, Medium) — 同一行：检测到 `eval()` 使用

c. Brief risk description
> `/debug/eval` 端点将用户提供的 `expr` 参数直接传入 Python `eval()`。攻击者可传入如 `__import__('os').system('whoami')` 执行任意系统命令，或通过 `open('/etc/passwd').read()` 读取服务器敏感文件，获得对服务器的完全控制权。

d. Your change (short code diff or explanation, AI coding tool usage)
> 使用 Warp Oz AI 辅助完成修复。在文件顶部新增 `import ast`，将 `eval(expr)` 替换为 `ast.literal_eval(expr)`，并捕获异常返回 400：
>
> ```diff
> +import ast
>  from typing import Optional
>
>  @router.get("/debug/eval")
>  def debug_eval(expr: str) -> dict[str, str]:
> -    result = str(eval(expr))  # noqa: S307
> -    return {"result": result}
> +    try:
> +        result = str(ast.literal_eval(expr))
> +    except (ValueError, SyntaxError) as exc:
> +        raise HTTPException(status_code=400, detail=f"Invalid literal: {exc}")
> +    return {"result": result}
> ```

e. Why this mitigates the issue
> `ast.literal_eval()` 只能解析 Python 字面量（数字、字符串、列表、字典、布尔值、`None`），不执行任何函数调用、属性访问或任意表达式。即使攻击者传入 `__import__('os').system('id')`，`ast.literal_eval` 会直接抛出 `ValueError` 并返回 400，完全切断了代码执行路径，同时保留了对合法字面量的解析能力。

## Fix #3
a. File and line(s)
> `week6/frontend/app.js`, line 14（修复后为 14–17）

b. Rule/category Semgrep flagged
> - `javascript.browser.security.insecure-document-method.insecure-document-method` (ID 734764967, High) — line 14：用户可控数据写入 `innerHTML`，可导致 XSS

c. Brief risk description
> `loadNotes()` 将服务端返回的 `n.title` 和 `n.content` 直接通过模板字符串拼入 `innerHTML`。若攻击者在 Note 的 title 或 content 字段中存入 `<img src=x onerror=alert(document.cookie)>` 等 payload，页面渲染时浏览器会解析并执行该 HTML，导致任意 JavaScript 在其他用户浏览器中执行（存储型 XSS），可用于 cookie 盗取、页面劫持或钓鱼攻击。

d. Your change (short code diff or explanation, AI coding tool usage)
> 使用 Warp Oz AI 辅助完成修复。彻底弃用 `innerHTML`，改为用 DOM API 逐节点创建，所有用户数据均通过 `.textContent` 或 `createTextNode()` 写入：
>
> ```diff
>  for (const n of notes) {
>    const li = document.createElement('li');
> -  li.innerHTML = `<strong>${n.title}</strong>: ${n.content}`;
> +  const strong = document.createElement('strong');
> +  strong.textContent = n.title;
> +  li.appendChild(strong);
> +  li.appendChild(document.createTextNode(': ' + n.content));
>    list.appendChild(li);
>  }
> ```

e. Why this mitigates the issue
> `.textContent` 和 `createTextNode()` 将所有赋值内容视为纯文本，浏览器不会对其进行 HTML 解析。无论 `n.title` 或 `n.content` 包含何种 HTML 标签或事件属性，都会被转义显示为字面文本而非执行。与手动转义字符串相比，这种 DOM API 方式从根本上消除了 HTML 注入面，不依赖任何转义逻辑的正确性。

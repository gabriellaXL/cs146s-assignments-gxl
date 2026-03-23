toolName: view_files
            
status: success
          
            
filePath: c:\Users\gabri\Documents\cs146s\modern-software-dev-assignments-master\week2\assignment.md
          
# 第 2 周——行动项提取器（Action Item Extractor）

本周我们将在一个最小化的 FastAPI + SQLite 应用基础上继续扩展：它可以把自由格式的笔记转换为编号的行动项列表。

***建议在开始之前通读整份文档。***

提示：预览这个 markdown 文件
- Mac：按 `Command (⌘) + Shift + V`
- Windows/Linux：按 `Ctrl + Shift + V`

## 开始（Getting Started）

### Cursor 设置（Cursor Set Up）
按照以下说明设置 Cursor 并打开你的项目：
1. 领取免费的 1 年 Cursor Pro：https://cursor.com/students
2. 下载 Cursor：https://cursor.com/download
3. 启用 Cursor 命令行工具：打开 Cursor，Mac 用户按 `Command (⌘) + Shift + P`（非 Mac 用户按 `Ctrl + Shift + P`）打开 Command Palette（命令面板）。输入：`Shell Command: Install 'cursor' command`，选择后回车。
4. 打开一个新的终端窗口，进入项目根目录，运行：`cursor .`

### 当前应用（Current Application）
当前 starter 应用的启动方式：
1. 激活你的 conda 环境：
```
conda activate cs146s 
```
2. 在项目根目录运行服务器：
```
poetry run uvicorn week2.app.main:app --reload
```
3. 打开浏览器访问 http://127.0.0.1:8000/。
4. 熟悉应用当前状态。确保你能成功输入 notes（笔记），并生成提取出来的行动项清单（checklist）。

## 练习（Exercises）
对每个练习，使用 Cursor 来帮助你实现对当前“行动项提取器”应用的改进。

完成作业时，使用 `writeup.md` 记录你的进展。务必包含你使用的 prompts，以及你或 Cursor 做出的任何修改。评分将依据 write-up 的内容。另外也请在代码中到处加上注释来记录你的改动。

### TODO 1：搭建一个新功能（Scaffold a New Feature）
分析 `week2/app/services/extract.py` 中现有的 `extract_action_items()` 函数。它当前用预先定义的启发式规则（heuristics）来提取行动项。

你的任务是实现一个由 **LLM 驱动** 的替代方案 `extract_action_items_llm()`：使用 Ollama 通过大语言模型来做行动项提取。

一些提示：
- 如需输出结构化结果（例如 JSON 的字符串数组），参考文档：https://ollama.com/blog/structured-outputs
- 如需浏览可用的 Ollama 模型，参考文档：https://ollama.com/library。注意更大的模型会更耗资源，建议先从小模型开始。拉取并运行模型：`ollama run {MODEL_NAME}`

### TODO 2：添加单元测试（Add Unit Tests）
为 `extract_action_items_llm()` 编写单元测试，覆盖多种输入（例如：项目符号列表、以关键词开头的行、空输入），测试写在 `week2/tests/test_extract.py`。

### TODO 3：为清晰性重构现有代码（Refactor Existing Code for Clarity）
对后端代码进行重构，重点关注：清晰定义的 API 合约/Schema、数据库层清理、应用生命周期/配置、错误处理。

### TODO 4：使用 Agentic 模式自动化小任务（Use Agentic Mode to Automate Small Tasks）
1. 将 LLM 驱动的提取作为一个新 endpoint 集成进来。更新前端，添加 “Extract LLM” 按钮，点击后通过新 endpoint 触发提取流程。
2. 再暴露一个 endpoint 用于获取所有 notes。更新前端，添加 “List Notes” 按钮，点击后拉取并展示这些 notes。

### TODO 5：从代码库生成 README（Generate a README from the Codebase）
***学习目标：***
*让学生学习 AI 如何自我“审视”代码库并自动生成文档，展示 Cursor 解析代码上下文并将其转成易读文档的能力。*

使用 Cursor 分析当前代码库并生成结构清晰的 `README.md`。README 至少需要包含：
- 项目简介
- 如何安装与运行项目
- API endpoints 与功能说明
- 如何运行测试套件（test suite）的说明

## 交付物（Deliverables）
按说明填写 `week2/writeup.md`。确保你在代码库中的所有改动都有记录。

## 评分标准（Evaluation rubric，总分 100）
- 第 1–5 部分每部分 20 分（其中 10 分为生成的代码，10 分为每个 prompt）。
# Week 3 — Open-Meteo MCP Server（本地 STDIO）

本目录实现一个封装 [Open-Meteo](https://open-meteo.com/)（地理编码 + 实况天气）的 MCP 服务器，**无需 API Key**。

## 先决条件

- Python 3.10+
- 可访问公网的 HTTPS（调用 `geocoding-api.open-meteo.com` 与 `api.open-meteo.com`）

## 安装

在仓库根目录执行：

```bash
pip install -r week3/requirements.txt
```

## 运行（STDIO）

在仓库根目录：

```bash
python -m week3.server.main
```

服务器从标准输入读取 MCP 消息、向标准输出写入协议数据；**日志在 stderr**，请勿向 stdout 打印调试信息。

## 在 Cursor / Claude Desktop 中注册

将 `command` 换成你的 `python` 绝对路径（Windows 可用 `where python` 查看）。`args` 里第一项必须是本仓库根目录的**绝对路径**。

```json
{
  "mcpServers": {
    "openmeteo": {
      "command": "python",
      "args": [
        "-m",
        "week3.server.main"
      ],
      "cwd": "C:\\Users\\YOU\\Documents\\cs146s\\modern-software-dev-assignments-master"
    }
  }
}
```

- **Cursor**：在 MCP 设置里添加上述配置（或等价字段）。
- **Claude Desktop**：编辑 `claude_desktop_config.json`（Windows 一般在 `%AppData%\\Claude\\claude_desktop_config.json`），把 `cwd` 改成你的机器上的路径。

重启客户端后，应能看到名为 `openmeteo` 的服务器及下方工具。

## Tools 说明

| 名称 | 作用 | 主要参数 |
|------|------|----------|
| `search_place` | 地名搜索，返回候选地点与经纬度 | `name`：地名；`max_results`：1–10，默认 5 |
| `current_weather` | 按经纬度查询当前天气摘要 | `latitude`：-90～90；`longitude`：-180～180 |

**示例对话**：先调用 `search_place` 得到北京坐标，再将返回的纬度、经度传给 `current_weather`。

## 行为说明

- HTTP 超时、非 2xx、网络错误：工具返回可读错误说明，并写日志到 stderr。
- 遇到 HTTP 429：简单退避后重试（最多 3 次）。
- 无匹配地名或空数据：返回明确提示，不抛未捕获异常。

## 外部 API

- 地理编码：`GET https://geocoding-api.open-meteo.com/v1/search`
- 预报/当前：`GET https://api.open-meteo.com/v1/forecast`（使用 `current` 变量）

文档：<https://open-meteo.com/en/docs>

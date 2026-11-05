---
date: 2026-07-25
description: "Antigravity / Gemini CLI 環境での MCP クライアント定義 — ~/.gemini/settings.json の mcpServers ブロックと設定ファイル階層"
tags:
  - reference
  - mcp
  - antigravity
---

Antigravity / Gemini 開発環境における **MCP（Model Context Protocol）クライアント** の定義と設定場所について説明します。

---

### 1. 定義・接続の設定場所
MCP サーバー（クライアントが接続・利用するツール群）の設定は、**ユーザー設定ファイル (`mcpServers` ブロック)** 内に定義します。

* **グローバル設定ファイル**:
  `C:\Users\ykomi\.gemini\settings.json`

  このファイル内の `mcpServers` 項目に、利用する MCP サーバーの起動コマンドや URL を定義します。

  **定義例 (`settings.json`)**:
  ```json
  {
    "mcpServers": {
      "gemini-api-docs-mcp": {
        "type": "http",
        "url": "https://gemini-api-docs-mcp.dev"
      },
      "agentmemory": {
        "command": "npx",
        "args": [
          "-y",
          "@agentmemory/mcp"
        ],
        "env": {
          "AGENTMEMORY_URL": "http://localhost:3111"
        }
      }
    }
  }
  ```

---

### 2. 誰が「MCP クライアント」として動作するのか？
Antigravity システムにおいては、**Antigravity 実行本体（CLI / IDE / エージェントランタイム）が MCP クライアントとして機能**します。

1. **Antigravity CLI / IDE 起動時**:
   設定ファイル（`~/.gemini/settings.json`）の `mcpServers` を読み込みます。
2. **MCP サーバーとのハンドシェイク**:
   定義されたコマンド（`npx` 等）を実行して MCP サーバーをローカルプロセスとして起動するか、指定の HTTP URL に接続します。
3. **ツールの登録と利用**:
   MCP サーバーから提供されるツール群を認識し、AI エージェントが利用できるツールとして動的に追加・実行します。

---

### 3. 設定ファイルの場所一覧まとめ

| 設定対象         | ファイルパス                                    | 役割                            |
| :----------- | :---------------------------------------- | :---------------------------- |
| **全体/MCP設定** | `~/.gemini/settings.json`                 | `mcpServers` やフック（Hooks）などの定義 |
| **CLI個別設定**  | `~/.gemini/antigravity-cli/settings.json` | 権限、モデル選択、ワークスペース設定など          |
| **プロジェクト個別** | (各プロジェクトルート)/`.gemini/settings.json`      | プロジェクト固有の MCP サーバーや設定         |

---

### 4. 実機確認（2026-07-26）

`~/.gemini/settings.json` の `mcpServers` に実際に登録されているのは `agentmemory`（`npx -y @agentmemory/mcp`）と `gemini-docs`（`uvx --from git+https://github.com/philschmid/gemini-api-docs-mcp`）の2件。上記の定義例は URL 型で書いているが、実設定は両方ともコマンド起動（Stdio）型。

一方 [[MCP Server使用方法]] が説明している IDE 側の `~/.gemini/antigravity/mcp_config.json` は**空ファイル**だった。つまり CLI 系（`settings.json`）と IDE 系（`mcp_config.json`）は別系統で、現状 MCP が効いているのは CLI 側のみ。

## Related

- [[MCP Server使用方法]] — Antigravity IDE 側（UI / `mcp_config.json`）からの設定手順
- [[MCP-LIST]] — MCP サーバー候補一覧
- [[Antigravity-CLI-skills]] — Antigravity CLI のスキル分類

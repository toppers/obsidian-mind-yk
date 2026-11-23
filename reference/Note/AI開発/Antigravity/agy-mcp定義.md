---
date: 2026-07-25
description: "Gemini CLI の MCP 定義（~/.gemini/settings.json の mcpServers）と設定ファイル階層。agy は settings.json を参照せず ~/.gemini/config/mcp_config.json とされる（2026-11-23訂正、未検証）"
tags:
  - reference
  - mcp
  - antigravity
---

Antigravity / Gemini 開発環境における **MCP（Model Context Protocol）クライアント** の定義と設定場所について説明します。

> [!warning] 訂正（2026-11-23、未検証）
> 以下の `~/.gemini/settings.json` は **gemini-cli** が参照する設定ファイルで、**agy（Antigravity CLI）は参照しません**。agy 側の MCP 設定は `~/.gemini/config/mcp_config.json` とされます（[[agy-設定ファイルの読み込み]]）。根拠は、agy を起動して中の Gemini に確認した回答です（実機での再現・公式ドキュメントとの照合はしていません）。下の本文のうち、`settings.json` を agy の設定として述べた箇所は、この訂正に従って読み替えてください。

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
   設定ファイルの `mcpServers` を読み込みます（`~/.gemini/settings.json` は gemini-cli の場合。agy は `~/.gemini/config/mcp_config.json`、2026-11-23訂正・未検証）。
2. **MCP サーバーとのハンドシェイク**:
   定義されたコマンド（`npx` 等）を実行して MCP サーバーをローカルプロセスとして起動するか、指定の HTTP URL に接続します。
3. **ツールの登録と利用**:
   MCP サーバーから提供されるツール群を認識し、AI エージェントが利用できるツールとして動的に追加・実行します。

---

### 3. 設定ファイルの場所一覧まとめ

| 設定対象         | ファイルパス                                    | 役割                            |
| :----------- | :---------------------------------------- | :---------------------------- |
| **全体/MCP設定（gemini-cli 用）** | `~/.gemini/settings.json`                 | `mcpServers` やフック（Hooks）などの定義。agy は参照しない（2026-11-23訂正・未検証） |
| **CLI個別設定**  | `~/.gemini/antigravity-cli/settings.json` | 権限、モデル選択、ワークスペース設定など          |
| **プロジェクト個別** | (各プロジェクトルート)/`.gemini/settings.json`      | プロジェクト固有の MCP サーバーや設定         |

---

### 4. 実機確認（2026-07-26）

`~/.gemini/settings.json` の `mcpServers` に実際に登録されているのは `agentmemory`（`npx -y @agentmemory/mcp`）と `gemini-docs`（`uvx --from git+https://github.com/philschmid/gemini-api-docs-mcp`）の2件。上記の定義例は URL 型で書いているが、実設定は両方ともコマンド起動（Stdio）型。

一方 [[MCP Server使用方法]] が説明している IDE 側の `~/.gemini/antigravity/mcp_config.json` は**空ファイル**だった。つまり `settings.json`（gemini-cli 系）と IDE 系（`mcp_config.json`）は別系統で、2026-07-26 時点で MCP が登録されていたのは `settings.json` 側のみ。（2026-11-23訂正: この `settings.json` は gemini-cli のもので、agy が使うかのような当初の読みは誤り。agy の MCP 設定の中身〔`~/.gemini/config/mcp_config.json`〕は未確認。）

## Related

- [[MCP Server使用方法]] — Antigravity IDE 側（UI / `mcp_config.json`）からの設定手順
- [[MCP-LIST]] — MCP サーバー候補一覧
- [[Antigravity-CLI-skills]] — Antigravity CLI のスキル分類
- [[agy-設定ファイルの読み込み]] — agy が起動時に読む設定・ルール・スキル・フックの一覧（未検証。agy の MCP は `~/.gemini/config/mcp_config.json`）

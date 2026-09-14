---
date: 2026-08-17
description: "headroom をAPIプロキシとして使う実行例（Claude Code / OpenAI互換クライアント / Codex）"
tags:
  - work-note
---

⚠ Skill descriptions were shortened to fit the skills context budget. Codex can still see every skill, but some descriptions are
  shorter. Disable unused skills or plugins to leave more room for the rest.

• SSOT.md と現在のローカル設定を確認し、headroom をプロキシとして使う実行例に絞って回答します。

• Started `/root/headroom_proxy_research`

• Started `/root/headroom_proxy_research`

• Ran rtk read SSOT.md
  └ SSOT_PROJECT_DECISION_DIR: <SSOT_DECISION_DIR>/01_DECISIONS/<project_name>
    SSOT_LOG_PROJECT_DIR:      <SSOT_DECISION_DIR>/10_DAILY/<project_name>
    … +101 lines (ctrl + t to view transcript)
    the
         | spelling of the name, or if a path was included, verify that the path is correct and try again.

• Ran rtk proxy rg -n "headroom|proxy" C:\Users\ykomi\.codex\memories\MEMORY.md
  └ 189:- export-skills-csv, skills_list.csv, skill名, skillの説明, skillのSKILL.mdのフルパス, PowerShell, rtk proxy, UTF-8 without
    BOM, SKILL.md, YAML description, Rows=131
    … +47 lines (ctrl + t to view transcript)
    the
         | spelling of the name, or if a path was included, verify that the path is correct and try again.

• Running rtk proxy headroom.exe proxy --help

• Running rtk proxy headroom.exe --version

• Ran rtk proxy rg -n "headroom|base_url|OPENAI_BASE_URL" .
  └ Set-PsFzfOption: C:\Users\ykomi\OneDrive\Documents\PowerShell\Microsoft.PowerShell_profile.ps1:6
    Line |
    … +10 lines (ctrl + t to view transcript)
    the
         | spelling of the name, or if a path was included, verify that the path is correct and try again.

• Ran rtk proxy headroom.exe proxy --help
  └ Usage: headroom proxy [OPTIONS]

    … +264 lines (ctrl + t to view transcript)
                                      HEADROOM_EMBEDDING_SERVER_SOCKET)
      -?, --help                      Show this message and exit.

• Ran rtk proxy headroom.exe --version
  └ headroom, version 0.27.0

• Waiting for agents

• Finished waiting
  └ No agents completed yet

• Waiting for agents

• Finished waiting
  └ No agents completed yet

• Interacted with `/root/headroom_proxy_research`

• Interacted with `/root/headroom_proxy_research`

• Waiting for agents

• Finished waiting
  └ No agents completed yet

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Headroom 0.27.0では、別ターミナルでプロキシを起動し、AIクライアントの接続先を localhost:8787 に変更します。

  rtk proxy headroom.exe proxy

  Claude Codeから使う場合:

  $env:ANTHROPIC_BASE_URL = "http://127.0.0.1:8787"
  rtk proxy claude

  OpenAI互換クライアントから使う場合:

  $env:OPENAI_BASE_URL = "http://127.0.0.1:8787/v1"
  rtk proxy <利用するコマンド>

  Codexでは、C:\Users\ykomi\.codex\config.toml に既にHeadroom用テンプレートがあります。次のコメントを外して有効化します。

  model_provider = "headroom"

  [model_providers.headroom]
  name = "OpenAI via Headroom proxy"
  base_url = "http://127.0.0.1:8787/v1"
  supports_websockets = true

  [model_providers.headroom.env_http_headers]
  X-Headroom-Project = "HEADROOM_PROJECT"

  設定後にCodexを再起動します。自動設定する場合は次です。

  rtk proxy headroom.exe init codex

  疎通だけ確認する場合は、最適化を無効にできます。

  rtk proxy headroom.exe proxy --no-optimize

  なお、mcp_servers.headroom はHeadroomのMCP機能であり、今回のAPIプロキシとは別設定です。

─ Worked for 3m 10s ────────────────────────────────────────────────────────────────────────────────────────────────────────────────

## Related
- [[headroom-index]]

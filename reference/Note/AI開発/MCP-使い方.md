---
date: 2026-09-28
description: "Codex CLI で有効な MCP サーバーを尋ねた際の回答の貼り付け（2026-09-28）。セッションに公開された6件と、config.toml に登録済みだが未公開の4件（headroom・cce-ghrepo 等）の区別"
tags:
  - reference
  - mcp
  - codex-cli
---

headroom
cce-ghrepo-c2aad4
=======
• このセッションでツールが公開されているMCPサーバーは agentmemory、node_repl、om、qmd、semble、serena です。GitHub・Google Drive・Figmaなどの連
  携ツールも codex_apps 経由で利用できます。

  Codexの設定 (/C:/Users/ykomi/.codex/config.toml)には、上記に加えて cce-ghrepo-c2aad4、headroom、mcp-mermaid、codegraph も有効として登録されて
  います。ただし、この4件のツールは現在のセッションには公開されていないため、接続状態までは確認できていません。

↳ Hook · Session end checklist:
    - Archive completed projects? (work/active/ -> work/archive/YYYY/)
    - Update indexes? (Index.md, Memories.md, People & Context, Brag Doc)
    - New notes linked? (orphans are bugs)
    - Run /om-vault-audit if many notes were created/modified

• Hook failed
  └ hook exited with code 1


## Related
- [[reference/Note/AI開発/codex-cli/mcp|codex-cli/mcp]] — Codex CLI の MCP 設定
- [[Claude-MCP-Tool一覧]] — Claude Code 側の MCP ツール一覧
- [[Gotchas - Tooling & Config]] — headroom MCP 登録の gotcha

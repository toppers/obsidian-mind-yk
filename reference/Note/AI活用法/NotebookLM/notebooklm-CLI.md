---
date: 2026-09-08
description: "notebooklm コマンド（teng-lin/notebooklm-py、tmc/nlm とは別ツール）のトップレベル --help リファレンス。session/notebook/chat とコマンドグループ・artifact生成の一覧。"
tags:
  - reference
  - notebooklm
  - cli
---

# notebooklm — CLI リファレンス

> `notebooklm --help` の出力（2026-09-08 取得）。ツールは `teng-lin/notebooklm-py`。`nlm`（[[nlm-CLI]]、tmc/nlm）とは別の CLI で、両者は**併用**する方針（[[notebooklmclix]]）。

## グローバルオプション

| オプション | 用途 |
|-----------|------|
| `--version` | バージョン表示 |
| `--storage PATH` | `storage_state.json` のパス（既定: `~/.notebooklm/profiles/<profile>/storage_state.json`） |
| `-p, --profile TEXT` | プロファイル名（既定: config または `default`） |
| `-v, --verbose` | 冗長化（`-v`=INFO, `-vv`=DEBUG） |
| `--quiet` | status/INFO/WARN を抑制（error のみ）。`-v/-vv` と排他 |

**Tip**: notebook ID は部分一致可（`notebooklm use abc` が `abc123...` にマッチ）。

## クイックスタート

```bash
notebooklm login              # 先に認証
notebooklm list               # ノートブック一覧
notebooklm create "My Notes"  # ノートブック作成
notebooklm ask "Hi"           # 現在のノートブックに質問
```

## Session

| コマンド | 用途 |
|---------|------|
| `login` | ブラウザ経由で NotebookLM にログイン |
| `use` | 現在のノートブックコンテキストを設定 |
| `status` | 現在のコンテキスト（アクティブなノートブックと会話）を表示 |
| `clear` | 現在のノートブックコンテキストをクリア |
| `doctor` | プロファイル設定・認証状態・マイグレーションを確認 |
| `auth` | 認証管理コマンド |
| `completion` | SHELL 用のシェル補完スクリプトを出力 |

## Notebooks

| コマンド | 用途 |
|---------|------|
| `list` | 全ノートブックを一覧 |
| `create` | ノートブック作成 |
| `delete` | ノートブック削除 |
| `rename` | ノートブック名変更 |
| `summary` | AI 生成インサイト付きのノートブックサマリー |
| `metadata` | ソース一覧を含むノートブックメタデータをエクスポート |

## Chat

| コマンド | 用途 |
|---------|------|
| `ask` | ノートブックに質問 |
| `suggest-prompts` | AI 推奨プロンプトを取得 |
| `configure` | チャットのペルソナ・応答設定 |
| `history` | 会話履歴の取得、またはノートとして保存 |

## コマンドグループ（`notebooklm <group> <command>`）

| グループ | サブコマンド |
|---------|-------------|
| `source` | add, add-drive, add-drive-file, add-research, clean, delete, delete-by-title, fulltext, get, guide, list, refresh, rename, stale, wait |
| `artifact` | delete, export, get, get-prompt, list, poll, rename, retry, suggestions, wait |
| `note` | create, delete, get, list, rename, save |
| `label` | add, create, delete, emoji, generate, list, remove, rename, sources |
| `collection` | add, create, delete, list, notebooks, remove, rename |
| `share` | add, public, remove, status, update, view-level |
| `research` | cancel, import, status, wait |
| `profile` | create, delete, list, rename, switch |
| `agent` | show |
| `skill` | install, package, show, status, uninstall |
| `language` | get, list, set |
| `mcp` | install |

## Artifact アクション（`notebooklm <action> <type>`）

| アクション | type |
|-----------|------|
| `generate` | audio, cinematic-video, data-table, flashcards, infographic, mind-map, quiz, report, revise-slide, slide-deck, video |
| `download` | audio, cinematic-video, data-table, flashcards, infographic, mind-map, quiz, report, slide-deck, video |

## 関連

- [[_NotebookLM-まとめ]]
- [[nlm-CLI]] — 別実装（tmc/nlm）。乗り換えではなく併用する
- [[notebooklmclix]] — NotebookLMソース管理システムの作業ノート（バックエンドCLI候補）

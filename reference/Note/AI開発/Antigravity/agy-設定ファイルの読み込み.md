---
date: 2026-11-23
description: "Antigravity CLI（agy）が起動時に読み込む設定・ルール・スキル・プラグイン・フックの場所と、優先順位・段階的読み込み・24KB／20,000トークン上限のメモ（出典の回答は未検証）"
tags:
  - reference
  - antigravity
  - agy
---

# agy が起動時に読み込むファイル

> [!warning] 未検証（unverified）
> 本文は、他のAI（出典未記録）が答えた説明の貼り付けで、実機・公式ドキュメントでの確認はしていません（2026-11-23 時点）。使う前に実機で確認します。
>
> MCP の設定場所は、既存の [[agy-mcp定義]]（`~/.gemini/settings.json`）と食い違っていましたが、agy を起動して中の Gemini に確認したところ、`~/.gemini/settings.json` は gemini-cli が参照する設定ファイルで、agy は参照しないとのことでした（2026-11-23、ユーザー確認。この回答自体も AI のもので、未検証）。本ノートの記載（`~/.gemini/config/mcp_config.json`）と整合するため、[[agy-mcp定義]] 側を訂正済みです。

読み込み対象は、CLI 本体の設定、ワークスペース配下、グローバル配下の3系統です。Windows では `~` が `C:\Users\<ユーザー名>` です。

## 1. CLI 本体の設定

| ファイル | 役割 |
|---|---|
| `~/.gemini/antigravity-cli/settings.json` | CLI の全体設定（モデル、権限設定など） |
| `~/.gemini/config/config.json` | プラグインの有効／無効状態など |

## 2. ワークスペース（プロジェクト）配下

現在の作業ディレクトリ（CWD）から、リポジトリルート（`.git` のある階層）まで親を遡って自動探索します。カスタマイズ用ディレクトリは `.agents/`（ほか `.agent/`・`_agents/`・`_agent/`）です。

- **ルール**: 各階層の `GEMINI.md`／`AGENTS.md`、`.agents/rules/*.md`、`.agents/rules.json`
- **スキル**: `.agents/skills/<name>/SKILL.md`、`.agents/skills.json`（別ディレクトリのスキルの参照・継承用）
- **プラグイン**: `.agents/plugins/<name>/plugin.json`（有効なとき、配下の `rules/`・`skills/*/SKILL.md`・`hooks.json`・`mcp_config.json` も読む）、`.agents/plugins.json`
- **ライフサイクルフック**: `.agents/hooks.json`（`SessionStart` など）

## 3. グローバル（マシン共通）配下

`~/.gemini/config/`（および `~/.gemini/`）の中身が、全プロジェクト共通で読み込まれます。

- **ルール**: `~/.gemini/GEMINI.md`、`~/.gemini/config/AGENTS.md`、`~/.gemini/config/rules/*.md`
- **MCP サーバー設定**: `~/.gemini/config/mcp_config.json`
- **スキル**: `~/.gemini/config/skills/<name>/SKILL.md`、`~/.gemini/config/skills.json`
- **プラグイン**: `~/.gemini/config/plugins/<name>/plugin.json`、`~/.gemini/config/plugins.json`
- **フック**: `~/.gemini/config/hooks.json`

`~/.gemini/antigravity-cli/builtin/` の組み込みスキル・プラグインもマウントされます。

## 4. 優先順位と挙動

優先順位（高い順）:

1. ワークスペースの自動探索（CWD → リポジトリルート）
2. ワークスペースの宣言ファイル（`skills.json`／`plugins.json`）
3. グローバルの自動探索（`~/.gemini/config/`）
4. 組み込みカスタマイズ（Built-in）
5. グローバルの宣言ファイル

段階的読み込み（Progressive Disclosure）:

- `SKILL.md` は、起動時に `name` と `description` だけがコンテキストに入り、本文は使うと判断されたときに読み込まれます。
- `GEMINI.md`／`AGENTS.md` と `always_on` のルールは常時読み込まれ、条件付きルールは該当時だけ読み込まれます。

上限と重複排除:

- パス解決後に重複排除されます（同じファイルは二重に読み込まれません）。
- ルールは1ファイル 24KB まで、常時ルール全体で 20,000 トークンの予算です。超えた分は、ファイルパスの参照に降格されます。

## Related

- [[agy-mcp定義]] — MCP クライアントの定義場所（gemini-cli 用の `settings.json`。agy の MCP は本ノートの `~/.gemini/config/mcp_config.json`、2026-11-23 に訂正済み）
- [[MCP Server使用方法]] — Antigravity IDE 側の MCP 設定手順
- [[Antigravity-CLI-skills]] — スキルの配置場所（Workspace / Global / Shared）の分類

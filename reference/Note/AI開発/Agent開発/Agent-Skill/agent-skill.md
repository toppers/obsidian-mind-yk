---
date: 2026-08-09
description: "Agent Memory関連ツール調査メモと、独自スキル群（class-internal-spec-to-code等）の要否判定O/Xリスト"
tags:
  - reference
  - ai
  - agents
---

# Agent Skill 調査メモ

> 関連: [[AI-Agents|AI エージェント]] / [[agent-skill-2|Agent Skill 分割マッピング表]] / [[skill-cleaner]]

TencentCloud/TencentDB-Agent-Memory

フレームワーク
LangChain

O
class-internal-spec-to-code
class-external-spec-to-code
class-internal-spec-to-external-spec | 外部ファイル読み込み
forward-gen-cli-external-spec

external-spec-contradiction-check

X
cli-internal-spec | 外部コマンド定義からCLIの内部仕様書生成
external-spec-notation-check
gen-external-spec-index
gen-external-spec-workspace
gen-internal-spec-index
gen-internal-spec-workspace
internal-spec-to-code
python-cli-idea-to-req-detail
python-cli-internal-spec
python-cli-req-to-external-spec
reverse-gen-internal-spec
spec-to-code-workspace
=
debug-ruff-mypy
export-skill-csv

=
github-project-jp-wiki
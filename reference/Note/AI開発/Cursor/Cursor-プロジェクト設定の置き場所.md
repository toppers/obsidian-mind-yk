---
date: 2026-09-10
description: "Cursor のプロジェクト単位設定の置き場所 — .vscode/settings.json（エディタ）、.cursor/rules/*.mdc・.cursor/skills/・.cursorignore・AGENTS.md（AI）。ワークスペース設定が User Settings より優先。"
tags:
  - reference
  - cursor
  - config
---

# Cursor — プロジェクト設定の置き場所

プロジェクト単位で設定を置く場所は**役割で分かれる**。ユーザー全体の設定（`%APPDATA%\Cursor\User\settings.json`）より**ワークスペース側が優先**される。関連スキル/MCP の控えは [[cursor-skills]]。

## エディタ設定（フォント・保存時フォーマットなど）

リポジトリ直下に `.vscode/settings.json`。Cursor は VS Code と同じワークスペース設定を読む。

- チームで共有するなら git に入れる。自分だけなら User Settings のままで十分
- 例: タブ幅、format on save、Python インタープリタパス

## AI 向けのプロジェクト指示

| 置き場所 | 用途 |
|----------|------|
| `AGENTS.md` | エージェント向けのプロジェクト概要・制約（[[AIエージェントに対する指示]] と同系の役割） |
| `.cursor/rules/*.mdc` | ルール。`alwaysApply: true` で常時、`globs` で特定ファイルだけ |
| `.cursor/skills/` | プロジェクト専用スキル |
| `.cursorignore` | インデックス／コンテキストから外すパス |

### ルール例（`.cursor/rules/*.mdc`）

```
---
description: Python の変更範囲を守る
globs: src/**/*.py
alwaysApply: false
---
指示されたファイル以外は編集しない。
```

### リポジトリに既にあるもの（例）

- `AGENTS.md` … プロジェクト案内
- `.cursor/hooks.json` … フック
- `.cursor/skills/` … スキル
- `.cursor/learning/` … 学習テレメトリ（通常は gitignore。設定ではない）

## 置き分けの目安

| 対象 | 置き場所 |
|------|----------|
| 全プロジェクト共通 | Cursor の User Settings |
| このリポの編集体験（タブ幅、format on save、Python パス） | `.vscode/settings.json` |
| このリポの AI の振る舞い | `AGENTS.md` と `.cursor/rules/` |
| 秘密・個人の MCP / API キー | ユーザー側。リポに置かない |

## Related

- [[cursor-skills]] — Cursor で使えるスキル/MCP サーバの控え
- [[AIエージェントに対する指示]] — AGENTS.md 系のエージェント指示ファイルの考え方

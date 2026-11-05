---
date: 2026-05-23
description: "Claude Code でスキル・サブエージェントに使用するモデルを指定する方法 — フロントマター・環境変数・起動フラグの3方式"
tags:
  - reference
  - claude-code
  - skills
---

# Claude Code スキルのモデル指定

スキルやサブエージェントで使用モデルを変える主要な方法。

## 方法まとめ

| 方法 | 設定場所 | スコープ |
|------|---------|---------|
| フロントマター `model:` | スキル `.md` ファイル | そのスキル限定 |
| 環境変数 `CLAUDE_CODE_SUBAGENT_MODEL` | OS 環境変数 | 全スキル・subagent |
| セッションコマンド `/model` | インタラクティブ | セッション全体 |
| 起動フラグ `--model` | `claude --model opus` | そのセッション |

## フロントマターで指定（推奨）

`.claude/commands/<skill>.md` または `.claude/skills/<skill>/SKILL.md` の YAML フロントマターに `model` を追加：

```yaml
---
name: analyze-deep
description: 深い分析スキル
model: claude-opus-4-7
---
```

このスキルだけ Opus で実行される。

## モデル ID

- **Opus 4.7**: `claude-opus-4-7`
- **Sonnet 4.6**: `claude-sonnet-4-6`
- **Haiku 4.5**: `claude-haiku-4-5-20251001`

## Tip

特定スキルだけ重い推論が必要な場合は `effort: xhigh` も合わせて指定すると効果的。

## 関連

- [[Claude Code スキル]] — スキルの作成・管理全般
- [[Claude-Code-教科書]] — Claude Code の包括的な参照
- [[brain/Skills]] — vault 内カスタムスラッシュコマンド一覧

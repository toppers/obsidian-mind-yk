---
date: 2026-10-09
description: "steipete/agent-scripts の skill-cleaner(スキル棚卸しツール)の参照元URLと実行コマンド例。ローカルにも skill-cleaner スキルとして導入済み"
tags:
  - reference
  - ai
  - agents
  - skill
---

# skill-cleaner

> 関連: [[agent-skill|Agent Skill 調査メモ]] / [[report-skill-cleaner|skill-cleaner 実行時の生出力(2026-07-20)]]

## 参照元

- [agent-scripts/skills/skill-cleaner/SKILL.md (steipete/agent-scripts)](https://github.com/steipete/agent-scripts/blob/main/skills/skill-cleaner/SKILL.md)
- スキル一覧上の説明: 「Codex/OpenClaw skill audit: live budget, usage, duplicates, compact descriptions.」(スキルの予算・使用状況・重複・説明文の圧縮を監査する)

## 実行コマンド例

リポジトリ側のパス `skills/skill-cleaner/scripts/skill-cleaner.ts` を Node で直接実行します。以下は 2026-10-09 にメモしたコマンドです(オプションの意味は未検証。(inferred) は名前からの推測)。

```bash
# ログ解析なしで実行
node --experimental-strip-types skills/skill-cleaner/scripts/skill-cleaner.ts --no-logs

# ライブ(現在読み込まれているスキル)の確認もログ解析もなし (inferred)
node --experimental-strip-types skills/skill-cleaner/scripts/skill-cleaner.ts --no-live --no-logs

# 直近6か月・ログ上限800MB・ログを深く解析 (inferred)
node --experimental-strip-types skills/skill-cleaner/scripts/skill-cleaner.ts --months 6 --max-log-mb 800 --deep-logs

# コンテキスト長272000トークン・予算2% を指定 (inferred)
node --experimental-strip-types skills/skill-cleaner/scripts/skill-cleaner.ts --context-tokens 272000 --budget-percent 2 --no-logs

# 対象ルートを指定
node --experimental-strip-types skills/skill-cleaner/scripts/skill-cleaner.ts --root ~/Dropbox/boxd/skills --no-logs
node --experimental-strip-types skills/skill-cleaner/scripts/skill-cleaner.ts --root ~/.agents/skills --root-only --no-logs
```

## 使いどころ

- 自作スキルの要否判定(O/X リスト)は [[agent-skill]] にあります。skill-cleaner は使用実績・重複・説明文の長さ(コンテキスト予算)の面から、その判定を裏付ける材料になります (inferred)。
- 実行結果の生出力の例は [[report-skill-cleaner]] を参照してください。

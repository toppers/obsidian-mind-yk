---
date: 2026-07-07
description: "記憶の正本を巡る運用監査メモ。Claude project memory・Codex memories・vault brain/・beads・PMB の並存、vault の AGENTS.md 削除＋AGENTS_2.md 未追跡で Codex の読み込み入口が壊れる件、削除候補ファイル"
tags:
  - reference
  - obsidian
  - claude-code
  - audit
---

PostToolUse
=====
• 1. 全体評価
  読み取り専用で確認しました。全体として、Obsidian vault を正本に寄せる設計はありますが、実態は Claude project memory、
  Codex memories、vault brain/、beads、PMB が並存しており、「正本はどこか」が運用上まだ揺れています。特に vault 側の
  AGENTS.md が削除状態で AGENTS_2.md が未追跡、かつ CLAUDE.md は root に AGENTS.md がある前提なので、エージェント別の読
  み込み入口が壊れやすい状態です。

  2. 最も危ない運用上の問題
  最重要は「記憶の正本ルールと実ファイルが矛盾していること」です。

  C:\0-MD-2\_ARCHIVE\ObsidianVault2\0-MD-2\.claude\memory-template.md と vault CLAUDE.md は、Claude project memory は
  MEMORY.md だけ、耐久記憶は brain/ としています。一方で実際には C:\Users\ykomi\.claude\projects\E--Ccur-
  python3\memory\work-asset-map.md や project_skill_*.md 系が残っています。これは確認待ち・正式記憶・移行メモが混ざるリ
  スクが高いです。

  加えて git status では vault 側が D AGENTS.md、?? AGENTS_2.md でした。Codex は AGENTS.md を読む前提なので、このままだ
  と Codex向け運用規約が想定通り読まれない可能性があります。

Claude project memory
Codex memories
vault brain/
beads
PMB

CLAUDE.md(@AGENTS.md)
X AGENTS.md
AGENTS_2.md

削除
C:\Users\ykomi\.claude\projects\E--Ccur-python3\memory\work-asset-map.md
project_skill_*.md 

## Related

- [[Claude Code クロス調査結果]]
- [[ops-prompt]]
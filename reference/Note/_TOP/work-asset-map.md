---
date: 2026-07-05
name: work-asset-map
description: ykominamiの仕事資産の所在マップと2026-07-05運用レビューの未決事項
tags:
  - reference
  - ops-audit
metadata: 
  node_type: memory
  type: reference
  originSessionId: 2432e685-04d8-43e0-aef5-c5480d60f99f
---

仕事資産の所在（2026-07-05時点）:
- 稼働中Obsidian vault: `C:\0-MD-2\_ARCHIVE\ObsidianVault2\0-MD-2`（_ARCHIVE配下だが現役。git remote: github.com/ykominami/obsidian-mind、**private**）
- 外側ツリー `C:\0-MD-2` はGoogle Drive同期（.tmp.driveupload あり）。`_CREDENTIIAL\pass.txt` は2026-07-05に本人が削除済み
- vaultが_ARCHIVE配下なのは**意図的**（本人確認済み 2026-07-05）。obsidian-mindの雇用者向け機能も今後使う予定あり（剪定不要）
- グローバルルール: `~/.claude/CLAUDE.md`（Karpathy+PMB+テスト規律）と `~/.codex/AGENTS.md`（基本部のみ）— 同内容の重複でドリフト済み
- RTK正本: `~/.agents/RTK.md`（.claude/.codex両方からsymlink）
- 記憶系統が5+並存: PMB / beads(bd remember) / vault brain\/ / codex memories / agentmemory skills / serena
- **正本ルール決定（2026-07-05）**: 決定・教訓は vault brain/ が正本、beads はタスクのみ、PMB は補助
- 月次棚卸しは未着手（本人回答）。週次(om-weekly)と四半期クローズの間のギャップとして今後整備対象
- claude.ai側（2026-07-05監査）: Projects 20件は指示文・ナレッジ皆無で自動メモリーのみ。Web Skills 23件（自作9: python-cli-tool, asset-audit, single-file-site, gas-script, group-dining-plan, cc-env, google-oauth-ruby, gpg-agent-ssh, oss-research）。cc-env=Claude Code環境知識の正本がWeb側のみに存在。folder-classify仕様はObsidian未退避（消失リスク）

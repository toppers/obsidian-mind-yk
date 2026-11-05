---
date: 2026-06-04
description: "llm-wiki CLIの設定・コマンドリファレンスと使用メモ"
tags:
  - reference
---

# llm-wiki MEMO

## 設定ファイル

```json
// ~/.config/llm-wiki/config.json
{
  "hub_path": "~/wiki",
  "resolved_path": "C:/Users/ykomi/wiki"
}
```

## コマンド一覧

```
/wiki:ingest     ← ソース取り込み
/wiki:assess
/wiki:compile    ← raw/ → wiki/ ビルド
/wiki:librarian
/wiki:lint
/wiki:ll
/wiki:output
/wiki:plan
/wiki:project
/wiki:query      ← 知識ベースへの問い合わせ
/wiki:refresh
/wiki:research
/wiki:retract
/wiki:thesis
/wiki:wiki
/wiki:wiki-manager
```

## よく使うコマンド

```
/wiki:ingest
/wiki:compile --wiki tecs
```

## プラグインファイル構成

```
plugins\marketplaces\llm-wiki\claude-plugin\commands\query.md
plugins\marketplaces\llm-wiki\claude-plugin\commands\wiki.md
plugins\marketplaces\llm-wiki\claude-plugin\skills\wiki-manager\references\ingestion.md
plugins\marketplaces\llm-wiki\claude-plugin\skills\wiki-manager\references\projects.md
plugins\marketplaces\llm-wiki\claude-plugin\skills\wiki-manager\SKILL.md
plugins\marketplaces\llm-wiki\plugins\llm-wiki\skills\wiki\references\ingestion.md
plugins\marketplaces\llm-wiki\plugins\llm-wiki\skills\wiki\references\projects.md
plugins\marketplaces\llm-wiki\README.md
```

## バリアント

- **ekadetov/llm-wiki** — `/llm-wiki:wiki init|ingest|query|lint`
- **AgriciDaniel/claude-obsidian**
- **nashsu/llm_wiki**

## Related

- [[Obsidian_nvk_llm-wiki]]
- [[TECS開発]]

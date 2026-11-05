---
date: 2026-06-13T00:00:00.000Z
description: "LLM wiki記事フォーマット仕様 — wiki:queryセッション記録。フロントマター・セクション構成の定義"
tags:
  - reference
  - llm-wiki
  - wiki-format
---

❯ Wiki Articleのフォーマットを教えて

● Skill(wiki:query)
Successfully loaded skill · 5 tools allowed
Allowed by auto mode classifier

WikiのHUBを解決してから記事フォーマットを調べます。

  Read 3 files

Wikiの記事フォーマットの仕様は、このTECS Wikiには格納されていません。代わりに、プラグインの参照ドキュメントと実際の記事を読んで回答します。

  Read 2 files

Wiki Article のフォーマットは wiki-structure.md 参照ドキュメントに定義されています。以下がフォーマットの全体像です。

---
Wiki Article フォーマット（wiki/ 配下）

フロントマター

---
title: "記事タイトル"
category: concept | topic | reference
sources: [raw/type/file1.md, raw/type/file2.md]
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
aliases: [別名1, 別名2]          # Obsidian の発見用
confidence: high | medium | low
summary: "インデックス用の2〜3文の要約"
---

実際の記事（cdl-language.md）では volatility と verified フィールドも追加されています（拡張フィールド）。

本文構造

# 記事タイトル

> [1段落の抄録]

## [内容に応じたセクション]

[合成コンテンツ — コピペではなく説明・文脈化・相互参照]

## See Also

- [[related-slug|関連記事]] ([関連記事](../category/related-slug.md)) — 関係の説明

## Sources

- [ソースタイトル](../../raw/type/file.md) — このソースの貢献内容

デュアルリンク形式（重要）

記事内の相互参照は必ず両フォーマットを同一行に記述：

[[target-slug|表示テキスト]] ([表示テキスト](../category/target-slug.md))

- [[wikilink]] → Obsidian がグラフビューとバックリンクに使用
- (相対パス) → Claude Code が実際にファイルを辿れる

ファイル命名規則

┌───────────────┬──────────────────────────────────────────────────────┐
│     種別      │                      命名ルール                      │
├───────────────┼──────────────────────────────────────────────────────┤
│ raw ソース    │ YYYY-MM-DD-descriptive-slug.md（日付プレフィックス） │
├───────────────┼──────────────────────────────────────────────────────┤
│ wiki 記事     │ descriptive-slug.md（日付なし — 生きたドキュメント） │
├───────────────┼──────────────────────────────────────────────────────┤
│ output 成果物 │ {type}-{topic-slug}-{YYYY-MM-DD}.md                  │
└───────────────┴──────────────────────────────────────────────────────┘

すべて小文字・ハイフン区切り・最大60文字。

---
補足: このフォーマット仕様は claude-plugin/skills/wiki-manager/references/wiki-structure.md に定義されており、現在のTECS Wikiには格納されていません。
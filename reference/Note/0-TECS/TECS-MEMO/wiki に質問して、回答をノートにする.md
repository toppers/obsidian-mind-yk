---
date: 2026-06-18
description: "TECS仕様書(html版)のサブディレクトリ名を質問に変換し、/wiki:query の回答を Obsidian ノートとして作らせる依頼プロンプト"
tags:
  - reference
  - tecs
  - wiki-query
  - prompt
---

`C:\0-MD-2\_ARCHIVE\ObsidianVault2\0-MD-2` を  `vault` にした `Obsidian`
  に対して、`\reference\Note\0-TECS\TECS仕様書(html版)` のサブディレクトリ名(を `-` で分割した右側部分)を質問として、
  `/wiki:query --wiki tecs-0-md <質問>` の返した文字列を内容とする、`reference\Note\TECS\TECS仕様書(tecs-0-md)` の下に
  `TECS仕様書(tecs-0-md)-<質問>` というタイトルのノート作成して


   `C:\0-MD-2\_ARCHIVE\ObsidianVault2\0-MD-2` を `vault` にした `Obsidian`
  に対して、
  `reference\Note\0-TECS\TECS-MEMO\TECS質問.md`のノートから、すべての行に対し、1行の内容を質問とし(ただし空行は無視する)、
  `/wiki:query --wiki tecs-0-md <質問>` の返した文字列を内容とする、`reference\Note\0-TECS\TECS仕様書(tecs-0-md)` の下に
  `TECS仕様書(tecs-0-md)-<質問>` というタイトルのノート作成して
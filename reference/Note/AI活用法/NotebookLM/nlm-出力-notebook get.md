---
date: 2026-07-16
description: "nlm notebook get の実行結果 — 返る JSON の実例（日本語文字列は Unicode エスケープされている）"
tags:
  - reference
  - notebooklm
  - cli
---

nlm notebook get <notebook_id> を実際に実行した結果、出力フォーマットは以下のJSONでした（Unicodeエスケープされていますが日本語文字列です）。

{
  "id": "bb4a0ade-b494-4c7f-b6e6-301d9047ea4e",
  "title": "(19) 認証・認可の最新トレンド：「OSW 2026」 - YouTube",
  "source_count": 1,
  "sources": [
    {
      "id": "0a469776-cd95-4b53-8bdd-db18e04c499d",
      "title": "認証・認可の最新トレンド：「OSW 2026」",
      "type": "youtube",
      "url": "https://www.youtube.com/watch?v=XBnq0U9f7-Q"
    }
  ],
  "is_owned": true,
  "is_shared": false,
  "created_at": "2026-06-29T08:34:10Z",
  "modified_at": "2026-07-15T19:48:12Z"
}

フィールド構成

┌──────────────┬────────┬─────────────────────────────────────────────────┐
│  フィールド  │   型   │                      内容                       │
├──────────────┼────────┼─────────────────────────────────────────────────┤
│ id           │ string │ notebook_id                                     │
├──────────────┼────────┼─────────────────────────────────────────────────┤
│ title        │ string │ Notebookのタイトル                              │
├──────────────┼────────┼─────────────────────────────────────────────────┤
│ source_count │ int    │ source数                                        │
├──────────────┼────────┼─────────────────────────────────────────────────┤
│ sources      │ array  │ source一覧（各要素は id, title, type, url）     │
├──────────────┼────────┼─────────────────────────────────────────────────┤
│ is_owned     │ bool   │ 自分が所有者か                                  │
├──────────────┼────────┼─────────────────────────────────────────────────┤
│ is_shared    │ bool   │ 共有されているか                                │
├──────────────┼────────┼─────────────────────────────────────────────────┤
│ created_at   │ string │ 生成日時（UTC, ISO 8601, YYYY-MM-DDTHH:MM:SSZ） │
├──────────────┼────────┼─────────────────────────────────────────────────┤
│ modified_at  │ string │ 更新日時（UTC, ISO 8601, YYYY-MM-DDTHH:MM:SSZ） │
└──────────────┴────────┴─────────────────────────────────────────────────┘

docs/spec/external/fetch.md との差異

docs/spec/external/fetch.md:65 には「(YAML)（id, title, is_owned, is_shared, created_at, modified_at）」と記載されていますが、実際の出力は以下の点で異なります。

- YAMLではなくJSONで出力される
- source_count と sources（source一覧）も含まれている（ドキュメントには未記載）
- created_at/modified_at はUTC（Zサフィックス）であり、〈用語の定義〉が定めるJSTタイムスタンプ形式（YYYY-MM-DD HH:MM:SS）への変換が別途必要

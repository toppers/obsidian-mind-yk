---
date: 2026-05-31
description: "nlm — NotebookLM CLI のコマンドリファレンス。notebook/source/chat/studio/research/audio/report/quiz等を網羅"
tags:
  - reference
  - notebooklm
  - cli
---

# nlm — NotebookLM CLI リファレンス

> `nlm --ai` の出力を整形したもの。Google NotebookLMをCLIから操作するためのツール。

## コマンド一覧

| コマンド | 用途 |
|---------|------|
| `login` | 認証 |
| `notebook` | ノートブック管理 |
| `source` | ソース管理 |
| `chat` | チャット設定・対話 |
| `studio` | スタジオアーティファクト管理 |
| `research` | リサーチ・ソース発見 |
| `alias` | IDエイリアス管理 |
| `config` | 設定管理 |
| `audio` | 音声オーバービュー作成（ポッドキャスト） |
| `report` | レポート作成 |
| `quiz` | クイズ作成 |
| `flashcards` | フラッシュカード作成 |
| `mindmap` | マインドマップ作成 |
| `slides` | スライドデッキ作成 |
| `infographic` | インフォグラフィック作成 |
| `video` | 動画オーバービュー作成 |
| `data-table` | データテーブル作成 |
| `auth` | 認証状態確認 |

## notebook

```bash
nlm notebook list [-a] [-j] [-q] [-t] [-p PROFILE]
nlm notebook create [TITLE] [-p PROFILE]
nlm notebook get NOTEBOOK_ID [-j] [-p PROFILE]
nlm notebook describe NOTEBOOK_ID [-p PROFILE]   # AI生成サマリー
nlm notebook rename NOTEBOOK_ID NEW_TITLE [-p PROFILE]
nlm notebook delete NOTEBOOK_ID [-y] [-p PROFILE]
nlm notebook query NOTEBOOK_ID QUESTION [-c CONV_ID] [-s SOURCE_IDS] [-p PROFILE]
```

## source

```bash
nlm source list NOTEBOOK_ID [-a] [-d] [-S] [-j] [-q] [-u] [-p PROFILE]
nlm source add NOTEBOOK_ID [-u URL] [-t TEXT] [-d DRIVE_ID] [-y YOUTUBE_URL] [--title TITLE] [--type TYPE] [-p PROFILE]
nlm source get SOURCE_ID [-j] [-p PROFILE]
nlm source describe SOURCE_ID [-p PROFILE]        # AI生成サマリー＋キーワード
nlm source content SOURCE_ID [-o OUTPUT_FILE] [-p PROFILE]
nlm source delete SOURCE_ID [-y] [-p PROFILE]
nlm source stale NOTEBOOK_ID [-j] [-p PROFILE]    # 同期が必要なDriveソース
nlm source sync NOTEBOOK_ID [-s SOURCE_IDS] [-y] [-p PROFILE]
```

## chat

```bash
nlm chat configure NOTEBOOK_ID [-g GOAL] [--prompt TEXT] [-r LENGTH] [-p PROFILE]
# GOAL: default | learning_guide | custom
# LENGTH: default | longer | shorter

nlm chat start NOTEBOOK_ID [-p PROFILE]           # インタラクティブチャット（REPL）
```

## studio

```bash
nlm studio status NOTEBOOK_ID [-a] [-j] [-p PROFILE]
nlm studio delete NOTEBOOK_ID ARTIFACT_ID [-y] [-p PROFILE]
```

## research

```bash
nlm research start QUERY [-s SOURCE] [-m MODE] [-n NOTEBOOK_ID] [-t TITLE] [-f] [-p PROFILE]
# SOURCE: web | drive
# MODE: fast (~30秒, ~10ソース) | deep (~5分, ~40ソース, webのみ)

nlm research status NOTEBOOK_ID [-t TASK_ID] [--compact|--full] [--poll-interval SEC] [--max-wait SEC] [-p PROFILE]
nlm research import NOTEBOOK_ID [TASK_ID] [-i INDICES] [-p PROFILE]
```

## コンテンツ生成

```bash
# 音声オーバービュー（ポッドキャスト）
nlm audio create NOTEBOOK_ID [-f FORMAT] [-l LENGTH] [--language LANG] [--focus TOPIC] [-s SOURCE_IDS] [-y] [-p PROFILE]
# FORMAT: deep_dive | brief | critique | debate

# レポート
nlm report create NOTEBOOK_ID [-f FORMAT] [--prompt TEXT] [--language LANG] [-s SOURCE_IDS] [-y] [-p PROFILE]
# FORMAT: 'Briefing Doc' | 'Study Guide' | 'Blog Post' | 'Create Your Own'

# クイズ
nlm quiz create NOTEBOOK_ID [-c COUNT] [-d DIFFICULTY] [-s SOURCE_IDS] [-y] [-p PROFILE]

# フラッシュカード
nlm flashcards create NOTEBOOK_ID [-d DIFFICULTY] [-s SOURCE_IDS] [-y] [-p PROFILE]
# DIFFICULTY: easy | medium | hard

# マインドマップ
nlm mindmap create NOTEBOOK_ID [-t TITLE] [-s SOURCE_IDS] [-y] [-p PROFILE]

# スライド
nlm slides create NOTEBOOK_ID [-f FORMAT] [-l LENGTH] [--language LANG] [--focus TOPIC] [-s SOURCE_IDS] [-y] [-p PROFILE]

# インフォグラフィック
nlm infographic create NOTEBOOK_ID [-o ORIENTATION] [-d DETAIL] [--language LANG] [--focus TOPIC] [-s SOURCE_IDS] [-y] [-p PROFILE]

# 動画オーバービュー
nlm video create NOTEBOOK_ID [-f FORMAT] [-s STYLE] [--language LANG] [--focus TOPIC] [--source-ids IDS] [-y] [-p PROFILE]
# STYLE: auto_select | classic | whiteboard | kawaii | anime | watercolor | retro_print | heritage | paper_craft

# データテーブル
nlm data-table create NOTEBOOK_ID DESCRIPTION [--language LANG] [-s SOURCE_IDS] [-y] [-p PROFILE]
```

## alias / config / auth

```bash
# エイリアス
nlm alias set NAME VALUE [-t TYPE] [-p PROFILE]
nlm alias get NAME
nlm alias list
nlm alias delete NAME [-y]

# 設定
nlm config show [-j]
nlm config get KEY
nlm config set KEY VALUE

# 認証
nlm auth status [-p PROFILE]
nlm auth list
nlm auth delete PROFILE [-y]
```

## 関連

- [[NotebookLM-Obsidian活用ワークフロー]]
- [[_NotebookLM-まとめ]]
- [[notebooklm-CLI]] — 別実装（`notebooklm` コマンド、notebooklm-py 系）。コマンド体系を比較

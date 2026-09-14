---
date: 2026-06-13T00:00:00.000Z
description: "wiki:planコマンド例 — tecsgen外部仕様書・TECSCDE JS版アーキテクチャ設計のプロンプトサンプル"
tags:
  - reference
  - tecs
  - wiki-plan
---

  /wiki:plan "tecsgen外部仕様書の構成設計" --wiki tecs
  /wiki:plan "TECSCDE JavaScript版アーキテクチャ設計" --wiki tecs --format rfc
  /wiki:plan "notebookmlx設計" --wiki notebookmlx --quick
==
  /wiki:plan "tecsgen外部仕様書の構成設計" --wiki tecs

  次に何をしますか？

  1. Webリサーチでブートストラップ
  /wiki:research "TECS TOPPERSコンポーネントシステム tecsgen CDL" --wiki tecs --sources 10

  2. ローカルのTECSドキュメントを取り込む
  /wiki:ingest <ファイルパスまたはURL> --wiki tecs

  3. 既存ノートをinboxにドロップして一括取り込み
  # ファイルを C:/Users/ykomi/wiki/topics/tecs/inbox/ に置いてから：
  /wiki:ingest --inbox --wiki tecs

  ▎ Tip: リサーチセッションは多数のURLを取得します。承認プロンプトを省略するには .claude/settings.local.json の
  ▎ permissions.allow に "WebFetch" と "WebSearch" を追加してください。

  /wiki:plan "TECSCDE JavaScript版アーキテクチャ設計" --wiki tecs --format rfc
  /wiki:plan "notebookmlx設計" --wiki notebookmlx --quick


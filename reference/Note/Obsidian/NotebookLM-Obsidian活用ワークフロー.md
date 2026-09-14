---
date: 2026-05-29
description: "NotebookLMとObsidianを組み合わせた情報整理ワークフロー — 要約・QA・ノート化・タグ運用・実践ケース集"
tags:
  - reference
  - notebooklm
  - obsidian
  - workflow
source: reference/Inbox/ObsidianユーザーのためのNotebookLM活用術.md
---

# NotebookLM + Obsidian 活用ワークフロー
「ObsidianユーザーのためのNotebookLM活用術」
## NotebookLMの基本機能

1. **要約** — 資料を読み込ませると自動要約
2. **質疑応答** — 資料に基づいたQ&A
3. **複数資料横断** — 複数PDFを一括検索・比較
4. **出力活用** — 要約・QA結果をObsidianに落とし込む

## Obsidianへの落とし込みワークフロー

### ノートの作り方（テンプレート）

→ `[[templates/from-NotebookLM]]` を使う

### タグとリンクの活用

- `# 宿題` `# 試験範囲` `# 引用` `# 経費` など目的別タグ
- タスク管理ノートへのリンクでToDoに落とし込む

## 実践ケース集

| ユースケース | NotebookLMの役割 | Obsidianの役割 |
|---|---|---|
| 学校プリント | 宿題・提出日・試験範囲を抽出 | 教科別ノートに要点を整理 |
| 会議議事録PDF | 議論・決定事項・担当者を抽出 | プロジェクトノートに保存、ToDoにリンク |
| 領収書・請求書 | 金額・日付・支払先を抽出 | 経費ノートに月別整理 |
| 参考文献PDF | 要約・重要引用を抽出 | テーマ別ノートに貼り付け、`#引用`タグ |

## ポイント

- 「資料→NotebookLM要約→Obsidianノート」のパイプラインを型化する
- 要約ノートに「補足メモ（自分の考え）」セクションを必ず設ける
- 出力を `# 引用` タグで管理 → 執筆時に一発検索可能
- 「要点→考察→元号下書き」の流れをObsidianで完結させる

## NotebookLMプロンプト例（Vault対話）

- 要約: 「このVaultの内容を3つのポイントで要約して」
- 行動化: 「このノートから、明日からできる行動を5つ提案して」
- 発散: 「このアイデアを広げられる視点を教えて」
- つながり: 「このノートと関連する他のノートを教えて」
- 振り返り: 「今月の振り返りから見える自分の成長ポイントは」

> 出典: 「Obsidianで知識をお金に変える」第2章 — NotebookLMでVaultに「話しかける」

## 関連

- [[templates/from-NotebookLM]]
- [[brain/Patterns]]
- [[ObsidianユーザーのためのNotebookLM活用術]]

---
date: 2026-09-08
description: "Kortex Notebook（kortex-notebooklm.com）— NotebookLMをナレッジハブ化するChrome拡張。LLMチャットのアーカイブ、ソース一括インポート、チャット/成果物エクスポート、プロンプト管理、ダッシュボード、自動化ルールを追加する。"
tags:
  - reference
  - notebooklm
  - chrome-extension
  - tool
---

# Kortex Notebook: Best Gemini NotebookLM Toolkit

- **URL**: kortex-notebooklm.com（Chrome ウェブストア掲載）
- **形態**: ブラウザ拡張機能（Chrome）。NotebookLM の UI に機能を追加する
- **規模（as of 2026-09-08、ストア掲載値）**: 評価 4.7（366件）、ユーザー約100,000、「おすすめ」バッジ
- **課金**: 一部機能は無料（ハイライト＆スナイプ、チャットのクリップボードコピー等）、一括インポート系は Pro 機能

NotebookLM を「ダイナミックで相互接続されたナレッジベース」に拡張することを謳う。競合カテゴリは NotebookLM の周辺ツール一般で、[[notebooklmclix]]（自作の NotebookLM ソース管理システム）や [[nlm-使い方\|nlm CLI]] と機能領域が重なる（ソースの一括管理・エクスポート・整理）。ただし Kortex は GUI 拡張、nlm は CLI という違いがある。

## 機能グループ（16項目を整理）

### 取り込み（インポート）
- **ワンクリック LLM アーカイブ**: ChatGPT / Claude / Gemini / Perplexity のページに「NotebookLM」ボタンを追加し、会話全体を引用付きソースとして NotebookLM へ取り込む
- **ソーシャルメディアインポート**: スレッド/投稿を文脈・投稿者・元URL付きで取り込む
- **ハイライト＆スナイプ**: 任意のウェブページのテキストを右クリックで NotebookLM に送信（無料・サブスク不要）
- **一括インポート（Pro）**: Google Docs 一括同期 / URL リスト / 開いているタブ / RSS フィード / CSV / ウェブクローラー

### 書き出し（エクスポート）
- **ソースダウンローダー**: ノートブックのソースを PDF / Markdown / テキスト / ZIP で出力（個別・一括・ノートブック全体）
- **多形式チャットエクスポート**: Q&A 履歴を Markdown / テキスト / PDF / JSON（無料でクリップボードコピーも可、メッセージ選択エクスポート）
- **厳選ブリーフィングノート**: チャットの重要回答をチェック選択して共有可能なブリーフィング文書を生成
- **Studio ノート＆成果物エクスポート**: AI ノート・学習ガイド・クイズ・FAQ・タイムライン等を Markdown / テキスト / PDF で出力
- **オーディオ概要マネージャー / ポッドキャスト RSS 生成**: AI 音声概要の管理・DL、カスタム RSS フィード化

### 整理・管理
- **プロンプト管理**: フォルダ（色付き）・タグでプロンプトを保存、クラウド同期
- **ソースビュー**: ソースのカスタムフィルタビュー（すべて/PDF/Web/Google Docs/Text/YouTube）を保存、デバイス間同期
- **高度なダッシュボード**: 全ノートブック横断のソーステーブル、スマート検索、グローバル検索（Ctrl+K）、コレクション＆タグ、お気に入り
- **ソース管理**: 複数選択削除、処理失敗した「不良ソース」の特定・削除
- **機能管理**: Kortex 各機能のオン/オフ

### 自動化
- **自動化ルール**: Auto Researcher（タイトル/新ソース追加をトリガーに自動リサーチ）、Podcast Curator（条件成立で音声概要を自動生成）、パイプライン自動化（複数アクション連携）

## Related

- [[_NotebookLM-まとめ]] — NotebookLM 関連ノートのインデックス
- [[notebooklmclix]] — 自作の NotebookLM ソース管理システム（機能領域が重なる、比較対象）
- [[nlm-使い方-source]] — nlm CLI のソース管理（CLI 版の対応機能）
- [[見逃した10の機能]] — NotebookLM 本体の隠れ機能メモ

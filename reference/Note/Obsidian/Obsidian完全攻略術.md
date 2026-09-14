---
date: 2026-07-23
description: "Obsidianプラグイン活用ガイド — Tasks/Kanban/Excalibrain/DataView/Templater/Calendar等の機能概要とカスタムCSSによる外観カスタマイズ例"
tags:
  - reference
  - obsidian
  - plugins
---

OBSIDIAN完全効力

# Plugin
## Takss
ノート内のチェックボックスをタスクとして管理。期限や優先度でフィルタリング可。
## Kanban
カンバンボード形式で視覚的に整理。進行状況を一目で把握。
## Excalibrain
選択したノートを中心に、関連するノートをマインドマップ形式で表示

## DataView
- Obsidian内のMarkdownファイルデータベースのように扱い、クエリを用いてノートをリストやテーブル形式で表示できる
- ノートのメタデータ（プロパティ）を基にした動的なリストやテーブルの作成
- 特定のタグや日付、タイトルなどの条件でノートをフィルタリング
- 複雑なクエリを用いて、ノート間の関係性を可視化
## Templater
- Obsidianのテンプレート機能を強化し、動的なテンプレートの作成やスクリプトの実行を可能にする
- 日時やメタデータの自動挿入
- ユーザー定義のスクリプトや関数の実行
- テンプレート内での条件分岐やループ処理
## Calendar
- Obsidian内でカレンダー形式のビューを提供し、日付ごとのノート作成や管理を容易にする
- カレンダー上で日付をクリックして新しいノートを作成
- デイリーノートやジャーナルの管理
- カレンダー上での未完了タスクの確認
## Kanban
- タスクやプロジェクトの進行状況を視覚的に管理するためのカンバンボードを作成
- カンバンボードの作成とカスタマイズ
- ドラッグ＆ドロップによるタスクの移動
- カスタムステージやカラムの設定
## Excalidraw
- Obsidian内で手書き風の図やスケッチを作成できる
- 図形やテキストの追加、編集
- Obsidian内のノートとして保存
## Obsidian Git
- ノートをGitリポジトリに自動的にバックアップし、変更履歴を追跡
## Tasks
- タスク管理強化
- タスクの生成と管理
- 期限や優先度の設定
- 繰り返しタスクの設定
## Periodic Notes
- 日次、週次、月次、年次ノートの作成
- 定期的なノートのテンプレート化
- カレンダーとの連携
## Excalibrain
- ノート間の親子関係や兄弟ノードを視覚的に表示
- リンクkの持つ意味やVault全体の構造を直感的に理解
- ノート同士の関連性を一目で確認
## Omnisearch
- PDFや画像を含めて検索できる
- OCR処理する
- PDFや画像内のテキストを検索可能にする
- OCR処理による文字認識
- 花蓮製の高い検索結果の表示
## Smart Connections
- メモ相互の関連性を自動発見する
- 関連ノートの提案
- 知識ネットワークの拡張
## D2
- テキストからダイアグラムを生成
- ソフトウェアアーキテクチャ図の作成
- LaTeXやTikZをグラフや図として描画
# カスタムCSSによるインターフェースのデザイン変更
## CSSスニペットの活用
- .obsidian/snippets/
	- custom-style.css
	- ```
	  h1,h2,h3{
		  color: #3498db;
	  }
	  ```
	  Obsidianの設定画面から、外観>CSSスニペットでスニペットを有効か
## 開発者ツール(DevTools)
## CSSカスタムプロパティの活用
```
--h1-color: #e74c3c;
```
## カスタマイズ例
### チェックリストの取消線を非表示にする
```
.task-list-itemi-is-checked {
text-decoration: none;
}
```
### コードブロックの言語に応じて色を変更する
```
.cm-s-obsidian .cm-syntax .cm-keyword {
  color: #e74c3c;
}
```
# 追加
## Obsidian Embed Calendar

## Related

- [[reference/Note/Obsidian/Obsidian-Pluginリスト|Obsidian-Pluginリスト]] — 既存のプラグイン一覧ノート
- [[reference/Note/Obsidian/Obsidian Bases大全|Obsidian Bases大全]] — プロパティ設計・Base活用の関連ガイド

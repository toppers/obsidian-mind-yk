---
date: 2026-09-16
description: "notebooklmclix のログインおよびループ取得を行うPowerShellスクリプト実装用プロンプト"
tags:
  - reference
  - prompt
---
# Context
# Notes
以下の処理を行うPowerShellスクリプトを実装して

# 1.ディレクトリ移動
e:\Ccur\python3\notebooklmclix

# 2.ログイン
下記のコマンドの実行
`uv run notebooklmclix login`

# 3.ノートブック取得（失敗するか、すべて取得するまで)
リターンコードが0 ノートブックをすべて取得済み
リターンコードが10 未取得のノートブックが存在する
リターンコードが上記以外 失敗発生

下記のコマンドの実行
`uv run notebooklmclix fetch --limit 100`

リターンコードが10の間、上記のコマンドの実行を繰り返す

## Related
-

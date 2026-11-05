---
date: 2026-05-05
description: "Python パッケージ配布の最短手順（Zenn記事）— uv init でプロジェクトのディレクトリを作るところから"
tags:
  - reference
  - python
  - packaging
---

[Pythonパッケージ配布の最短手順](https://zenn.dev/d3c0b/articles/74627e56499816)
# uvでプロジェクトのディレクトリを作成する
uv init zenntest # 各々のパッケージ名
# /zenntestに移動
cd zenntest
# 実際にPyPIにアップロードするファイルを作成する
uv build
# PyPIのアカウント設定ページで取得したAPIトークンを添えて`uv publish`
# (--publish-urlオプションは練習時のみ必要)
uv publish --token APIトークン --publish-url https://test.pypi.org/legacy/

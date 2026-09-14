---
date: 2026-06-18
description: "headroom-ai を uv tool run で起動するコマンド控え — UV_TOOL_DIR と --cache-dir をローカルへ向け codex を wrap する"
tags:
  - reference
  - tool
  - uv
---
- コンテキストウィンドウの節約を目的としてMCPサーバー
- headroom_compress: 大量の結果を圧縮してハッシュ化
- headroom_retrieve: ハッシュから元データを取得
- headroom_status: 圧縮統計確認
- 使われる場面
	ツール結果が大量のデータを返す場合（例：ファイル一覧、grep結果、ログ等）、headroomが自動的に内容を圧縮して以下のようなマーカーに置き換えます：
	[250 items compressed... hash=abc123]
	Claudeがその一部だけ必要な場合、headroom_retrieve でクエリ付き取得が可能：
	headroom_retrieve(hash="abc123", query="error")

- なぜ重要か
	- コンテキストウィンドウへの大量データ流入を防ぐ
	- 必要な部分だけ選択的に取得できる
	- 長い会話でもコンテキスト枯渇を遅らせる
	
$env:UV_TOOL_DIR='.uv-tools'
  uv --cache-dir .uv-cache tool run --python C:\Users\ykomi\.direnv\data\mise\installs\python\3.13.12\python.exe --from 'headroom-ai[all]' headroom wrap codex --no-proxy
  
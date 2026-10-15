---
date: 2026-07-20
description: "pmb MCP サーバーの接続失敗の調査記録 — 当該セッションでは mcp__pmb__* が一切追加されず、直前の別セッションでは正常だったため恒常的ではなく間欠的な障害と判定"
tags:
  - reference
  - mcp
  - troubleshooting
---

確認した事実
- 今回セッション: deferred_tools_delta は1回のみ発火、mcp__pmb__* 一切追加されず、以降リトライも無し → 接続失敗確定。
- 直前(1時間前)の ghrepo セッション、および gistx セッションでは pmb 正常接続、mcp__pmb__* 10ツール全部利用可能。→ 恒常的な壊れ方ではなく間欠的。
- 実バイナリで同一条件を再現: command: pmb-mcp の解決先 c:\Users\ykomi\.direnv\bin\pmb-mcp.exe、env PMB_CWD=E:\Ccur\python3\gistx、cwd=E:\Ccur\python3\ghrepo で手動起動 → MCP initialize ハンドシェイク正常完了、ツール一覧取得成功。バイナリ・設定自体は今この瞬間は正常。

有力な原因
FastMCP起動時にPyPI相当のアップデートチェックをネットワーク越しに行う(起動バナーの 🎉 Update available: 3.4.4 がその証拠)。この応答待ちのせいで起動に数秒余分にかかる。今回セッション起動時にこの通信が遅延/詰まり、Claude Code側のMCP接続タイムアウトに引っかかって「失敗」扱いになった可能性が高い。同時刻に SessionStart hook(cce.exe 呼び出し)も別要因(bashによるWindowsパスのバックスラッシュ欠落)で失敗しており、セッション起動自体が不安定だった傍証もある。

副次的に見つかった設定不備(直接の失敗原因ではないが直すべき)
~/.claude.json のグローバル mcpServers.pmb.env.PMB_CWD が "E:\\Ccur\\python3\\gistx" に固定されている。プロジェクト非依存であるべき値がハードコードされているため、ghrepo等どのプロジェクトで起動しても pmb は常に gistx のワークスペースを参照する(接続には支障なしと確認済みだが、記録される記憶・lessonsが常にgistxのものになる)。

対処
1. すぐ試す: セッション再起動で再接続を試みる(タイムアウト起因なら次回は繋がる可能性大)。
2. 恒久対策: PMB_CWD のハードコードを外す。pmbがcwdから自動判定できるなら env自体削除。プロジェクトごとに切り替えたいなら .mcp.json(プロジェクトローカル)側に移す。
3. 更新チェックの遅延が疑わしいなら pmb-ai 側にオフライン/アップデートチェック無効化オプションがないか確認(公式ドキュメント/pmb --help)。

✻
---
date: 2026-07-23
description: "qmd の MCP クライアント/サーバー導入記録 — npm がネイティブモジュールのビルドをブロックし、mise 管理 node では node-gyp-build が解決できず失敗した経緯"
tags:
  - reference
  - qmd
  - mcp
  - troubleshooting
---

qmd MCPクライアント/サーバーのインストールが完了しました。

やったこと:
1. npm install -g @tobilu/qmd → Windows環境でnpmがネイティブモジュール(better-sqlite3, node-llama-cpp, tree-sitter系)のビルドスクリプトをブロックし、確認の上で許可設定して再実行 → それでもnpm/bun経由の自動ビルドがこの環境（Windows + mise管理node）で node-gyp-build/postinstallスクリプトを解決できず失敗
2. bun install -g @tobilu/qmd に切り替え → CLI自体は C:\Users\ykomi\node_modules 配下にインストールされたが、同様に better-sqlite3 のネイティブバイナリだけビルドされず
3. better-sqlite3 パッケージ内で prebuild-install を手動実行し、GitHub Releaseからプリビルド済みバイナリを直接取得 → qmd status が正常動作することを確認（既存のインデックス: 330ファイル、wiki系コレクション9件を検出）
4. claude mcp add qmd -s user -- qmd mcp でユーザースコープ（全プロジェクト共通）のstdio MCPサーバーとして登録 → claude mcp get qmd で Connected を確認

これで新しいセッションから qmd の検索(qmd_query等)ツールがMCP経由で使えるはずです。現在のセッションではまだツールが読み込まれていないので、使う場合はこのセッションを再起動するか、ToolSearch 経由で読み込んでください。

なお bun install -g の際に C:\Users\ykomi\node_modules 直下にパッケージが展開されており、通常のグローバルインストール先（~/.bun/install/global等）と異なる少し変則的な場所です。動作に支障はありませんが、気になる場合はお知らせください。

## Related
- [[reference/Note/AI開発/Claude-Code/MCP/QMD/QMD-SQLiteの場所|QMD インストール後の SQLite の所在]] — インデックス DB とエンジン本体（better-sqlite3 / sqlite-vec）の格納場所

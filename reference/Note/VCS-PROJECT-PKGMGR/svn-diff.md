---
date: 2026-08-24
description: "SVNタグ間（tecsgen-1.7.0〜1.8.0等）のログ取得コマンド控え"
tags:
  - reference
  - svn
  - tecsgen
---

❯ tags/tecsgen-1.7.0 とtags/tecsgen-1.8.0 の間のlog を取得する方法を教えて

タグのパスを確認してから、実際に使えるコマンド例を示します。

  Ran 2 shell commands

両方のタグが存在することを確認できました。それぞれのリビジョン番号を調べた上で、2つのタグ間のログを取得します。

  Ran 1 shell command

tecsgen-1.7.0 は trunk r3086 から、tecsgen-1.8.0 は trunk r3250 から作られています。この2つのリビジョン範囲で trunk のログを取得すれば、両タグ間の変更履歴が得られます。

方法1: trunk のリビジョン範囲でログを取る（最も一般的）

svn log -r 3086:3250 https://dev.toppers.jp/svn/tecs/toppers/tecsgen/trunk

詳細（変更ファイル一覧つき）が欲しい場合は -v を追加：

svn log -v -r 3086:3250 https://dev.toppers.jp/svn/tecs/toppers/tecsgen/trunk

方法2: タグそのものを指定してリビジョン範囲を取る

タグはコピーなのでこちらでも同様の結果になります：

svn log -r 3087:3252 https://dev.toppers.jp/svn/tecs/toppers/tecsgen/tags/tecsgen-1.8.0

## Related
- [[svn-log]]

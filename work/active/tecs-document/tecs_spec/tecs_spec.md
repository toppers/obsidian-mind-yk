---
date: 2026-09-16
description: "TOPPERS tecs_spec SVNリポジトリのドキュメント仕様書・TOC章節番号付与および章分割作業メモ"
project: tecs
status: active
quarter: Q3-2026
tags:
  - work-note
---

# tecs_spec
## Context
- 
- ローカルリポジトリ　"E:\Crepo\toppers-tecs-svn\toppers\tecs_spec\trunk"
- リモートリポジトリ  https://dev.toppers.jp/svn/tecs/toppers/tecs_spec/trunk
-  リモートリポジトリの情報
Path: .
Working Copy Root Path: E:\Crepo\toppers-tecs-svn\toppers\tecs_spec
URL: https://dev.toppers.jp/svn/tecs/toppers/tecs_spec/trunk
Relative URL: ^/toppers/tecs_spec/trunk
Repository Root: https://dev.toppers.jp/svn/tecs
Repository UUID: 7858d647-59cc-45ef-8cad-5c7a40372aff
Revision: 3303
Node Kind: directory
Schedule: normal
Last Changed Author: okuma-top
Last Changed Rev: 2291
Last Changed Date: 2015-11-23 10:03:15 +0900 (月, 23 11 2015)

## Notes
- prompt:
	- "E:\Crepo\toppers-tecs-svn\toppers\tecs_spec\trunk\base\_md\tecs_spec.md"から、LaTeXのTOCファイル"E:\Crepo\toppers-tecs-svn\toppers\tecs_spec\trunk\base\_md\tecs_spec.toc"を参考に、章番号、節番号などを章のタイトル、節のタイトルなどの先頭に空白文字1個を挟んで連結させたものを、同階層の`tecs_spec_ex.md`として作成して
	- 先ほどの処理を行う、Pythonスクリプトを作成して
	- "E:\Crepo\toppers-tecs-svn\toppers\tecs_spec\trunk\base\_md\tecs_spec_ex.md"から先頭が`## `で始まる行で必ず章として分割されたファイルを、同じ階層に新たに作成して。
## Action Items
- [ ] eps形式の図をpng形式の図に変換するスクリプトの作成
- [ ] tecd_specの原稿のテキストファイルをLaTeX化する際の中間ファイルからMarkdown形式ファイル化するPythonスクリプトの作成

## Related
- [[TECS開発]]
- [[work/Index.md|work/Index]]


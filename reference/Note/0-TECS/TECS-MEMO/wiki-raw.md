---
date: 2026-07-24
description: "tecs wiki の raw ソース状況メモ — raw/articles 58件、取り込み元 tecs-docs.readthedocs.io と対応 GitHub リポジトリ、tecs_spec.pdf のローカルパス。2026-09-13、tecs-spec-base（LaTeX直接変換版）を追加し、tecs-0-mdとの重複・tecs-0との版差・公開状況を記録"
tags:
  - reference
  - tecs
  - wiki
---

# tecs
raw/articlesのファイルが58個
https://tecs-docs.readthedocs.io/ja/latest/index.html　をwebから取り込んだもの。
対応するGithubリポジトリは以下のもの
https://github.com/toppers/tecs-docs.git 
# tecs_html
raw/articlesのファイルが86個
https://github.com/toppers/tecs-docs.git から sphinx-build を用いて作成した、HTMLファイル群を取り込んだもの
C:/Users/ykomi/Downloads/TECS-Documentation-20280608/TECS.md
C:/Users/ykomi/Downloads/TECS-Documentation-20280608/tecs_spec/trunk/base/tecs_spec.pdf ーDraft版(V1.3.0.1)「組込みコンポーネントシステム　TECS仕様書」 2015年11月15日

# tecs_md
raw/articlesのファイルが1個
https://github.com/toppers/tecs-docs.git から shinx-build を用いて作成した、PDFを markitdown で1個のMarkdown形式ファイルに変換したもの
C:/Users/ykomi/Downloads/TECS-Documentation-20280608/TECS.md
# tecs-0 | svnのold/generator/reference
raw/articlesのファイルは7個
https://dev.toppers.jp/svn/tecs/old/generator/trunk/reference
r906 | okuma-top | 2010-05-28 16:44:24 +0900 (Fri, 28 May 2010) | 1 line

old contents
---
章別ディレクト下のテキストファイル(ファイル名は連番を含む)群
/wiki:ingest でディレクトリを指定。LLMがすべてのファイルを読込、意味的にまとまりのあるファイルに分割する（章別ファイル、ファイルサイズが大きければ、さらにまとまりがあるように細分化したファイルにする）

# tecs-0-md | svnのtecs_spec
raw/notesのファイルが1個
https://dev.toppers.jp/svn/tecs/toppers/tecs_spec/trunk/tecs_spec.pdf　からmarkdownitで１個のMarkdown形式ファイルに変換したファイル

r2291 | okuma-top | 2015-11-23 10:03:15 +0900 (Mon, 23 Nov 2015) | 1 line

draft 1; temporary check in
- Draft版(V1.3.0.1)
- 2015年11月15日

==
# TECS簡易パッケージ内のTECS仕様書のバージョン
- [tecs_package-20120608.tar.gz](https://www.toppers.jp/download.cgi/tecs_package-20120608.tar.gz)
	- tecs_package/tecsgen/doc/tecs_spec.pdf
	- 暫定第一版(V1.0.2.32)
		- 2011年5月8日
- [tecs_package-20100604.tar.gz](https://www.toppers.jp/download.cgi/tecs_package-20100604.tar.gz)
	- tecs_package/tecsgen/doc/tecs_spec.pdf
	- 暫定第一版(V1.0.2)
	- 2010年6月4日
- [tecs_package-20090728.tar.gz](https://www.toppers.jp/download.cgi/tecs_package-20090728.tar.gz)
	- tecs_package/tecsgen/doc/tecs_spec.pdf
	- 暫定第一版(V1.0.0.5)
	- 2009年7月17日
- [tecs_package-20090612.tar.gz](https://www.toppers.jp/download.cgi/tecs_package-20090612.tar.gz)
	- tecs_package/tecsgen/doc/tecs_spec.pdf
	- 暫定第一版(V1.0.0.3)
	- 2009年6月12日

# tecs-spec-base | svnのtecs_spec（LaTeX原本直接変換）
raw/papersのファイルが1個
E:/Crepo/toppers-tecs-svn/toppers/tecs_spec/trunk/base/tecs_spec.md（toppers-tecs-svnのローカルクローン。dev.toppers.jp/svn/tecs 系と同一系譜）
変換パイプライン: プレーンテキスト → TeXソース化 → Markdown化（HTML/PDF経由なし）
- Draft版(V1.3.0.1)
- 2015年11月15日
- ingested: 2026-09-13

## tecs-0-mdとの比較（2026-09-13確認）
tecs-0-md（プレーンテキスト → TeXソース化 → HTML化 → PDF化 → Markdown化）と同一バージョン・実質同一内容。逐語一致を確認済み（例：「TECS におけるリモート呼び出しは、結合を RPC チャネルに置き換える」が両ソースで完全一致）。差異は変換パイプラインの段数のみ——tecs-0-mdはHTML/PDF経由でノイズが多く（目次崩れ、句読点が「: : : :」化、6820行/463KB）、tecs-spec-baseはTeXから直接変換したクリーン版（5890行/289KB）。
判断：両ウィキとも保持（現状維持）。tecs-spec-baseは高品質リファレンスとして活用する。

## tecs-0との比較（2026-09-13確認、raw/articles 5件＋シグニチャ例1件を通読）
「同一仕様書の別形式」ではなく実質「別バージョン」と判明。

| 項目 | tecs-0 | tecs-spec-base |
|------|--------|----------------|
| バージョン表記 | なし（無版数） | Draft V1.3.0.1 (2015-11-15) |
| 著作権表示 | copyright(c) 2008 | Copyright 2006-2015 |
| 公開範囲 | 「TOPPERSプロジェクト会員限定」「非会員は参照不可」 | 一般公開ライセンス（利用条件明記） |
| ステータス | 「本仕様書は、まだ作成途中です」 | 「暫定第一版」相当（改訂履歴が整備済み） |
| RPCの扱い | 第2章に独立節（30-rpc.txt）としてトランスペアレント/オペイク4分類を記述 | 第3章に統合（第6章TECS RPCは削除済み）。ただし4分類の説明文はほぼ同じ内容が残存 |

- 概念レベルでは重複あり：セル・セルタイプ・受け口・呼び口・シグニチャ・結合・RPCの4分類など根幹概念は一致（同じ仕様の系譜）。
- 逐語的な重複はなし：文言は書き直されている。
- tecs-spec-baseだけにある新機能（改訂履歴記載）：前方参照仕様変更／id・prototype・generate指定子／組込み型とtypedef型／tecs.h・t_stddef.h／固定結合・逆結合／リージョンスルー指定子／リージョン属性node,linkunit,domain,class／ルートネームスペース・ルートリージョン／nullable指定子——tecs-0には一切存在せず、V1.3.0.1より明確に古い初期ドラフトと確認。
- `2026-06-08-cdl-signature-examples.md`（source: MANUAL）は仕様書からの抽出ではなく手作りのサンプル集のため、重複対象外。

## 公開状況（ユーザ申告、2026-09-13）
- tecs-0: 外部に公開済み
- tecs-spec-base: 外部には非公開

詳細は llm-wiki 側 `C:/Users/ykomi/wiki/topics/tecs-spec-base/config.md` を参照。進捗全体は [[TECS開発]] を参照。



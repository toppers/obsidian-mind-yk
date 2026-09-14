---
date: 2026-06-03
description: "TECSCDE（TECSコンポーネント図エディタ）外部仕様書。全11章完成（概要・動作環境・画面構成・図の表現・ファイル操作・編集操作・表示機能・CDL連携・エラーと警告・制約と制限・用語集）。JS版はブラウザ単体・単一ページ構成。保存形式は CDL 同居の .cde。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

# TECSCDE 外部仕様

> [!info] 文書状態
> **改訂（2026-09-13）**: tree-sitter 製の CDL パーサ（`tree-sitter-cdl`／`tree-sitter-tecs-cdecl`、いずれも tecsgen 自身の構文定義 `bnf.y.rb`・`C_parser.y.rb` からの移植）の採用を決定し、**2.2・5.1.2・5.3.2・8.1.2・8.2.2・8.3.2・9.1.2・10.1／10.4 表**を改訂した。主な変更は3点——①2.2 の「依存ライブラリなし」に CDL 解析系のみの例外を設けた、②`import_C` の「常に非対応」を撤回し、利用者が明示的に読み込んだ C ヘッダからの `typedef`／`struct` 抽出を限定対応とした（プリプロセッサは実行しない）、③構文エラーの検出・提示を 8.3.2／9.1.2 に新設した。あわせて「`import` を追跡しない理由」をパーサ能力からファイルアクセス能力へ訂正し、UTF-8 限定・`__location_information__` 非対応という新たな制約を 5.1.2 に追加した。反映案の全文と検討経緯は [[work/active/CDLParser(tree-sitter利用)/TECSCDE外部仕様 tree-sitter反映案|TECSCDE外部仕様 tree-sitter反映案]]。
>
> **第1章（概要）完成（2026-07-23）・第2章（動作環境）完成（2026-07-29）・第3章（画面構成）完成（2026-07-29）・第4章（コンポーネント図の表現）完成（2026-07-31）・第5章（ファイル操作）完成（2026-08-01）・第6章（編集操作）完成（2026-08-06）・第7章（表示機能）完成（2026-08-07）・第8章（CDL 連携）完成（2026-08-08）・第9章（エラーと警告）完成（2026-08-11）・第10章（制約・制限）完成（2026-08-12）・第11章（用語集）完成（2026-08-13）** — **全11章完成、TECSCDE 外部仕様書は本文執筆完了**。TECSCDE はまだ実装前のため、10章以降は設計意図ベースで記入する。第11章は新規の一次資料調査を行わず、第1〜10章で使われた用語のうち TECSCDE 特有の意味を持つものを再編成した（既存の項目一覧8件を維持しつつ15件を追加、計23件）。CDL 言語一般の用語は [[tecsgen外部仕様]] の用語集を正とする方針を明記した。第10章は新規の一次資料調査を行わず、第1〜9章で確定済みの事実を「実行環境由来」「編集可否」「モデル・操作上の制約（現行版踏襲）」「機能スコープ外」の4分類に再編成した。**訂正**: 3.4.1 で「CDL ファイル由来／CDE ファイル由来」と表現していたセルの編集可否の区別を、実際の判定基準（セルの定義元ファイルが編集対象自身かどうか、`locale` ベース）に基づいて再定義した——`.cde` の中身は CDL そのものであり（5.1.1）、ファイル形式では編集可否は決まらない。第9章の現行版の事実は CDL 解析エラー・警告を出力する `Generator` クラス（`tecslib/core/bnf.y.rb`）・メッセージカタログ（`tecslib/messages/messages_console_ja_JP.rb`）・TECSCDE 起動処理（`tecscde.rb`）に基づく。**最大の発見**: tecsgen 本体はコード生成前にエラー件数を確認して `exit` するが、TECSCDE が呼ぶ `run1` にはこのチェックが存在せず、CDL にエラーがあっても TECSCDE は常に GUI を起動する——エラー・警告は起動したコンソールの標準出力にのみ現れ、GUI 上には保存失敗時を除き一切表示されない。第8章の現行版の事実は起動処理 `tecsgen.rb`・解析処理 `tecslib/core/tecsgen.rb`（`syntax_analisys`/`run1`/`run2`）・`Import` クラス（`tecslib/core/componentobj/import.rb`）に基づく。**現行版でもコード生成（`run2`）は一度もトリガーされない**（`cdelib` 全9ファイルで呼び出しゼロ）ことを確認し、JS 版の「tecsgen を直接起動できない」制約（2.3）が後退ではなく現行版の設計の継承であると位置付けた。第7章の現行版の事実は表示制御バー実装（`cdelib/tview.rb` 408〜449行）・`ALIGN` 定数と `round_length_val`（`cdelib/tmodel.rb`）・読み込み時のフォールバック配置（`cdelib/saveload.rb`）に基づく。検索・表示フィルタは現行版に対応する実装が存在しないため新規要件として規定した。第6章の現行版の事実は制御層 `cdelib/tcontrol.rb`（781行）とモデル層のアンドゥ機構 `ChangeSet`/`ChangeSetManager`（`tmodel.rb`）に基づく。第2章で JS 版の実行形態を**ブラウザ単体（ローカル・サーバ処理系なし）**と確定し、第3章で画面を**単一 HTML ドキュメント内の領域**と定めたため、以降の章はこの前提に従う（特に 5. ファイル操作・8.4 tecsgen との連携）。現行 Ruby/GTK 版の事実は `README-tecscde.txt`（tecscde V0.5.1）に加え、第3章以降は tecscde V0.5.1 のソース（`cdelib/*.rb` 全9ファイル・`glade/*.glade`）、第8章はさらに tecsgen 本体（`tecslib/core/*.rb`）に基づく。**ソースの実際の位置は `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`**（2026-08-01 に確認）。`tecscde` モジュールの下ではなく **`tecsgen` モジュールの下**にあり、`trunk/tecsgen/` の下に `cdelib`・`tecslib`・`flowlib`・`tecs` が並ぶ。同じ SVN 作業コピーに `ykominami-svn-2\tecscde\` も存在するが、第3〜8章が参照したのは上記の `tecsgen` 側である。

## 目次

1. [[TECSCDE外部仕様 - 01 概要]]
2. [[TECSCDE外部仕様 - 02 動作環境]]
3. [[TECSCDE外部仕様 - 03 画面構成]]
4. [[TECSCDE外部仕様 - 04 コンポーネント図の表現]]
5. [[TECSCDE外部仕様 - 05 ファイル操作]]
6. [[TECSCDE外部仕様 - 06 編集操作]]
7. [[TECSCDE外部仕様 - 07 表示機能]]
8. [[TECSCDE外部仕様 - 08 CDL 連携]]
9. [[TECSCDE外部仕様 - 09 エラーと警告]]
10. [[TECSCDE外部仕様 - 10 制約・制限]]
11. [[TECSCDE外部仕様 - 11 用語集]]

---

## Related

- [[TECSCDE内部仕様]] — 本外部仕様を実装するための内部設計（モジュール構成と責務境界、2026-08-21着手）
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]] — 同じ外部仕様に基づく、クラスベース内部設計の代替案（2026-09-05着手）
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]] — 本書を踏まえた、デスクトップアプリ（Electron/Tauri両対応）版の外部仕様（2026-09-05着手）
- [[work/active/CDLParser(tree-sitter利用)/TECSCDE外部仕様 tree-sitter反映案|TECSCDE外部仕様 tree-sitter反映案]] — tree-sitter製CDLパーサ採用の検討経緯（2026-09-13 に本書へ反映済み。規定の正は本書各章）
- [[TECS開発]] — 開発進捗全体
- [[tecsgen外部仕様]] — CDL コンパイラ外部仕様（文書スタイルの参照元）
- [[North Star]]
- [[reference/03-Resources/my-topic/wiki/tecs-tcd|TECS TCD]] — コンポーネント図の概念
- [[reference/03-Resources/my-topic/CLAUDE|TECS Wiki]] — llm-wiki 知識ベース
- [[perf/competencies/技術文書化|技術文書化]] — 仕様書作成の competency 証拠
- [[perf/competencies/ソフトウェアアーキテクチャ|ソフトウェアアーキテクチャ]] — 第2章の実行形態決定（ブラウザ単体）と、そこから導出した制約の competency 証拠

---
date: 2026-08-22
description: "tecsgen内部仕様書 第11章（エラー・警告処理）— フロー（コード生成前のエラーゲート、AppFile.update の抑制）、エラー番号体系（実際にはS/G/W/T/E/I/H/C/V/Bなど多数のプレフィックスが存在）。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 11 of 12. 2026-08-22、`tecsgen.rb`（`TECSGEN#optimize_and_generate`/`finalize`）・`syntaxobj/node.rb`・`plugin.rb`・`messages.rb`・全 `.rb` のエラーコード出現箇所を直接読んで検証・訂正。

## 11. エラー・警告処理

### 11.1 フロー

1. 構文解析中: `Generator.error/warning/info`（クラスメソッド、`bnf.y.rb`）→ `@@n_error`/`@@n_warning`/`@@n_info` をインクリメント → `Console.puts` で出力
2. 意味解析中: `Node#cdl_error(msg)`（`syntaxobj/node.rb`）→ `Generator.error2(@locale, msg)` で locale 付き出力。`@locale` は `Node#initialize` 時に `Generator.current_locale` から設定される
3. プラグイン: `Plugin#cdl_error(msg)` → `@locale` が設定されていれば即出力、未設定なら `@error_backlog` に積んで `set_locale` 呼び出し時にまとめて出力（`Node` は構文解析中に生成されるため locale を即座に持てるが、`Plugin` インスタンスはパースとは異なるタイミングで生成されるための対処）
4. **コード生成前のエラーゲート**（旧版になかった重要な分岐）: `TECSGEN#optimize_and_generate`（`tecsgen.rb` 386-390行目）は、最適化を終えた時点で `Generator.get_n_error != 0` なら `print_report` を呼んで **コード生成そのものに入らず** `exit 1` する。構文解析・意味解析でのエラーは、コード生成を「続行しつつ止める」のではなく、コード生成フェーズへの**進入自体を止める**
5. コード生成中のエラー: ゲートを通過した後の生成ループでは `cdl_error`/`Generator.error` は例外を投げず件数を増やすだけなので、個々のセルタイプ・セルの生成は最後まで続行される。汎用コード `G9999` はこの段階の I/O 失敗や想定外分岐（`generate.rb`/`pluginModule.rb` 各所）で使われる、専用コードを割り当てていない場合の共通フォールバック
6. **最終コミットの抑制**: `TECSGEN#finalize`（`tecsgen.rb` 421-428行目）は `Generator.get_n_error == 0` の場合にのみ `AppFile.update`（8.2 の `.tmp`→本ファイルの rename）を呼ぶ。コード生成中に1件でもエラーが増えていれば、生成された `.tmp` は破棄され、既存の出力ファイルは変更されない
7. `print_report`（`tecsgen.rb:192`）はエラー・警告件数のサマリを組み立てる関数で、4. の早期 exit 時と `finalize` の両方で呼ばれる。最終的な終了コードは `Generator.get_n_error != 0` なら 1、それ以外は 0（暗黙）

### 11.2 エラー番号体系

メッセージ本体は `"X9999 message $1 $2"` 形式（先頭に英字+数字のエラーコード）。`TECSMsg.get_error_message`（`messages.rb`）が正規表現 `/^[A-Z0-9]+/` でコード全体（例: `S1042`）を切り出し、ローカライズ済みメッセージテーブルにあれば置換、無ければ**ソースに書かれた英語のリテラルがそのままデフォルト表示文になる**（フォールバック設計）。`$1`, `$2` は引数で置換。warning/info も同型の `@@warning_message`/`@@info_message` テーブルと `get_warning_message`/`get_info_message` を使う別系統。

> [!note] プレフィックス文字は「重大度」ではなく「発生モジュール」を表す
> 旧版はプレフィックスを G/P/W の3種のみとしていたが、実際に全 `.rb` ファイルへ出現するコードを機械的に集計すると10種類以上ある。重大度（error/warning/info）はプレフィックス文字ではなく `cdl_error`/`cdl_warning`/`cdl_info` のどれを呼んだかで決まり、同じ `S` プレフィックスでもエラーと警告の両方が存在する。以下は出現頻度からの推定（発生源モジュールの対応表であり、文字の由来自体は未確認）。

| プレフィックス | 主な発生源（実測） | 備考 |
|--------------|------------------|------|
| `S` | `componentobj/` 配下ほぼ全ファイル（`cell.rb`/`celltype.rb`/`namespace.rb`/`join.rb`/`port.rb`/`region.rb`/`signature.rb` 等） | 意味解析エラーの大半（224件）を占める最大区分 |
| `G` | `bnf.y.rb`・`tecsgen.rb`・`pluginModule.rb` | 構文解析・全体制御・`G9999` 汎用フォールバック |
| `W` | ほぼ全ファイルに横断的に出現 | プレフィックスというより警告メッセージ（`cdl_warning`）全般、`W9999` は汎用 |
| `T` | `types.rb`・`gen_xml.rb` | 型システム関連 |
| `E` | `expression.rb` | 式評価 |
| `I` | `expression.rb`・`optimize.rb`・`cell.rb` | 情報メッセージ（`cdl_info`）関連に集中 |
| `P` | `plugin.rb`・`pluginModule.rb` | プラグイン共通 |
| `B` | `C_parser.y.rb`（`C_parser.tab.rb`） | `import_C` の C 言語サブパーサ（5.3参照） |
| `H` | `generate.rb` | 致命的内部エラー（例: `H1001 tecsgen: fatal internal error during code generation`） |
| `C` | `ctypes.rb` | `CType` モジュール関連 |
| `V` | `value.rb` | 定数値評価関連 |

---


---
date: 2026-08-22
description: "tecsgen内部仕様書 第12章（グローバル変数一覧）— 実装全体で使われるグローバル変数の一覧表。存在しない`$KCODE_CDL`等を削除し、`$force_overwrite`の説明と欠落していたテンプレート系変数を訂正。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 12 of 12. 2026-08-22、`tecsgen.rb`（`initialize_global_var`/`analyze_option`、280-340行目付近）を直接読んで全面検証・訂正。

## 12. グローバル変数一覧

> [!warning] `$KCODE_CDL` / `$KCODE_TECSGEN` は存在しない
> 旧版が挙げていた `$KCODE_CDL`（文字列 `"EUC"`）はソース中のどこにも定義されていない架空の変数だった（5章訂正時に判明）。文字コード関連の実在変数は `tecs_lang.rb` が設定する `$CHARSET_FILE`/`$CHARSET_CONSOLE`（Symbol: `:eucJP`/`:sjis`/`:utf8` 等）と `$KCONV_CDL`/`$KCONV_CONSOLE`/`$KCONV_TECSGEN`（`Kconv` 定数）であり、下表はこちらに置き換えた。

| 変数 | 型 | 初期値 | 説明 |
|------|----|--------|------|
| `$gen_base` | String | `"gen"` | 生成ディレクトリ（ベース） |
| `$gen` | String | `$gen_base` | 生成ディレクトリ（リンクルート別、`-g` で変更） |
| `$import_path` | String[] | `["."]` | CDL サーチパス（`-I` で追加、10.1 の二段探索の対象） |
| `$library_path` | String[] | `[tecsgen_base_path]` | Ruby ライブラリサーチパス |
| `$define` | String[] | `[]` | cpp マクロ定義（`-D`） |
| `$cpp` | String | `"gcc -E -DTECSGEN"`（環境変数 `TECS_CPP` があれば上書き） | C プリプロセッサコマンド（`-c`、5.3 参照） |
| `$tecspath` | String | `tecsgen_base_path/tecs`（環境変数 `TECSPATH` があれば上書き） | TECS ライブラリパス |
| `$rom` | Bool | `true`（環境変数 `TECSGEN_DEFAULT_RAM` があれば `false`） | ROM サポート（CB を分離生成、`-r` で `false` に） |
| `$unopt` | Bool | `false` | 最適化無効（`-U`） |
| `$unopt_entry` | Bool | `false` | 受け口最適化無効（`--unoptimize-entry`） |
| `$dryrun` | Bool | `false` | ドライラン（コード生成なし） |
| `$verbose` | Bool | `false` | 詳細出力 |
| `$debug` | Bool | `false` | デバッグ出力（`-t`、同時に `$verbose` も真になる） |
| `$ram_initializer` | Bool | `false` | RAM 初期化コード生成（`-R`） |
| `$idx_is_id` | Bool | `false` | 全セルタイプに idx_is_id 適用 |
| `$unique_id` | Bool | `false` | セルタイプ間で連番 ID（`-u`） |
| `$force_overwrite` | Bool | `false` | **全生成ファイル**の強制上書き（`-f`、8.2 参照。テンプレート限定ではない） |
| `$generate_all_template` | Bool | `false` | 全セルタイプの template を生成（`--generate-all-template`、8.2 参照） |
| `$generate_no_template` | Bool | `false` | template を一切生成しない（`--generate-no-template`、8.2 参照） |
| `$region_list` | Hash | `{}` | `-G` で指定したリージョン |
| `$generating_region` | Region | `nil` | 現在生成中のリンクルート（コマンドラインオプションではない） |
| `$target` | String | `"tecs"` | CDL ファイル名（拡張子除く、`ARGV[0]` から再設定される仮値） |
| `$c_suffix` | String | `"c"` | 生成ファイルの C 拡張子 |
| `$h_suffix` | String | `"h"` | 生成ファイルのヘッダ拡張子 |
| `$kcode` | String\|nil | `nil` | CDL ファイルの文字コード指定（`-k`：`euc`/`sjis`/`none`/`utf8`） |
| `$CHARSET_FILE` | Symbol\|nil | 環境変数解決後に決定（`tecs_lang.rb`） | CDL ファイルの実際の文字コード（例: `:eucJP`） |
| `$KCONV_CDL` | const | `Kconv::EUC`（`$CHARSET_FILE` 確定後に再設定） | CDL 用 `Kconv` 定数（5.1/10.2 の文字コード変換で使用） |
| `$KCONV_TECSGEN` | const | `Kconv::UTF8` | tecsgen ソース自身（メッセージ・コメント埋め込み文字列）の文字コード |

---


---
date: 2026-10-02
description: "tecsgen-python3外部仕様 第4章（出力）— 生成物はRuby版とバイト一致が受入基準。生成ファイル一覧、tecsgen.rbdmpを書かない差異、一致の確認状況（as of 2026-10-02）。"
project: tecsgen-python3
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

[[tecsgen-python3外部仕様]] の第4章（全10章）。生成ファイルの内容・マクロ・最適化の意味は [[work/active/tecsgen/tecsgen外部仕様 - 04 出力|Ruby版 第4章]]と同じです。ここでは Python 版の受入基準と差異だけを書きます。

## 4. 出力

### 4.1 受入基準（一致要件）

同じ入力・同じオプションで実行したとき、次が Ruby 版とバイト単位で一致すること。

1. `gen/`（`-g` で指定したディレクトリ）以下の全生成ファイル
2. 標準出力の内容（バナー、`-v` の経過表示を含む）
3. エラー・警告のメッセージ、コード、件数
4. 終了コード
5. エラー終了のときも、それまでに書き出されたファイル

### 4.2 生成ファイル

生成ファイルの種類は Ruby 版と同じです: `tCELLTYPE_tecsgen.h`・`tCELLTYPE_factory.h`・`tCELLTYPE_templ.c`・`tCELLTYPE_inline_templ.h`・`tecsgen.cfg`・`Makefile.templ`・`Makefile.tecsgen`・`Makefile.depend`・`global_tecsgen.h`、署名ごとの `*_tecsgen.h` など。**`CMakeLists.tecsgen.cmake`**（2026-10-05 追加。tecsgen-rb の cmake 対応）は、CMake が `include()` するソース一覧のマニフェストで、`Makefile.tecsgen` の代わりに使います。CLI オプションの追加は無く、常に出力されます。出力する変数は `TECS_IMPORT_CDLS`・`TECS_TECSGEN_SOURCES`・`TECS_PLUGIN_TECSGEN_SOURCES`・`TECS_PLUGIN_CELLTYPE_SOURCES`・`TECS_CELLTYPE_SOURCES`・`TECS_PLUGIN_EXTRA_SOURCES`・`TECS_INCLUDE_DIRS`・`TECS_COMPILE_DEFINITIONS`（常に出力）と、`TECS_LINK_OPTIONS`・`TECS_CUSTOM_COMMANDS`・プラグインが追加した行（あるときだけ出力）です。パス中の `$(GEN_DIR)` は `${TECS_GEN_DIR}`、`$(TECSPATH)` は `${ASP3_TECSGEN_DIR}/tecs`、`$(BASE_DIR)`・カレントは `${ASP3_SRCDIR}` に置き換わります（手順の詳細は内部仕様8章）。テンプレート（`_templ.c`・`_templ.h`）は `-f` を付けたときだけ上書きされ、通常は `tecsmerge` で既存コードへマージします。

### 4.3 Ruby版との差異

| 項目 | Ruby 版 | Python 版 |
|---|---|---|
| `tecsgen.rbdmp` | Ruby の `Marshal` 形式でモデルを書き出す（`tecsflow` 用） | **書かない**。`-v` で表示される経過メッセージだけ再現する。`tecsflow` を移植しないため |
| 生成物の改行 | 実行した環境の既定 | Windows でも `\n`（テストは Ruby 版を Linux で実行した結果と比べる） |

### 4.4 一致の確認状況（as of 2026-10-05）

正解データの基準は、2026-10-05 に SVN r3304 から tecsgen-rb（cmake 対応を含む）へ切り替えました。

| 区分 | ケース数 | 結果 |
|---|---|---|
| プラグインを使わないテストケース | 119 | 全件一致（`CMakeLists.tecsgen.cmake` を含む） |
| プラグインを使うテストケース（`test/` のケース、`tests/golden/kernel/` のカーネル 23 件、配布パッケージ 17 件を含む） | 77 | 全件一致（生成物・標準出力・終了コード）。配布パッケージは 2026-10-05 に再生比較の記録（p3）を採り、検証の対象に加えた |
| 比較の対象外（例外） | 1 | `transparent_marshaler`。tecsgen-rb に `TransparentMarshalerPlugin.rb` が無く再採取できないため、正解データは r3304 のまま残し、現在の出力とは比べない |

標準付属プラグインは 85 本中 83 本を移植済みで、プラグインを使う 77 ケースが一致します（2026-10-05。`TransparentRPCSignaturePlugin` を含む）。残る 2 本（`HRP2Cache`・`HRP2PostHook`）は動かす経路が無く、対象外です（[[tecsgen-python3外部仕様 - 06 プラグインシステム|6章]]）。

## Related

- [[tecsgen-python3外部仕様]] — 目次
- [[tecsgen-python3内部仕様 - 08 コード生成]] — Ruby 互換の要点（`sprintf`・改行ほか）
- [[tecsgen-python3移植計画]]

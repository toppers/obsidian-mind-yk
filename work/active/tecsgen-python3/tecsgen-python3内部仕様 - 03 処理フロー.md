---
date: 2026-10-02
description: "tecsgen-python3内部仕様 第3章（処理フロー）— cli.run から run1・run2・finalize までのフロー。Ruby版 第3章と同じ段取りで、Python版での差（RecursionError の扱い・.rbdmp を書かない・Host 経由の入出力）を示す。"
project: tecsgen-python3
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

[[tecsgen-python3内部仕様]] の第3章（全12章）。各ステップの意味と順序は、2026-08-23 に実ソースで検証済みの [[work/active/tecsgen/tecsgen内部仕様 - 03 処理フロー|Ruby版 第3章]]と同じです（`set_require_join` は `semantics_analisys_1` の最終ステップ、`check_join` の主眼は未結合・配列要素数・`size_is`・到達可能リージョン、`optimize_and_generate` は無条件に呼ばれ内部の `optimize` だけが `unopt` でガードされる、など）。ここでは Python 版の入口と差だけを書きます。

## 3. 処理フロー

### 3.1 トップレベル（`cli.run`）

```
cli.run(argv, environ)
  ├─ init(ctx, environ)
  │    ├─ initialize_global_var   # TecsgenContext の初期化（TECSGEN_DEFAULT_RAM・TECS_CPP・TECSPATH）
  │    ├─ analyze_option          # ruby_optparse によるオプション解析
  │    ├─ load_modules            # TECS_LANG.setup（言語・文字コード）ほか
  │    └─ setup                   # インポートパス調整・gen ディレクトリ作成（tecsflow でないとき）
  ├─ tecsgen = TECSGEN()
  ├─ tecsgen.run1()               # 構文解析 + 意味解析1・2
  ├─ tecsgen.run2()               # 最適化 + コード生成 + finalize
  └─ tecsgen.dump_tecsgen_rbdmp() # 経過表示だけ再現。.rbdmp は書かない
```

終了コードは `run` の戻り値（`__main__` が `sys.exit`）。`--help`・`--version` は `init` の中で表示して終わる。

### 3.2 run1・run2

- **run1** = `syntax_analisys` → `semantics_analisys_1` → `semantics_analisys_2`
  - 構文解析は Ruby 版と同じく、パース中の文法アクションがモデルを直接組み立てる（5章）。プラグインの `gen_cdl_file` もパース中に呼ばれる
  - 意味解析1の中で、ポストコード（`tmp_plugin_post_code.cdl`）を生成して再度パースする
- **run2** = `optimize_and_generate` → `finalize`
  - エラーが 1 件でもあれば、生成の前に報告して終了コード 1 で終わる
  - `finalize` が、変更があったファイルだけを上書きする（`.tmp` → 比較 → リネーム、10章）

### 3.3 例外とエラー終了

| 事象 | Ruby 版 | Python 版 |
|---|---|---|
| 想定内の終了（`exit`） | `exit n` | `TecsgenExit` を送出し、`run` が `status` を戻り値にする |
| 想定外の例外 | `rescue => evar` で報告して 1 | `except Exception` で同じ3行のメッセージを出して 1 |
| スタックオーバーフロー | `SystemStackError`（`StandardError` ではないので `rescue` に捕まらない） | `RecursionError` を捕まえ、標準出力はそのまま、標準エラーに例外名の行を出して 1（バックトレースは再現しない） |

### 3.4 入出力

ファイル・カレントディレクトリ・外部コマンド（cpp）は、すべて `Host`（`get_host()`）を通す。通常は実ファイルシステムに触る `Host`、差分テストでは記録を再生する `RecordedHost`。標準出力への書き込みは `ruby_compat.rb_print`・`rb_puts` を使い、改行は常に LF。

## Related

- [[tecsgen-python3内部仕様]] — 目次
- [[tecsgen-python3内部仕様 - 06 意味解析]]・[[tecsgen-python3内部仕様 - 07 最適化]]・[[tecsgen-python3内部仕様 - 08 コード生成]]
- [[tecsgen-python3内部仕様 - 10 ファイル入出力]]

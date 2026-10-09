---
date: 2026-10-02
description: "tecsgen-python3外部仕様 第7章（エラーと警告）— メッセージ書式・エラー番号・件数サマリはRuby版と一致、Ruby版が例外で落ちる場面の再現、Python版固有のメッセージの扱い。"
project: tecsgen-python3
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

[[tecsgen-python3外部仕様]] の第7章（全10章）。メッセージの書式とカテゴリは [[work/active/tecsgen/tecsgen外部仕様 - 07 エラーと警告|Ruby版 第7章]]と同じです。

## 7. エラーと警告

### 7.1 一致要件

| 項目 | 内容 |
|---|---|
| 書式 | `ファイル名:行番号:列番号: error: メッセージ`（位置が無いときは `error: メッセージ`）、`warning`・`info` も同じ |
| エラー番号 | S・G・W・T・E・I・P・B・H・C・V の各プレフィックスと番号を Ruby 版と同じにする（例 `S1142`・`G1016`・`P2001`）。メッセージ表は Ruby 版から生成 |
| 件数サマリ | 処理終了時の `N errors` などの行 |
| 順序 | 出る順序も Ruby 版と同じ（パース中の副作用の順序まで再現） |
| 終了コード | エラーがあれば 1 |

### 7.2 Ruby 版が例外で落ちる場面

Ruby 版が例外で異常終了する入力でも、標準出力の内容と終了コードを同じにします。

- スタックオーバーフロー（例: 属性の式が循環する CDL）: Ruby 版は `SystemStackError`。Python 版は `RecursionError` を捕まえ、同じ標準出力と終了コード 1 にする。標準エラー出力は例外名の行だけ合わせ、バックトレースは一致しない
- `tecsmerge` の `-f` を `-p` より前に書くなどの例外: メッセージの先頭の行と終了コード 1 を合わせる。バックトレースは一致しない

### 7.3 Ruby版との差異

| 項目 | 内容 |
|---|---|
| バックトレース | Ruby 版の例外のバックトレースは再現しない |
| `--help` の不正オプション | `invalid option: ...` などの文言は Ruby の `optparse` と同じ書式 |
| 未移植プラグインを指定したとき | プラグインのファイルが無いときのエラー（P2001）になる（[[tecsgen-python3外部仕様 - 06 プラグインシステム\|6章]]） |

## Related

- [[tecsgen-python3外部仕様]] — 目次
- [[tecsgen-python3内部仕様 - 11 エラー・警告処理]]

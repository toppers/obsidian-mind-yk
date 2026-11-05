---
date: 2026-10-02
description: "tecsgen-python3外部仕様 第3章（入力）— CDLファイル、文字コード、Cプリプロセッサ連携。受理するCDLとエラーの出方はRuby版と一致、差異なし。"
project: tecsgen-python3
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

[[tecsgen-python3外部仕様]] の第3章（全10章）。CDL の記述要素と対応バージョンは [[work/active/tecsgen/tecsgen外部仕様 - 03 入力|Ruby版 第3章]]と同じです（CDL 言語の仕様は CDL リファレンスマニュアルの範囲で、tecsgen の版に従います）。

## 3. 入力

### 3.1 CDL ファイル

- 拡張子 `.cdl`。複数ファイルを指定した場合は指定順に import される
- 文字エンコーディングは UTF-8 が既定。`-k`（`--kcode`）または環境変数 `TECSGEN_FILE_LANG` で `euc`・`sjis`・`none`・`utf8` を指定できる（`sjis` のときは Ruby 版と同じく、Windows-31J として不正なバイト列を含む CDL は `G1014`、Shift_JIS に無い文字（`～`・`∥`・丸数字・`㈱` など）が出力に入ると `H1001` で終了コード 1 になる。2026-10-04 に Ruby 3.2.3 と一致を確認）

### 3.2 解析結果の一致要件

字句解析と構文解析は、Ruby 版の字句解析器と、Ruby 版の racc が生成した LALR 表を取り出したものを使います（[[tecsgen-python3 構文解析方式決定]]）。このため次が Ruby 版と一致します。

| 項目 | 一致する内容 |
|---|---|
| 受理する CDL | 同じ範囲（`import_C` の C ヘッダも同様） |
| 構文エラー | 位置（行・列）、件数、エラー回復後のメッセージ |
| 意味解析 | エラー・警告の種類、件数、出る順序 |

確認は、Ruby 版の実行結果を正解とする差分テスト（`tests/golden/`）で行います。Ruby 版が例外で落ちる入力（例: `attribute-err` のスタックオーバーフロー）でも、標準出力・終了コード 1 を同じにします。

### 3.3 C プリプロセッサ連携

`import_C` ディレクティブで C ヘッダを取り込むとき、C プリプロセッサを外部コマンドとして呼びます。

- 既定のコマンド: `gcc -E -DTECSGEN`
- `-c` オプションまたは環境変数 `TECS_CPP` で変更（両方あれば環境変数が既定値を、`-c` がそれをさらに上書きする。Ruby 版と同じ）
- `-D`・`-I` でマクロ定義とインクルードパスを追加

### 3.4 Ruby版との差異

なし（入力の受理範囲に差異は無い）。ただし、プラグインを指定する CDL では、利用者が書いたプラグインを Python で書く必要がある（[[tecsgen-python3外部仕様 - 06 プラグインシステム|6章]]）。

## Related

- [[tecsgen-python3外部仕様]] — 目次
- [[tecsgen-python3内部仕様 - 05 字句解析・構文解析]] — 実装の詳細

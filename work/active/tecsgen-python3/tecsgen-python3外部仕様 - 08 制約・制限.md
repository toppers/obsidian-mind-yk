---
date: 2026-10-02
description: "tecsgen-python3外部仕様 第8章（制約・制限）— CDL・生成コードの制約はRuby版と同じ。Python版固有の制限: プラグイン2本は対象外・tecsflow非対応・Ruby製プラグイン非互換・Cygwin未検証（macOSはテスト一式まで確認済み）。"
project: tecsgen-python3
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

[[tecsgen-python3外部仕様]] の第8章（全10章）。CDL と生成コードに関する制約は [[work/active/tecsgen/tecsgen外部仕様 - 08 制約・制限|Ruby版 第8章]]（8.1・8.2）と同じです。

## 8. 制約・制限

### 8.1 CDL・生成コードの制約

Ruby 版と同じ（`C_EXP` の使い方、`INITIALIZE_TECS()` を main の先頭で呼ぶこと、ファイル名とセルタイプ名の一致、`_tecsgen.h` を最初に include するなど）。

### 8.2 Ruby版と同じ既知の制限

`-g` で階層ディレクトリを指定するときの事前作成、可変長呼び口配列の最適化、`-G` とリンクルートの関係は Ruby 版と同じです。

### 8.3 Python 版固有の制限（as of 2026-10-02）

| 制限 | 内容 |
|---|---|
| 未移植のプラグイン | 2 本（`HRP2Cache`・`HRP2PostHook`）。Ruby 版の標準付属の CDL から参照されず、動かす経路が無いため移植しない。これらを CDL で指定すると P2001 になる（[[tecsgen-python3外部仕様 - 06 プラグインシステム\|6章]]） |
| Ruby 製の利用者プラグイン | 動かない。Python で書き直す必要がある |
| `RUBYLIB` | 対応しない |
| `tecsgen.rbdmp` | 書かない。`tecsflow`・`tcflow`・旧 `tecscde` は対象外 |
| 動作確認 OS | Windows 11 と WSL（Linux）。macOS は 2026-10-04 に GitHub Actions で確認済み（テスト一式とバージョン表示。詳細は [[tecsgen-python3外部仕様 - 02 動作環境]]） |
| 正解データの範囲 | Ruby 版との一致は、`tests/golden/` にあるプラグイン不使用 119 ケースとプラグイン使用 85 ケース（カーネル 23 件、配布パッケージ 17 件、`CMake.add_*` を呼ぶケース 8 件を含む。as of 2026-10-09）で確認。それ以外の入力は未確認 |
| `-L` のコード実行 | 指したディレクトリの Python コードをそのまま実行する。信頼できるディレクトリだけを指定すること |

## Related

- [[tecsgen-python3外部仕様]] — 目次
- [[tecsgen-python3移植計画]] — 未移植の扱い

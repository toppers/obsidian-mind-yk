---
date: 2026-10-02
description: "tecsgen-python3外部仕様 第10章（用語集）— CDL言語の用語はRuby版を参照し、Python版の差分に出てくる用語（正解データ・オラクル・利用者プラグインなど）を定義。"
project: tecsgen-python3
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

[[tecsgen-python3外部仕様]] の第10章（全10章）。CDL 言語一般の用語（セル、セルタイプ、呼び口、受け口、シグニチャ、CELLCB、ファクトリ、composite、namespace、region、restrict、動的結合など）は [[work/active/tecsgen/tecsgen外部仕様 - 10 用語集|Ruby版 第10章]]を参照してください。ここには、この仕様書に出てくる Python 版固有の用語だけを定義します。

## 10. 用語集

| 用語 | 定義 |
|------|------|
| 正解データ | Ruby 版を実行して採った入力と出力の記録（`tests/golden/`）。移植の受入基準の基準になる |
| オラクル | Ruby 版を実際に実行して、内部状態（モデル、Namespace への問い合わせ）を記録する仕組み（`tests/ruby/p3_oracle.rb`）。Python 版は記録を再生して比べる |
| 一致 | 生成物がバイト単位で等しく、標準出力・エラー・警告・終了コードも等しいこと |
| 利用者プラグイン | `-L` で指すディレクトリに置く、利用者が書いた Python のプラグイン（`<クラス名>.py`） |
| 組み込みプラグイン | パッケージに同梱された標準付属プラグイン（`tecsgen.plugin`）。利用者プラグインで上書きできない |
| 未移植プラグイン | Ruby 版にあるが Python 版にまだ無いプラグイン（[[tecsgen-python3外部仕様 - 06 プラグインシステム\|6章]]） |
| TECSPATH | 標準 CDL ライブラリ（`tecs/`）の場所。未設定ならパッケージ同梱のもの |
| tecsmerge | 生成テンプレートを保守中のセルタイプコードにマージするコマンド |

## Related

- [[tecsgen-python3外部仕様]] — 目次
- [[tecsgen外部仕様]] — Ruby 版（CDL 用語の正本）

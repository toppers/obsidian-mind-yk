---
date: 2026-09-21
description: "tecsgen-python3（Ruby版tecsgenのPython3移植）外部仕様書の目次。Ruby版 tecsgen外部仕様 の全10章構成に対応し、全10章を章別ノートとして執筆済み（2026-10-02）。"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
  - index
---

# tecsgen-python3 外部仕様

> [!info] 文書状態
> **全10章を執筆済み（2026-10-02）** — 章別ノートに分割。Ruby 版 [[tecsgen外部仕様]] と章番号・章名を揃え、Python 版の差異（動作環境・`-L`・`RUBYLIB`・`tecsgen.rbdmp`・プラグインの移植状況）は各章の「Ruby版との差異」に書いた。事実はコードベース（`E:/Ccur/python3/tecsgen-python3`）で確認済み。執筆時に (TBC) を付けた箇所は、2026-10-04 までにすべて確認して解消した。そのため (TBC) の印は残っていないが、未確認のまま明記している事項は、Cygwin と macOS での実際の CDL 利用が [[tecsgen-python3外部仕様 - 02 動作環境|2章]]、正解データの範囲外の入力が [[tecsgen-python3外部仕様 - 08 制約・制限|8章]]、権限無しエラーの文言が [[tecsgen-python3内部仕様 - 05 字句解析・構文解析|内部仕様5章]]に書いてある。

Ruby 実装の [[tecsgen外部仕様]] が全10章・章別ノート分割済みのため、本書も同じ10章構成を採る。章番号・章名を一致させ、Python3 版で差異が生じる箇所のみ各章内に「Ruby版との差異」節を設けて記述する方針。

## 目次（Ruby版対応表）

| 章 | 章名 | Ruby版（移植元） | 状態 |
|---|---|---|---|
| 1 | 概要 | [[work/active/tecsgen/tecsgen外部仕様 - 01 概要\|01 概要]] | **執筆済み** → [[tecsgen-python3外部仕様 - 01 概要\|1章]] |
| 2 | 動作環境 | [[work/active/tecsgen/tecsgen外部仕様 - 02 動作環境\|02 動作環境]] | **執筆済み** → [[tecsgen-python3外部仕様 - 02 動作環境\|2章]] |
| 3 | 入力 | [[work/active/tecsgen/tecsgen外部仕様 - 03 入力\|03 入力]] | **執筆済み** → [[tecsgen-python3外部仕様 - 03 入力\|3章]] |
| 4 | 出力 | [[work/active/tecsgen/tecsgen外部仕様 - 04 出力\|04 出力]] | **執筆済み** → [[tecsgen-python3外部仕様 - 04 出力\|4章]] |
| 5 | コマンドラインインターフェース | [[work/active/tecsgen/tecsgen外部仕様 - 05 コマンドラインインターフェース\|05 CLI]] | **執筆済み** → [[tecsgen-python3外部仕様 - 05 コマンドラインインターフェース\|5章]] |
| 6 | プラグインシステム | [[work/active/tecsgen/tecsgen外部仕様 - 06 プラグインシステム\|06 プラグインシステム]] | **執筆済み** → [[tecsgen-python3外部仕様 - 06 プラグインシステム\|6章]] |
| 7 | エラーと警告 | [[work/active/tecsgen/tecsgen外部仕様 - 07 エラーと警告\|07 エラーと警告]] | **執筆済み** → [[tecsgen-python3外部仕様 - 07 エラーと警告\|7章]] |
| 8 | 制約・制限 | [[work/active/tecsgen/tecsgen外部仕様 - 08 制約・制限\|08 制約・制限]] | **執筆済み** → [[tecsgen-python3外部仕様 - 08 制約・制限\|8章]] |
| 9 | 使用例 | [[work/active/tecsgen/tecsgen外部仕様 - 09 使用例\|09 使用例]] | **執筆済み** → [[tecsgen-python3外部仕様 - 09 使用例\|9章]] |
| 10 | 用語集 | [[work/active/tecsgen/tecsgen外部仕様 - 10 用語集\|10 用語集]] | **執筆済み** → [[tecsgen-python3外部仕様 - 10 用語集\|10章]] |

章別ノート（`tecsgen-python3外部仕様 - NN 章名.md`）に分割済み（2026-10-02）。

## Notes

### Ruby版との差異が出る見込みの箇所（執筆前の見込み。2026-10-03 時点で、各章に反映済み。実際の差異は各章の「Ruby版との差異」を見る）

- **動作環境（2章）** — Ruby 処理系ではなく Python3 処理系。Python 3.13.11 以上、実行時の依存パッケージなしに確定（[[tecsgen-python3外部仕様 - 02 動作環境]]）。
- **入力の解析系（3章）** — 2026-09-27、Python3 版も Ruby 版の racc の表をそのまま使う方式に決定（[[tecsgen-python3 構文解析方式決定]]。当初の tree-sitter 案は、受理する CDL の範囲と構文エラーの出方が変わるためやめた）。受理する CDL の範囲・構文エラーの位置と件数は Ruby 版と一致する（差分テストで確認済み）。外部仕様上の差異は無い
- **CLI（5章）** — **Ruby 版と完全互換にすることに決定**（2026-09-26、[[tecsgen-python3 P0基本方針決定]]）。一覧の正本は `tecsgen.rb` の `analyze_option`。**例外が1つある**: 環境変数 `RUBYLIB`（Ruby 版では `-L` と同等）は対応しない。代わりの環境変数も作らない（2026-10-01 決定、[[tecsgen-python3 -L ユーザプラグイン探索設計]]）。`-L` は引き続き使え、探す対象は `<クラス名>.py` になる。
- **`-L` と利用者プラグイン（5・6章）** — 2026-10-01 実装済み。`-L` のディレクトリ（複数指定可）から、組み込みの後に `<クラス名>.py`・`tecslib/plugin/<クラス名>.py` を探す。組み込みと同名のプラグインは `-L` で上書きできない。ロードに失敗すると P2003、ファイルが無ければ P2001（Ruby 版と同じ番号）。プラグインは基底クラスを `tecsgen.plugin.*` から明示的に import する。`-L` で指したディレクトリのコードをそのまま実行する（Ruby 版と同じ信頼モデル）。仕様は [[tecsgen-python3内部仕様 - 09 プラグイン機構]]。
- **プラグインシステム（6章）** — プラグインの記述言語が Ruby から Python3 に変わるため、呼び出し規約・引数文法の外部仕様が変わる。詳細は [[tecsgen-plugins-python3]] 側。
- **出力（4章）** — 生成コードは Ruby 版と一致させるのが移植の受入基準（生成物の差分ゼロ）。ここは差異ではなく一致要件として書く。

## Action Items

- [x] 全10章を執筆（2026-10-02）
- [x] 実装が進んだら更新: 6章のプラグイン移植状況（85 本中 83 本、残り2本は対象外）と一致ケース数（77、2026-10-05 の P7 で基準を tecsgen-rb に切り替えた後の値）、8章の正解データの範囲、4章の一致ケース数、2章の macOS 検証（2026-10-04）を反映（2026-10-09）

## Context

- [[tecsgen-python3]] — 親ノート、作業全体の進捗管理
- [[tecsgen外部仕様]] — Ruby 実装版の外部仕様（移植元・章立ての基準）
- [[tecsgen-python3内部仕様]] — 本書に対応する内部仕様（未執筆）
- Python3版最新コード `E:/Ccur/python3/tecsgen-python3`
- Ruby版最新コード `E:/Crepo/toppers-tecs-svn/toppers/tecsgen/branches/ykominami_r3033`

## Related

- [[tecsgen-python3]]
- [[tecsgen外部仕様]] — Ruby実装版の外部仕様（参考）
- [[tecsgen]] — Ruby実装版（移植元）
- [[tecsgen-plugins-python3]] — プラグイン側仕様書
- [[TECS開発]] — 開発進捗全体

---
date: 2026-09-21
description: "tecsgen-python3（Ruby版tecsgenのPython3移植）内部仕様書の目次。Ruby版 tecsgen内部仕様 の全12章構成に対応。4〜8・10〜12章をフェーズの実装に合わせて執筆中（2026-09-27時点）"
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

# tecsgen-python3 内部仕様

> [!info] 文書状態
> **全12章を執筆済み（2026-10-02）** — 章立てを Ruby 版 [[tecsgen内部仕様]] に合わせて確定（2026-09-22）。[[tecsgen-python3移植計画]] の方針どおり、フェーズの実装に合わせて章を書く。P1 で10・11・12章の該当範囲、P2 で5章、P3 で4・6章と5・12章の追記、P4 で7・8章を執筆した。2026-10-02（P6e）に1〜3章を執筆し、全12章がそろった。構文解析は tree-sitter をやめ、Ruby 版の racc の表を使う方式に変えた（[[tecsgen-python3 構文解析方式決定]]、2026-09-27）。

移植元 Ruby 実装の [[tecsgen内部仕様]] は全12章・章別ノート分割済みで、各章は実ソース直読みによる検証パスを一巡している（2026-08-23 時点）。本書も同じ12章構成を採り、章番号・章名を一致させる。Python3 版で実装が変わる箇所は各章内に「Ruby版との差異」節を設けて記述する。

対象は Ruby 版 v1.9.1 相当（`branches/ykominami_r3033`、trunk と byte-for-byte 一致を確認済み — Ruby版内部仕様の記載による）。

## 目次（Ruby版対応表）

| 章 | 章名 | Ruby版（移植元） | 移植の性格 | 状態 |
|---|---|---|---|---|
| 1 | 概要 | [[work/active/tecsgen/tecsgen内部仕様 - 01 概要\|01 概要]] | 書き下ろし | **執筆済み** → [[tecsgen-python3内部仕様 - 01 概要\|1章]] |
| 2 | ソースファイル構成 | [[work/active/tecsgen/tecsgen内部仕様 - 02 ソースファイル構成\|02 ソースファイル構成]] | ほぼ踏襲（Ruby と1ファイル対1モジュール、[[tecsgen-python3 パッケージ構成決定\|対応表]]） | **執筆済み** → [[tecsgen-python3内部仕様 - 02 ソースファイル構成\|2章]] |
| 3 | 処理フロー | [[work/active/tecsgen/tecsgen内部仕様 - 03 処理フロー\|03 処理フロー]] | ほぼ踏襲 | **執筆済み** → [[tecsgen-python3内部仕様 - 03 処理フロー\|3章]] |
| 4 | クラス設計 | [[work/active/tecsgen/tecsgen内部仕様 - 04 クラス設計\|04 クラス設計]] | ほぼ踏襲（mixin は多重継承） | **P3 範囲を執筆** → [[tecsgen-python3内部仕様 - 04 クラス設計\|4章]]（最適化・生成・プラグインは P4・P5） |
| 5 | 字句解析・構文解析 | [[work/active/tecsgen/tecsgen内部仕様 - 05 字句解析・構文解析\|05 字句解析・構文解析]] | 踏襲（Ruby の字句解析器と racc の表をそのまま移植。2026-09-27 に tree-sitter から変更） | **執筆済み** → [[tecsgen-python3内部仕様 - 05 字句解析・構文解析\|5章]]（P2・文法アクションは P3） |
| 6 | 意味解析 | [[work/active/tecsgen/tecsgen内部仕様 - 06 意味解析\|06 意味解析]] | ほぼ踏襲 | **P3 範囲を執筆** → [[tecsgen-python3内部仕様 - 06 意味解析\|6章]] |
| 7 | 最適化 | [[work/active/tecsgen/tecsgen内部仕様 - 07 最適化\|07 最適化]] | ほぼ踏襲 | **執筆済み（P4）** → [[tecsgen-python3内部仕様 - 07 最適化\|7章]] |
| 8 | コード生成 | [[work/active/tecsgen/tecsgen内部仕様 - 08 コード生成\|08 コード生成]] | 踏襲（生成物の一致が受入基準） | **執筆済み（P4。プラグイン生成部分は P5）** → [[tecsgen-python3内部仕様 - 08 コード生成\|8章]] |
| 9 | プラグイン機構 | [[work/active/tecsgen/tecsgen内部仕様 - 09 プラグイン機構\|09 プラグイン機構]] | **全面差替**（Ruby 動的ロード → Python import） | **ロードと `-L` 探索を執筆（P5q）** → [[tecsgen-python3内部仕様 - 09 プラグイン機構\|9章]]（残りは [[tecsgen-plugins-python3]] と分担） |
| 10 | ファイル入出力 | [[work/active/tecsgen/tecsgen内部仕様 - 10 ファイル入出力\|10 ファイル入出力]] | 一部差替（文字コード変換） | **P1 範囲を執筆** → [[tecsgen-python3内部仕様 - 10 ファイル入出力\|10章]] |
| 11 | エラー・警告処理 | [[work/active/tecsgen/tecsgen内部仕様 - 11 エラー・警告処理\|11 エラー・警告処理]] | 踏襲（エラー番号体系を維持） | **P1 範囲を執筆** → [[tecsgen-python3内部仕様 - 11 エラー・警告処理\|11章]] |
| 12 | グローバル変数一覧 | [[work/active/tecsgen/tecsgen内部仕様 - 12 グローバル変数一覧\|12 グローバル変数一覧]] | **全面差替**（Ruby グローバル変数 → 設定オブジェクト） | **P1・P3 分の対応表と書き方規約** → [[tecsgen-python3内部仕様 - 12 グローバル変数一覧\|12章]]（以降のフェーズで追記） |

執筆が進み本書が 25KB を超えた時点で、Ruby 版と同様に `tecsgen-python3内部仕様 - NN 章名.md` へ章別分割する。

## Notes

### Ruby版との差異が出る見込みの箇所（執筆前の見込み。2026-10-03 時点で、すべて決定・実装済みで各章に反映済み。実際の差異は各章の「Ruby版との差異」を見る）

- **5章 字句解析・構文解析** — ~~tree-sitter 製パーサを使うため構造ごと書き直し~~ → **2026-09-27、racc の表をそのまま使う方式に変更**（[[tecsgen-python3 構文解析方式決定]]）。Ruby 版と同じくパース中にアクションがモデルを直接組み立てるので、中間の構文木の契約は不要になった。
- **9章 プラグイン機構** — Ruby 版は `plugin.rb`/`pluginModule.rb` による動的ロードと `MultiPlugin` ディスパッチ（`MultiPlugin < Node` であり `Plugin` の子ではない）。Python3 版はプラグインを Python モジュールとして import する形になるため、ロード規約・名前解決・`MultiPlugin` 相当の扱いを再設計。詳細は [[tecsgen-plugins-python3]] 側と分担。
- **12章 グローバル変数一覧** — Ruby 版は `$force_overwrite`・`$CHARSET_FILE`・`$KCONV_TECSGEN` 等のグローバル変数で実装全体の状態を持つ。Python3 版で同じ形は採らない見込みで、設定オブジェクト／モジュール定数への写像表として書き直す。
- **2章 ソースファイル構成** — **Ruby 版と1ファイル対1モジュールで対応させることに決定**（2026-09-26、[[tecsgen-python3 パッケージ構成決定]]）。再オープンされたクラスは機能別の mixin にする。2章は同ノートの対応表を中心に書く。
- **4章 クラス設計** — Ruby の mixin（`Importable` 等）は**多重継承で写すことに決定**（2026-09-26、[[tecsgen-python3 P0基本方針決定]]）。MRO は include を書いた順の逆に並べる。
- **12章 グローバル変数** — **1つの設定オブジェクトへ集約することに決定**（2026-09-26、同上）。プラグインから参照する方法も `get_context()` に決まった（[[tecsgen-python3内部仕様 - 12 グローバル変数一覧]]、2026-10-03）。
- **10章 ファイル入出力** — Ruby 版の `TECSIO`（`bnf.y.rb` 内蔵）による文字コード変換は Python3 の標準 codecs へ置換。`.tmp`→比較→リネームによる更新抑制（`AppFile` 側）は挙動として維持する。
- **8章 コード生成 / 11章 エラー・警告処理** — 生成物とエラー番号体系（S/G/W/T/E/I/P/B/H/C/V の各プレフィックス）は Ruby 版と一致させるのが移植の受入基準。差異ではなく一致要件として書く。

### 移植時に持ち込んではいけない Ruby 版の既知の問題

Ruby版内部仕様 9.7「既知の問題」に3件が記録されている（`TransparentRPCSignaturePlugin` 参照切れ、FMP の RPC 死コード、CppIfGen の二重無効化コード。いずれも実行時の再現確認なし）。Python3 版へ機械的に移植すると同じ欠陥を引き継ぐため、9章執筆時に扱いを決める。（**2026-10-05 追記**: `TransparentRPCSignaturePlugin` の参照切れは、r3304 の問題だった。tecsgen-rb には `TransparentRPCSignaturePlugin.rb` があり、Python 版も移植して解消した。詳細は [[tecsgen-python3 cmake対応計画]]。FMP・CppIfGen の2件は未確認のまま）

## Action Items

- [x] 1〜3章を執筆（2026-10-02）。全12章がそろった
- [ ] 各フェーズの実装が進んだら更新: 4章（プラグインの再オープン部分）、9章（プラグインの移植状況。2026-10-03 時点で 85 本中 83 本を移植、残り2本は対象外）、12章（残りのグローバル変数）
- [x] 10章の `-k` の差異（`-k euc` で UTF-8 リテラルが混ざる、`-k sjis` で Shift_JIS に無い文字が H1001、不正バイト列が G1014）を Python 版で再現した（2026-10-04、Python 版リポジトリのブランチ `ykominami/fix-kcode-differences`、コミット `d062f91`）

## Context

- [[tecsgen-python3]] — 親ノート、作業全体の進捗管理
- [[tecsgen内部仕様]] — Ruby 実装版の内部仕様（移植元・章立ての基準、全12章検証パス一巡済み）
- [[tecsgen-python3外部仕様]] — 本書に対応する外部仕様（全10章執筆済み）
- Python3版最新コード `E:/Ccur/python3/tecsgen-python3`
- Ruby版最新コード `E:/Crepo/toppers-tecs-svn/toppers/tecsgen/branches/ykominami_r3033`

## Related

- [[tecsgen-python3]]
- [[tecsgen内部仕様]] — Ruby実装版の内部仕様（参考）
- [[tecsgen-python3外部仕様]] — 外部から見た仕様
- [[tecsgen]] — Ruby実装版（移植元）
- [[tecsgen-plugins-python3]] — プラグイン側仕様書
- [[TECS開発]] — 開発進捗全体

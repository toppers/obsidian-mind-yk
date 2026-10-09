---
date: 2026-10-03
description: "tecsgen-python3移植計画のうち完了済みフェーズP3（型・値・式・コンポーネントモデルと意味解析）・P4（最適化とコード生成）の詳細をverbatim分離したアーカイブ。25KB閾値による分割"
project: tecsgen-python3
status: completed
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - plan
---

# tecsgen-python3移植計画 Archive — P3–P4

[[tecsgen-python3移植計画]] の P3・P4 の節を、25KB 閾値のため verbatim で分離したもの（2026-10-03）。P0〜P2 は [[tecsgen-python3移植計画 Archive — P0–P2]]。

### P3 型・値・式・コンポーネントモデルと意味解析

- **P2 から移した作業**: 文法アクション本体の移植、`Import`・`Import_C`、TYPE_NAME の判定を `Namespace` につなぐ。最初の合格条件は「全テスト CDL で、パース直後のモデル JSON とエラー集合が Ruby 版と一致する」

- `types.rb`・`value.rb`・`expression.rb`（42KB。C の式評価、整数の桁あふれや型昇格の扱いに注意）・`componentobj/*`
- `semantics_analisys_1`/`_2`: `set_definition_join`、ポストコード生成、`create_reverse_join`、`set_require_join`、`check_join` など（内部仕様 3.2・6章）
- 合格条件: 意味解析後のモデル JSON とエラー集合が一致する

**進捗（as of 2026-09-27）**: 実装・検証済み。`main` にコミット・push 済み（2026-09-27）: P3a 比較基盤 `608cf30`、オラクル再採取 `e35ff74`、P3b 型・値・式 `67945a2`、P3c コンポーネントモデル `d6406f8`、P3d 文法アクション `aa02fe4`、P3e 意味解析と CLI `3101fc6`、README・`wsl_check --oracle` `02f1a46`。

- 検証結果（Windows）: `tests/test_p3_model.py` はプラグインを読まない 119 ケースすべてで、parse 直後・`semantics_analisys_1` 後・`semantics_analisys_2` 後の3チェックポイントのモデル JSON と出力が Ruby 版と一致。プラグインを読む 35 ケースは P5 まで対象外（ユーザー決定）。`ErrorCase/attribute-err` は `tests/test_p3_cli.py` で Ruby と同じ落ち方（stdout 一致・終了コード1・stderr に `SystemStackError`）を確認。全体は Windows 789 passed / 36 skipped、WSL 784 passed / 41 skipped（WSL で多い分は Ruby を要する P1 のテスト）。`ruff`・`ty` とも両環境で通過
- 仕様: [[tecsgen-python3内部仕様 - 04 クラス設計|4章]]・[[tecsgen-python3内部仕様 - 06 意味解析|6章]]を新規執筆、[[tecsgen-python3内部仕様 - 05 字句解析・構文解析|5章]]・[[tecsgen-python3内部仕様 - 12 グローバル変数一覧|12章]]に追記
- Ruby 互換の要点: Ruby の Symbol を `str` と区別する `Symbol` クラス（`Y.NAME` で書く）、同名のクラスメソッドとインスタンスメソッドを持つ `dualmethod`、未代入の ivar を nil として返す `Node.__getattr__`。Ruby 版の癖（`! x.instance_of? Port || ...` の優先順位、`when` の末尾カンマ、`ParamList#to_str` の TypeError など）もそのまま再現した
- 持ち越し: `TOOL_INFO` は P4（→ P4 で P5 へ再持ち越し）、プラグインは P5。`--help` の書式と `-v` の Ruby バージョン行は差が残る（TBC → **解消**、P6b: `--help` は Ruby 版とバイト一致。`-v` の差は Ruby バージョン行と同梱 CDL のインストール先パスだけで、意図した差。[[tecsgen-python3外部仕様 - 05 コマンドラインインターフェース]]、2026-10-03 確認）

### P4 最適化とコード生成

- `optimize.rb`（内部仕様 7章。CALL/ENTRY で最適化フラグの初期値が逆になっている点も再現する）
- `generate.rb` 5,399行 → 生成物ごとにモジュールを分ける（`_tecsgen.h`・`_factory.h`・`_templ.c`・`global_tecsgen.h`・`tecsgen.cfg`・Makefile 類）
- バイト単位で一致させるうえでの注意: Ruby の `sprintf`/`to_s`/`inspect` と Python の数値・文字列書式の違い、ハッシュの反復順（どちらも挿入順）、`sort` の安定性（Ruby は不安定、Python は安定）、改行コード
- 合格条件: プラグインを使わないテストケースで `gen/` がバイト単位で一致する
- **比較基盤（2026-09-27 ユーザー採用）**: 新しく作らず、P3 のオラクル（`tests/ruby/p3_oracle.rb`）と記録を再生する `RecordedHost`（`tests/p3_oracle_data.py`）を土台にする。~~オラクルに生成物の記録を足し~~ → 実装時に不要と分かった: P3 の記録は run 全体を通して採っているので生成中の問い合わせも入っており、生成物の正解は `tests/golden/cases/` にある。**記録の採り直しなしで**、`RecordedHost` に書かれた内容を正解データと比べる

**進捗（as of 2026-09-27）**: 実装・検証済み。`main` にコミット `3964ec3`（2026-09-27 push 済み）。プラグインを使わない **119ケースすべてで一致**（正常終了75件の `gen/` がバイト単位で一致、エラー終了44件の標準出力・終了コード・途中のファイルが一致）。pytest 908 passed / 72 skipped（Windows）・903 passed / 77 skipped（WSL。多い分は Ruby を要する P1 のテスト）、`ruff`・`ty` とも両環境で通過。
- 実装: `core/optimize.py`、`core/generate.py`（Namespace・Signature・型）、`core/generate_celltype{,_ph,_cell,_templ}.py`（Celltype）、`TECSGEN.run2`・`finalize`・`dump_tecsgen_rbdmp`（`.rbdmp` は書かないが `-v` の経過は再現）、出力をすべて `Host` 経由に。テスト `tests/test_p4_gen.py`・一覧 `tools/port/p4_progress.py`
- 見つけた Ruby 互換の要点: `sprintf` の `%s` の幅は CDL 由来のバイナリ文字列ではバイト数（Shift_JIS 指定時は文字数）、`%d` は数値文字列を受け付ける、`[][0]` は nil、正規表現の `^`・`$` は行単位。詳細は [[tecsgen-python3内部仕様 - 08 コード生成#8.3 バイト一致のための Ruby 互換|内部仕様 8.3]]
- 仕様: [[tecsgen-python3内部仕様 - 07 最適化|7章]]・[[tecsgen-python3内部仕様 - 08 コード生成|8章]]を新規執筆
- **P5 へ持ち越し**: `TOOL_INFO`（使うのはプラグインと `class` ケースだけと判明）、`unjoin_plugin`、プラグイン生成セルタイプの `gen_ep_func?` 系

## Related

- [[tecsgen-python3移植計画]] — 本体
- [[tecsgen-python3移植計画 Archive — P0–P2]] — 完了済みフェーズ P0〜P2
- [[tecsgen-python3]]

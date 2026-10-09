---
date: 2026-09-30
description: "tecsgen-python3移植計画のP5のうち、P5e〜P5i（OpaqueRPCPlugin・TECSInfo系・CIfGen/CppIfGen・ATK1・MrubyBridge、2026-09-28）の進捗記録。P5 進捗ログから25KB閾値で verbatim 分離したイベントログ"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
---

# tecsgen-python3移植計画 — P5 進捗ログ — P5e–P5i

[[tecsgen-python3移植計画 — P5 進捗ログ]] から、P5e〜P5i（2026-09-28）の段落を verbatim で移した（2026-09-30、25KB閾値による分離）。P5j 以降は元のログに、P5a〜P5d は [[tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d]] にある。

## P5e（2026-09-28）

**進捗（as of 2026-09-28、P5e）**: `OpaqueRPCPlugin`（`plugin/OpaqueRPCPlugin.py`）と、共有 mixin `GenOpaqueMarshaler`（`plugin/lib/GenOpaqueMarshaler.py`）をほぼ全量移植。`opaqueRPC` オラクルケースは実際に**成功**するため（`GenTransparentMarshaler` とは異なり）`gen_ep_func_body_marshal`/`gen_ep_func_body_unmarshal`/`gen_preamble`/`gen_postamble`/`print_params`/`alloc_for_out_param`/`dealloc_for_params`/`print_out_nullable` を含めてコード生成部分も実装した（`print_param` 単数は P5d で移植済みの `GenParamCopy` をそのまま再利用）。`opaqueRPC` ケースで OpaqueRPCPlugin 自身が生成する CDL・marshaler/unmarshaler の C コードは Ruby 版とバイト単位で一致することを確認（`tools/port/p4_progress.py` 相当のチェックを直接実行、`extra=[]`・`differ=[]`）。同ケースの残る不一致は未移植の `TECSInfoPlugin`（TECSInfo系、次のプラグイン移植順で対応予定）のみで、OpaqueRPCPlugin 自体には起因しない。pytest 908 passed / 72 skipped（Windows）・903 passed / 77 skipped（WSL、回帰なし）、`ruff`・`ty` とも両環境で通過。

**持ち越し**: `opaqueMarshaler`（`OpaqueMarshalerPlugin` という別のラッパークラス）・`sharedOpaqueRPC`（`SharedOpaqueRPCPlugin`、340行規模）はまだ未移植——いずれも `GenOpaqueMarshaler` を共有するが、プラグインクラス自体は今回の対象外。標準プラグイン76本、`-L` によるユーザプラグイン探索は未着手。次は移植順（Through系→TECSInfo系→Multi→カーネル依存→mruby系）に従い `TECSInfoPlugin` へ進む。

## P5f（2026-09-28）

**進捗（as of 2026-09-28、P5f）**: `TECSInfoPlugin`（`plugin/TECSInfoPlugin.py`）・`TECSInfoCompoPlugin`（`plugin/TECSInfoCompoPlugin.py`）・その基底クラス `CompositePlugin`（`plugin/CompositePlugin.py`、未移植だった）を移植。加えて `tecsinfo.rb`（901行。`Namespace`・`Region`・`Celltype`・`Port`・`Cell`・`Signature`・`FuncHead`・`ParamDecl`・`Decl`・`Type` を再オープンしてリフレクション情報を CDL セルとして出力する）を `core/tecsinfo.py` に、既存の `*Generate`/`*Optimize` mixin と同じ規約（1 mixin = 1 クラス、実クラスの base list に直接追加）で移植。対象オラクルケース `TECSInfo/raminitializer`・`TECSInfo/ramonly`・`TECSInfoAccessor/raminitializer`・`TECSInfoAccessor/ramonly` の4件すべてで `gen/` がバイト単位で一致することを確認（`extra=[]`・`differ=[]`）。`opaqueRPC` も 304/306 ファイルまで改善（残り2件は別要因、後述）。
- 発見した実装上の注意点: (1) `NamespacePath#append!`（破壊的）と `#append`（複製を返す、元は変更しない）を混同すると結合先セルの解決に失敗する（`S1110 not cell` として出る）。(2) `Symbol` は `str` と等値比較されない（`ruby_compat.Symbol.__eq__` は `Symbol` 同士のみ真）ため、`celltype.get_global_name() == "文字列"` は常に偽になる——`sym("...")` で包む必要がある。(3) Ruby の `self.class.superclass` 相当は、この移植の mixin 規約（実クラスを `__bases__` の最後に置く）では `type(self).__bases__[-1]` で求める（`CIntType(CType, IntType)` のような ctypes.rb 相当のラッパー型で使う）。(4) テストが1プロセスで複数ケースを実行するため、Ruby の `@@cell_list` に相当するクラス変数は `core/state.py::reset_model_state` でリセットする必要がある——ただし対象プラグインを P3 モデル比較テストの「Python にしかないクラス」判定が誤検出するため、モジュールが実際に import 済みの場合だけ `sys.modules` 経由でリセットする（強制 import しない）。
- `ty` 対応: これらの mixin は実クラス自身（例: `Namespace`）の base list に直接混ぜるため、プラグイン mixin が使う `TYPE_CHECKING`/`_Base` トリック（`_Base` を実クラスにする）は自己参照で `cyclic-class-definition` になり使えない。`self` 経由のメソッド呼び出しは `cast(Any, self)` で型を外して呼ぶ。
- **既知の残課題**: `TECSInfoAccessor/*` は生成物こそ完全一致するが、標準出力の警告が1件足りない（Ruby は `tmp_rTEMP_TECSInfoSub.cdl` の2回目の import で `W1008 reuse designation mismatch` を出すが、この移植ではまだ再現できていない——`TECSInfoPlugin`・`TECSInfoCompoPlugin` の両方が同じリージョンに同じファイル名で `Import` する際の `Generator.is_reuse()`（現在パーサの reuse 状態）の違いが原因と推測。ファイル内容には影響しないため後回し）。`opaqueRPC` の残り2ファイル（`tOpaqueMarshaler_sSimple.c`・`tOpaqueUnmarshaler_sSimple.c`）差分は未調査（P5e 側の残課題）。`test_p4_gen.py` の一律 skip は変更していない（既存方針どおり `p4_progress.py` で進捗管理）。pytest 908 passed / 72 skipped（Windows）・903 passed / 77 skipped（WSL、回帰なし）、`ruff`・`ty` とも両環境で通過。

## P5g（2026-09-28）

**進捗（as of 2026-09-28、P5g）**: Multi 系のうち `CIfGenPlugin`・`CppIfGenPlugin`（いずれも `MultiPlugin` の子。付与位置に応じて `*CelltypePlugin`／`*CellPlugin` へ振り分け）と、その具象クラス4本（`CIfGenCellPlugin`・`CIfGenCelltypePlugin`・`CppIfGenCellPlugin`・`CppIfGenCelltypePlugin`）を移植（ユーザー決定: 今回はこの2ファミリーに絞る）。`cifplugin`（24/24）・`cppifplugin`（44/44）が生成物・標準出力・終了コードとも完全一致し、`MultiPlugin.get_plugin` 経由の振り分け（P5a で用意済み）が実ケースで動くことも確認。`gen_factory` の呼び出し配線は `generate_factory_header_post` に既にあり（P4 で移植済み。P5e までの「未着手」記載は誤りだった）、追加作業は不要だった。`CppIfGenCelltypePlugin` の `@@b_signature_header_generated` は `state.py` で import 済みの場合だけリセット。Ruby 版の癖（`begin public` 以降のループが受け口だけでなく呼び口も回る、`TOPPERS_CB_TYPE_ONLY` の定義・解除部分を `dummy` 変数に入れて出力しない）もそのまま再現。
- **持ち越し（Multi 系の残り）**: `MrubyBridgePlugin` ファミリー（`MrubyBridgeSignaturePlugin` 1,047行ほか、lib 2本を含め約2,000行。対象 `multiplugin/1`・`multiplugin/2`）は移植順どおり mruby 系フェーズで扱う。`HRMPPlugin` はカーネル依存、`MrubyInfoBridgePlugin` は対象ケースなし。

## P5h（2026-09-28）

**進捗（as of 2026-09-28、P5h）**: カーネル依存系のうち ATK1（TOPPERS/ATK1、OSEK）の5本 `ATK1KernelPlugin`・`ATK1TaskPlugin`・`ATK1ResourcePlugin`・`ATK1AlarmPlugin`・`ATK1ISRPlugin` を移植（ユーザー決定）。`celltypePlugin` ケースが生成物68ファイル・標準出力（Ruby 版自身の `S3003 Task2: id number '1' conflict` エラーを含む）・終了コードとも完全一致。Ruby 版の癖を再現: `ATK1TaskPlugin` の `++extended_task_count;` は Ruby では `+(+x)` で何もしないため常に 1、`ATK1AlarmPlugin` の `str` はセルごとに nil から始まり結合の無い項目では直前の値を引き継ぐ、`ATK1ResourcePlugin` は AppFile で作成中の `<celltype>_factory.h` を CFile で直接 "w" で開く。`ATK1KernelPlugin` の `@@cell_list` は `state.py` でリセット。`generate` ケースも ATK1 起因のエラーは解消し、残りはテストケース同梱のユーザープラグイン `RTMBridgePlugin`（`-L` 探索が未対応）のみ。
- **判断（2026-09-28）**: HRP・HRP2・FMP・HRMP 系（約8,000行、`lib/GenHRP2Marshaler.rb` 含む）と `ATK1EventPlugin`・`ATK1DelayTaskPlugin` は、155ケースの中に正解データが1件もないため今回は移植しない。移植しても Ruby との一致を検証できず、基本方針（正解は Ruby 版の実行結果）に反するため。着手するなら、先に ASP3/HRP3 などの CDL で WSL の Ruby 版からオラクルケースを採取する（P6 の「実プロジェクトで差分テスト」の前倒し）。

## P5i（2026-09-28）

**進捗（as of 2026-09-28、P5i）**: mruby 系の MrubyBridge ファミリー7本（`MrubyBridgePlugin`（MultiPlugin）・`MrubyBridgeSignaturePlugin`・`MrubyBridgeCellPlugin`・`MrubyBridgeCelltypePlugin`・`MrubyBridgeCompositePlugin`・`lib/MrubyBridgeSignaturePluginModule`・`lib/MrubyBridgeCelltypePluginModule`、Ruby 約2,000行）を移植。`multiplugin/1`（59/59）・`multiplugin/2`（9/9、Ruby 版自身の `P2002`・`P1004` エラーと終了コード1を含む）が生成物・標準出力・終了コードとも完全一致。
- 見つけた既存コードのバグ: `CdlParser.parse_file`（Ruby の `Generator.parse`）が、Import・`generate_and_parse` と違ってホスト経由の `_host_reader` ではなく実ファイルを直接読んでいた。呼び出し元がこれまで無く潜在していた（`MrubyBridgeSignaturePlugin#new_cell` が初めて使う）。`_host_reader` を使うよう修正。
- Ruby 版の癖を再現: `MrubyBridgeCelltypePlugin` はクラス名に反して `CompositePlugin` の子（通常のセルタイプに付けると `P2002 not kind of CelltypePlugin`）、`set_exclude` は `get_function_head` の結果を `false` と比べるため存在しない関数名でもエラーにならない、`MrubyBridgeCelltypePluginModule#set_exclude_port` は未定義の `@cell` を参照して落ちる、INIB の場合も extern 宣言の型名に `_CB` を使う。
- ロード時の副作用: Ruby 版は `MrubyBridgeSignaturePlugin.rb` が require された時点で `TECSGEN::Makefile` に `-lmruby`・`$(MRUBYPATH)/include`・`MRUBYPATH` を追加する（プロセスごとに1回）。1プロセスで何度も実行するテストのため、`MrubyBridgeSignaturePlugin.on_load()` を実行回ごとに1回だけ行う形にし、Ruby 版が require する各入口（MultiPlugin の振り分け・CellPlugin・CelltypePluginModule の生成時）から呼ぶ。バナー（stderr）とモジュールのクラス変数は `state.py` でリセット。
- **カーネル依存・mruby 系の残り**: `MrubyInfoBridge*`・`Mruby2CBridgePlugin` は対象ケースなし。

## Related

- [[tecsgen-python3移植計画 — P5 進捗ログ]] — 親ログ（P5j 以降）
- [[tecsgen-python3移植計画 — P5 進捗ログ — P5a–P5d]] — P5a〜P5d
- [[tecsgen-python3移植計画]] — 本体（P5 節に索引）
- [[tecsgen-python3]]

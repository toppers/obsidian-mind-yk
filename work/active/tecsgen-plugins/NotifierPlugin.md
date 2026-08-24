---
date: 2026-08-14
description: "tecsgen 標準付属セルタイププラグイン NotifierPlugin の仕様書。ASP3カーネルのタイムイベント通知（周期通知・アラーム通知）をtAlarmNotifier/tCyclicNotifier等のセルとして扱い、静的API記述とアダプタ関数を自動生成する"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
  - plugin
---

# NotifierPlugin 仕様書

> [!info] 文書状態
> tecsgen プラグイン仕様書の2件目（1件目は [[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]]）。[[North Star]] の「16/17種が未記載」のうち、カーネル対応系「ASP3 NotifierPlugin」に対応。**この1件は他と異なり公式ドキュメントが既に存在する** — `reference/03-Resources/my-topic/raw/articles/2026-04-24-asp3--timeeventnotifier.md`（TOPPERS tecs-docs「タイムイベント通知」を ingest 済み）が、セルタイプ・シグニチャ・属性・通知方法アルゴリズムを詳細に記述している。本ノートは同資料を一次資料の中心に据えつつ、**公式ドキュメントに記載のないドメイン・クラス境界対応（4.3）をソースコードから追加**し、両者を突き合わせて実装の一致を確認した。ソースは `tecslib/plugin/NotifierPlugin.rb`（1231行）・`tecslib/plugin/CelltypePlugin.rb`（親クラス）・`tecslib/core/bnf.y.rb`（CDL 文法定義）。

## 1. 概要

**NotifierPlugin は、TOPPERS/ASP3 カーネルの「タイムイベント通知」（周期通知・アラーム通知）を TECS のセルとして扱うためのセルタイププラグインである。** タイムイベント通知はカーネルの静的 API（`CRE_ALM`・`CRE_CYC`）で生成するが、パラメータの組み立てが複雑なため通常のファクトリ記述では表現できず、`NotifierPlugin` がセルの属性値とテンプレート文字列から適切な静的 API 記述を自動生成する。

もう一つの役割は、通知先としてハンドラ関数（ユーザ定義のコールバック）を指定したい場合の**アダプタ関数**（受け口関数をカーネルが直接呼べる形へ変換する仲介関数）の自動生成である。

## 2. CDL 構文

### 2.1 呼び出し形式

`NotifierPlugin` は `CelltypePlugin` を継承する（`NotifierPlugin.rb` 50行 `class NotifierPlugin < CelltypePlugin`）。celltype の `[ ]` 内で specifier として呼び出し、シグニチャ引数は取らない（[[work/active/tecsgen/tecsgen外部仕様 - 06 プラグインシステム#6.2 プラグイン呼び出し規約|6.2]] の specifier 形式）。

```
[active, generate(NotifierPlugin, "factory=\"CRE_ALM({{id}}, { {{attribute}}, {{{_handler_params_}}} });\", output_file=tecsgen.cfg")]
celltype tAlarmNotifier { ... };
```

必須のプラグイン引数は2つ（`NotifierPlugin.rb` 902〜919行 `initialize`）。指定がなければ `cdl_error`（`NTF1003`）。

| 引数 | 内容 |
|---|---|
| `factory` | 生成する静的 API 記述のテンプレート文字列。`{{属性名}}` は対応する属性値に置換される |
| `output_file` | テンプレート展開結果の出力先ファイル（例: `tecsgen.cfg`） |

`{{_handler_params_}}` は特別な二重中かっこで、属性値ではなく 4章で述べる「通知先指定アルゴリズム」が生成するパラメータ列に置換される。

### 2.2 適用対象（標準セルタイプ）

`NotifierPlugin` はユーザが直接 `[generate(...)]` を書く対象ではなく、**tecsgen 標準ライブラリの CDL（`kernel.cdl` 等）内で既に `tAlarmNotifier`・`tCyclicNotifier` 等のセルタイプに適用済み**である。アプリケーション開発者はこれらのセルタイプのセルを生成するだけでよい。

| セルタイプ | 役割 |
|---|---|
| `tAlarmNotifier` | アラーム通知（相対時間後に1回通知）の生成・制御・状態取得 |
| `tCyclicNotifier` | 周期通知（一定周期で繰り返し通知）の生成・制御・状態取得 |
| `tTimeEventHandler` | 通知方法「タイムイベントハンドラの呼出し」専用。`ciHandlerBody` でハンドラ本体の受け口に結合する |
| `tAlarmHandler` | `tAlarmNotifier` + `tTimeEventHandler` を内包する複合セルタイプ。ハンドラ関数通知を直接使いたい場合の簡易版 |
| `tCyclicHandler` | 同上（周期通知版） |

シグニチャ: `siHandlerBody`（ハンドラ本体、`void main(void)`）・`sAlarm`/`siAlarm`（アラーム制御、タスク/非タスクコンテキスト用）・`sCyclic`（周期制御）・`siNotificationHandler`（通知先指定専用、関数を持たない——実行時には使われず結合の存在自体が情報として使われる）。

## 3. 通知方法

タイムイベント通知には、共通呼び口 `ciNotificationHandler`（通常）／`ciErrorNotificationHandler`（エラー時）の結合先セルタイプ・受け口と、セル属性の組み合わせで決まる7種の通知方法がある。

| 通知方法 | 結合先セルタイプ・受け口 | 対応する疑似コード |
|---|---|---|
| タイムイベントハンドラの呼出し | `tTimeEventHandler::eiNotificationHandler` | `handler.ciHandlerBody.main();` |
| 変数の設定 | 結合しない（属性 `setVariableAddress`/`setVariableValue` のみ） | `*setVariableAddress=setVariableValue;` |
| 変数のインクリメント | 結合しない（属性 `incrementedVariableAddress`） | `++*incrementedVariableAddress;` |
| タスクの起動 | `tTask::eiActivateNotificationHandler` | `er=act_tsk(handler.id);` |
| タスクの起床 | `tTask::eiWakeUpNotificationHandler` | `er=wup_tsk(handler.id);` |
| セマフォの資源の返却 | `tSemaphore::eiNotificationHandler` | `er=sig_sem(handler.id);` |
| イベントフラグのセット | `tEventflag::eiNotificationHandler`（属性 `flagPattern`） | `er=set_flg(handler.id,flagPattern);` |
| データキューへの送信 | `tDataqueue::eiNotificationHandler`（属性 `dataqueueSentValue`） | `er=psnd_dtq(handler.id,dataqueueSentValue);` |

**1つのタイムイベント通知に指定できる通知方法は1つに制限される。** 複数指定または未指定は tecsgen 実行時エラーになる。

### 3.1 エラー通知

サービスコールを伴う5方式（タスク起動・タスク起床・セマフォ返却・イベントフラグセット・データキュー送信）は失敗しうる。失敗時の通知方法（エラー通知）を `ciErrorNotificationHandler` ＋ `〜ForError` 系属性で個別に指定できる（ハンドラ関数はエラー通知には使えない）。エラー通知を省略した場合は tecsgen 実行時に**警告**が出る（属性 `ignoreErrors=true` で抑制可能）。逆に、エラーが発生しない通知方法（ハンドラ呼出し・変数系）にエラー通知を指定するとエラーになる。

## 4. 動作

### 4.1 ハンドラタイプによる通知先の解決

`NotifierPlugin` は「ハンドラ」（通常通知・エラー通知の総称）ごとに、結合先セルタイプ・受け口と属性値の組み合わせを `HANDLER_TYPES` 配列（`NotifierPlugin.rb` 886〜898行、`ActivateTaskHandlerType`・`WakeUpTaskHandlerType`・`SetVariableHandlerType`・`SetVariableToErrorCodeHandlerType`・`IncrementVariableHandlerType`・`SignalSemaphoreHandlerType`・`SetEventflagHandlerType`・`SendToDataqueueHandlerType`・`SendErrorCodeToDataqueueHandlerType`・`UserHandlerType`・`NullHandlerType`）と照合し、完全一致する1つを選ぶ（`validate_join`、`gen_factory_for_cell` 1031〜1038行）。一致がなければ `cdl_error`（`NTF1001`）。

選ばれたハンドラタイプが `gen_cfg_handler_type`／`generate_attr_map`／`gen_cfg_handler_parameters` を通じて、`factory` テンプレートの `{{_handler_params_}}` を埋めるパラメータ列を生成する。

### 4.2 アダプタ関数の生成（ハンドラ関数通知の場合）

`ciNotificationHandler` が `tTimeEventHandler::eiNotificationHandler` に結合された場合（`UserHandlerType`）、カーネルの静的 API は関数ポインタ＋`intptr_t` 引数1個（`T_NFY_HDR::tmehdr`/`exinf`）しか渡せないのに対し、TECS の受け口関数は状況により最大2引数（`idx`・配列添字 `subscript`）を必要とする。この不一致を仲介するのが `AdapterGenerator`（`NotifierPlugin.rb` 100〜411行、内部クラス `EntryProperty`・`EntryPort`・`Handler`・`HandlerAttribute`）が生成する**アダプタ関数**である。

- 引数のうち1個は `exinf` を介して直接渡し、受け口関数と残りの引数はその値ごとに関数を特殊化する（1個のアダプタ関数を複数の結合で共有できるよう、セルインデックスまたは配列添字のパターン数が少ない方を一般化する——`NotifierPlugin.rb` 冒頭コメント 52〜97行）。
- 生成先ヘッダ／実装ファイルは `tTimeEventHandler.h`／`tTimeEventHandler.c`（`gen_factory` 940〜945行）。

## 5. 発見: ドメイン・クラス境界への対応（公式ドキュメント未記載）

参照した公式ドキュメント（`reference/03-Resources/my-topic/raw/articles/2026-04-24-asp3--timeeventnotifier.md`）にはドメイン（[[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]] 等が扱う信頼境界）への言及が一切ないが、**ソースコードには HRP／HRMP ドメインを意識した検証・出力ラップ処理が存在する**（`gen_factory_for_cell` 1043〜1112行）。

- 通知セルの所属リージョンに `domain(HRP, ...)` または `domain(HRMP, ...)` が指定されている場合、ハンドラタイプごとに追加検証を行う。
  - `UserHandlerType`（ハンドラ関数呼出し）は `option == "kernel"` のリージョンにしか置けない（ハンドラ関数を直接呼ぶため）。
  - それ以外のカーネルオブジェクト系ハンドラタイプは `option == "OutOfDomain"` のリージョンに置けない。
  - いずれの場合も、通知セルと結合先セルは**同一ドメインに属していなければならない**（`cdl_error`「must be placed in same domain」）。
- 検証を通過すると、生成する静的 API 記述を `option` に応じて `KERNEL_DOMAIN{ ... }` または `DOMAIN(<ドメイン名>){ ... }` で包む（1077〜1086行）。
- 同様に、所属リージョンに `class(FMP, ...)` または `class(HRMP, ...)` が指定されている場合は `CLASS(<クラス名>){ ... }` でさらに包む（1092〜1112行）。`class_type` が上記2種以外、または `domain_type` が HRP/HRMP 以外の場合はいずれも `cdl_error`（"unknown domain/class type"）。

この対応は tecs-docs の「タイムイベント通知」記事には現れないため、**ドメイン・クラス機構が導入された際に NotifierPlugin 側だけソースが更新され、上位ドキュメントへの反映が漏れた**可能性がある（一次資料のみで確認できる事実であり、公式ドキュメントとの照合では検出できなかった）。

## 6. 制約・注意点

- **通知方法は1セルにつき1つのみ**、エラー通知も1つのみ（3章）。組み合わせ違反は tecsgen 実行時エラー。
- **`siNotificationHandler` に関数は定義されていない。** 通知先の識別はシグニチャ照合ではなく、結合先セルの ID 属性値を読み取ることで行われる（2.2）——アプリケーション定義のセルでこのシグニチャの呼び口・受け口を定義してはならない。
- **属性値は `id` を除き `[omit]` される**（静的 API 記述の引数、または `NotifierPlugin` の入力としてのみ使われ、実行時のメモリ割り当てを持たない）。
- **アダプタ関数のシグネチャは受け口関数の状況（singleton か否か、配列か否か）で4通りに変化する**（4.2）ため、生成コードを手で書くのは非現実的——本プラグインの存在意義そのものに関わる。
- ドメイン・クラス検証（5章）は一次資料のみに基づく——将来の tecs-docs 側の更新で言及が追加される可能性がある。

## Related

- [[work/active/tecsgen/tecsgen外部仕様 - 06 プラグインシステム|tecsgen外部仕様 第6章]] — プラグイン呼び出し規約。本ノートの執筆過程で `[generate(...)]` の2形式（specifier／statement）の混同を発見し、6.2 を訂正した
- [[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]] — tecsgen プラグイン仕様書シリーズの1件目。ドメイン概念（trusted/nontrusted/OutOfDomain）の定義元
- [[reference/03-Resources/my-topic/wiki/plugin-notifier|NotifierPlugin (ASP3)]] — my-topic wiki 側の概念スタブ（未執筆のまま）。本ノートが実質的な詳細仕様を補完する
- [[TECS開発]] — 開発進捗全体
- [[North Star]] — 「プラグイン仕様書（15/17種が未記載）」ゲート
- [[perf/competencies/技術文書化|技術文書化]] — 公式ドキュメントとソースコードを突き合わせ、記載漏れ（ドメイン対応）を発見した competency 証拠

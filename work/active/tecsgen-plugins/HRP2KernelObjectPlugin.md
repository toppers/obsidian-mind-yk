---
date: 2026-08-15
description: "tecsgen 標準付属プラグイン群、HRP2KernelObjectPlugin の具象サブクラス10種の仕様書。TOPPERS/HRP2カーネルオブジェクト（タスク・セマフォ・イベントフラグ等）をCDL属性から生成する。8種の単機能プラグインに加え、後発の2種（HRP2ObjectPlugin・HRP2HandlerPlugin）がテーブル駆動で単機能プラグインの範囲を上回るオブジェクト種別まで対応する二層構造を持つ"
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

# HRP2KernelObjectPlugin 具象サブクラス群 仕様書

> [!info] 文書状態
> [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin|HRP2DomainBoundaryPlugin]]（2026-08-15）が「具象サブクラス群は未着手」として残していた10ファイルを執筆。一次資料は `tecslib/plugin/HRP2TaskPlugin.rb`（202行）・`HRP2SemaphorePlugin.rb`（69行）・`HRP2EventflagPlugin.rb`・`HRP2DataqueuePlugin.rb`・`HRP2PriorityDataqueuePlugin.rb`・`HRP2FixedSizeMemoryPoolPlugin.rb`・`HRP2AlarmHandlerPlugin.rb`・`HRP2CyclicHandlerPlugin.rb`・`HRP2ObjectPlugin.rb`（97行）・`HRP2HandlerPlugin.rb`（120行）、および `doc/changes.txt`（バグ #1125 の記録）。ソースの位置は他ノートと同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。CDL 実例はリポジトリ内に一件も見つからず（ATK1Plugin ファミリーと同種のギャップ）、CDL 構文はソースの `@plugin_arg_str` の使われ方から逆算した。

## 1. 概要

**10ファイルはいずれも [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin|HRP2KernelObjectPlugin]]（`< CelltypePlugin`）の具象サブクラスで、CDL のセルタイプ属性から TOPPERS/HRP2 カーネルの `CRE_XXX`/`SAC_XXX`（生成・アクセス許可）コンフィギュレータ命令を出力する。** ただし ATK1Plugin ファミリー（[[work/active/tecsgen-plugins/ATK1Plugin]]、1オブジェクト種別=1ファイルの単純な並列構造）とは異なり、**単機能プラグイン8種と、テーブル駆動の汎用プラグイン2種が並存し、後者は前者の範囲を包含したうえで、単機能プラグインが存在しないオブジェクト種別にも対応する**という二層構造になっている（5節で詳述）。

## 2. 単機能プラグイン8種の対応表

| プラグイン | CRE_ / SAC_ マクロ | 受け口リスト（`@@ep`） |
|---|---|---|
| `HRP2TaskPlugin` | `CRE_TSK` / `SAC_TSK` ＋ `DEF_TEX`（例外処理） | （コメントアウト、`get_entry_ports_name_list` 未使用） |
| `HRP2SemaphorePlugin` | `CRE_SEM` / `SAC_SEM` | `eSignalSemaphore`・`eWaitSemaphore`・`eManageSemaphore`・`eReferSemaphore` |
| `HRP2EventflagPlugin` | `CRE_FLG` / `SAC_FLG` | `eSetEventflag`・`eWaitEventflag`・`eManageEventflag`・`eReferEventflag` |
| `HRP2DataqueuePlugin` | `CRE_DTQ` / `SAC_DTQ` | `eSendDataqueue`・`eReceiveDataqueue`・`eManageDataqueue`・`eReferDataqueue` |
| `HRP2PriorityDataqueuePlugin` | `CRE_PDQ` / `SAC_PDQ` | `eSendPriorityDataqueue`・`eReceivePriorityDataqueue`・`eManagePriorityDataqueue`・`eReferPriorityDataqueue` |
| `HRP2FixedSizeMemoryPoolPlugin` | `CRE_MPF` / `SAC_MPF` | `eSendFixedSizeMemoryPool`・`eReceiveFixedSizeMemoryPool`・`eManageFixedSizeMemoryPool`・`eReferFixedSizeMemoryPool` |
| `HRP2AlarmHandlerPlugin` | `CRE_ALM` / `SAC_ALM` | `eStartAlarm`・`eStopAlarm`・`eManageAlarm`・`eReferAlarm` |
| `HRP2CyclicHandlerPlugin` | `CRE_CYC` / `SAC_CYC` | `eStartCyclic`・`eStopCyclic`・`eManageCyclic`・`eReferCyclic` |

いずれも `print_cfg_cre`/`print_cfg_sac`（[[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin|HRP2KernelObjectPlugin]] が定義する純粋仮想メソッド）を、`val`（属性値ハッシュ）と `acv`（アクセス許可ベクタ配列、4要素）から対応する1つのマクロへ素直に埋め込むだけの薄い実装（多くは10〜20行）。**`@@ep` の実際の用途は不明**——`get_entry_ports_name_list` を呼び出す側は `=begin`/`=end` でコメントアウトされており（全ファイル共通）、現状は未使用のデッドコードと思われる。

## 3. HRP2TaskPlugin の特別扱い

`HRP2TaskPlugin` だけは他7種と質的に異なる2つの拡張を持つ。

1. **ドメイン種別によるスタック指定の分岐**（54〜97行）: 所属ドメインが `trusted`（カーネルドメイン）なら `userStackSize` の指定を禁止し `systemStackSize` のみで `CRE_TSK` を生成、`nontrusted`（ユーザドメイン）なら逆に `userStackSize` を必須として `systemStackSize` の有無で2パターンの `CRE_TSK` 呼び出し形式を出し分ける。カーネルドメインのタスクにユーザスタックを持たせる／ユーザドメインのタスクにユーザスタックを持たせない、という組み合わせはいずれも `raise` でエラーにする。
2. **`gen_factory` のオーバーライドによる `ATT_MOD`（メモリ保護モジュール）の一括登録**（120〜199行）: `super`（`HRP2KernelObjectPlugin#gen_factory`、通常の CRE_/SAC_ 生成）を呼んだ後、**プログラム全体の全セルタイプを走査して**、カーネルオブジェクトセルタイプではない・かつコード生成が必要なセルタイプそれぞれについて、そのセルタイプが属するドメインの数と種類（`OutOfDomain` を含むか、複数ドメインにまたがるか）に応じて `ATT_MOD("<セルタイプ>.o")` をどの `.cfg` ファイルへ書くか（共有 `tecsgen.cfg` か、ドメイン専用の `tecsgen_<region>.cfg` か）を判定する。**この処理は「タスクを生成する」責務とは無関係な、プログラム全体のメモリ保護モジュール登録という別責務**であり、`@@generate_memory_module`（クラス変数）で一度しか実行しないようガードされている——なぜ `HRP2TaskPlugin` にこの責務が乗っているのか（他のカーネルオブジェクトプラグインではなく）はソースからは明確でない。

## 4. CDL構文（ソースからの逆算、実例なし）

単機能プラグイン8種は `[generate(HRP2SemaphorePlugin)] celltype ... { ... };` のように**プラグイン引数なしで呼べる**（`@plugin_arg_str` を分岐条件として使っていない）。一方、汎用プラグイン2種は `@plugin_arg_str`（`CelltypePlugin#initialize` が `option` からダブルクォートを外しただけの生文字列——key=value 形式ではない）をそのまま分岐条件に使うため、**1つのクォート文字列を第2引数に取る**。

```tecs-cdl
[generate(HRP2ObjectPlugin, "SEMAPHORE")]
celltype tMySemaphore {
    ...
};

[generate(HRP2HandlerPlugin, "CYCLIC")]
celltype tMyCyclicHandler {
    ...
};
```

## 5. 発見: 汎用2種は単機能8種を包含し、さらに単機能プラグインが存在しない4種別に対応する

`HRP2ObjectPlugin`（`@@api` テーブル、46〜54行）と `HRP2HandlerPlugin`（`elsif @plugin_arg_str == "..."` の分岐、65〜91行）を単機能8種と突き合わせた結果、次の対応関係が判明した。

| `@plugin_arg_str` | マクロ | 単機能プラグインとして存在するか |
|---|---|---|
| `HRP2ObjectPlugin, "SEMAPHORE"` | `CRE_SEM`/`SAC_SEM` | ○ `HRP2SemaphorePlugin` と重複 |
| `HRP2ObjectPlugin, "EVENTFLAG"` | `CRE_FLG`/`SAC_FLG` | ○ `HRP2EventflagPlugin` と重複 |
| `HRP2ObjectPlugin, "DATAQUEUE"` | `CRE_DTQ`/`SAC_DTQ` | ○ `HRP2DataqueuePlugin` と重複 |
| `HRP2ObjectPlugin, "PRIORITY_DATAQUEUE"` | `CRE_PDQ`/`SAC_PDQ` | ○ `HRP2PriorityDataqueuePlugin` と重複 |
| `HRP2ObjectPlugin, "FIXED_SIZE_MEMORYPOOL"` | `CRE_MPF`/`SAC_MPF` | ○ `HRP2FixedSizeMemoryPoolPlugin` と重複 |
| `HRP2ObjectPlugin, "KERNEL"` | `SAC_SYS` のみ（`CRE_SYS` 相当は生成しない） | **✕ 単機能プラグインなし** |
| `HRP2ObjectPlugin, "MESSAGE_BUFFER"` | `CRE_MBF`/`SAC_MBF` | **✕ 単機能プラグインなし**（[[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin\|HRP2RPCPlugin]] の既定 `channelCelltype=tMessagebufferChannel` が使うのと同じメッセージバッファオブジェクト） |
| `HRP2HandlerPlugin, "ALARM"` | `CRE_ALM`/`SAC_ALM` | ○ `HRP2AlarmHandlerPlugin` と重複 |
| `HRP2HandlerPlugin, "CYCLIC"` | `CRE_CYC`/`SAC_CYC` | ○ `HRP2CyclicHandlerPlugin` と重複 |
| `HRP2HandlerPlugin, "CONFIG_INT"` | `CFG_INT` | **✕ 単機能プラグインなし**（割込み設定） |
| `HRP2HandlerPlugin, "ISR"` | `ATT_ISR` | **✕ 単機能プラグインなし**（割込みサービスルーチン） |
| `HRP2HandlerPlugin, "INIT_ROUTINE"` | `ATT_INI` | **✕ 単機能プラグインなし**（初期化ルーチン） |
| `HRP2HandlerPlugin, "TERM_ROUTINE"` | `ATT_TER` | **✕ 単機能プラグインなし**（終了処理ルーチン） |

**単機能8種のうち6種（Task・AlarmHandler・CyclicHandler を除く5種＋Alarm・Cyclicの計7重複、Taskのみ非重複）が汎用プラグインと機能重複している一方、汎用プラグインだけが対応する6種別（KERNEL・MESSAGE_BUFFER・CONFIG_INT・ISR・INIT_ROUTINE・TERM_ROUTINE）が存在する。** 単機能プラグインの copyright ヘッダの開始年が軒並み2008年（最古参）なのに対し、`HRP2ObjectPlugin`（2008-**2017**）・`HRP2HandlerPlugin`（2008-**2018**）は最終更新年が新しく、割込み・初期化・終了処理・システムオブジェクト・メッセージバッファという単機能プラグイン化されていない残りのオブジェクト種別を後から1つのテーブル駆動プラグインへ集約する形で拡張されてきた、と推測できる（未検証・設計意図の記述はソース中に見当たらない）。

## 6. 既知の不具合（#1125、`doc/changes.txt` 237〜239行）

```
18/3/25 V1.6.0-alpha3
[不具合] #1125  HRPHandlerPlugin, HRP2HandlerPlugin で CB, INIB ともに最適化で消えるケースが想定されていない (ATT_INI)
```

`HRP2HandlerPlugin` の `INIT_ROUTINE`（`ATT_INI`）分岐について、CB（セル管理ブロック）と INIB（初期化ブロック）が両方とも最適化で消去されるケースを想定していなかったという不具合が V1.6.0-alpha3（2018-03-25）で記録されている。**この changes.txt のエントリは、HRP2 の前身カーネル向けの `HRPHandlerPlugin` にも同じ不具合が存在したことを示しており**、無印 HRP ファミリー（[[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin|HRP2DomainBoundaryPlugin]] 制約・注意点で「北極星に一度も登場していない」と記録した3ファミリーの1つ）が HRP2 と並行した構造を持つことの間接証拠にもなっている。

## 7. 制約・注意点

- CDL 実例がリポジトリ内に一件もなく、4節の構文はソースの分岐条件からの逆算であり未検証。
- 単機能プラグインと汎用プラグインのどちらを使うべきかの指針はソース中に見当たらない（両方が同じオブジェクト種別を生成できる場合、使い分けの基準は不明）。
- `@@ep`（受け口名リスト）は全ファイルで定義されているが参照側がコメントアウトされており、現状デッドコードの可能性が高い。
- `HRP2TaskPlugin` の `ATT_MOD` 一括登録処理（3節2項）はタスク生成と無関係な責務が同じクラスに同居しており、なぜここに置かれているかは未解明。
- 6節の不具合 #1125 が現在のソースで修正済みかどうかは本ノートでは未検証（`doc/changes.txt` の記録のみを確認）。

## Related

- [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin]] — 抽象基底クラス `HRP2KernelObjectPlugin` とドメイン境界仲介プラグイン（本ノートが具象サブクラス群を補完）
- [[work/active/tecsgen-plugins/ATK1Plugin]] — 同じ「1抽象基底クラス＋複数の具象カーネルオブジェクトプラグイン」構造を持つ別カーネルファミリー。ただしATK1には汎用プラグインによる重複・拡張は存在しない
- [[tecsgen外部仕様]] — 6.3 標準付属プラグイン一覧
- [[North Star]] — プラグイン仕様書化の進捗管理。HRP2系ファミリーの内訳を本ノートで具体化

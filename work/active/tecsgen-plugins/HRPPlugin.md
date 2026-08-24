---
date: 2026-08-15
description: "tecsgen 標準付属ドメインプラグイン HRPPlugin（TOPPERS/HRPカーネル向け）とその支援クラス HRPKernelObjectManager の仕様書。HRP2Pluginと並行した「北極星に一度も載っていなかった」3ファミリーの1つで、HRP2からの派生の痕跡が残るコードベース"
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

# HRPPlugin / HRPKernelObjectManager 仕様書

> [!info] 文書状態
> [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2系ファミリー完走]]（2026-08-15）で「北極星に一度も登場していない」と発見した3ファミリー（HRP・FMP・HRMP）のうち、無印 HRP（TOPPERS/HRP2 の前身カーネル）に初めて着手。一次資料は `tecslib/plugin/HRPPlugin.rb`（261行）・`tecslib/plugin/HRPKernelObjectManager.rb`（105行、`HRPKernelObjectManager`＋`HRPSVCManage`の2クラス）・`tecslib/plugin/lib/GenAttMod.rb`（277行、`GenAttMod`＋`GenDefSvc`の2モジュール）。ソースの位置は他ノートと同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。**HRP ファミリー（計10ファイル）は本ノート（`HRPPlugin`・`HRPKernelObjectManager`）＋[[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin|ドメイン境界仲介プラグイン一式5ファイル]]＋[[work/active/tecsgen-plugins/HRPKernelObjectPlugin|具象サブクラス3種]]で完走（2026-08-15）**。

## 1. 概要

**HRPPlugin は TOPPERS/HRP カーネル向けの「ドメインプラグイン」で、[[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]] と同じ役割（region の信頼ドメイン境界宣言＋ドメイン間結合への仲介プラグイン自動選択）を果たす（`< DomainPlugin`）。** 構造は HRP2Plugin とほぼ並行しているが、後述のとおりコード自体に「HRP2Plugin からの派生」を示す痕跡が残っており、単純な姉妹プラグインではなく歴史的な前後関係がある。

## 2. 発見: HRP2Plugin からの派生の痕跡

`HRPPlugin#add_through_plugin`（65〜133行）には、実際には呼ばれない多数のコメントアウトされたコードが残っており、その内容が一字一句 `HRP2SVCPlugin`・`HRP2RPCPlugin` を参照している（96・100・107・113・115・119・121・127行、例: `# @plugin_body = HRP2SVCPlugin.new(cell_name, plugin_arg, next_cell, next_cell_port_name, signature, celltype, caller_cell)`）。実際に返される値は `:HRPSVCThroughPlugin`・`:HRPRPCPlugin`（HRP2 の対応クラスとは異なる名前）であり、**コメントだけが HRP2 版の名残として残っている**——`HRPPlugin.rb` は `HRP2Plugin.rb` のコードを複製してから固有名を書き換える形で作られたことを示す直接証拠である。

この推測は copyright 年からも裏付けられる。`HRPPlugin.rb` は **「Copyright (C) 2014-2020」**、`HRPKernelObjectManager.rb` は **「Copyright (C) 2015-2021」**——[[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]]・[[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin|HRP2SVCPlugin/HRP2RPCPlugin]] を含む HRP2 系ファイル群の開始年（多くが2008年）よりずっと後である。**TOPPERS/HRP カーネル自体は HRP2 より歴史的に古いが、tecsgen のドメインプラグイン対応は HRP2 向けが先に実装され、HRP 向けは後から（既存の HRP2Plugin のコードを土台に）追加された**、という順序が読み取れる。

## 3. CDL 構文: ドメイン種別語彙が HRP2 と異なる

```
[domain(HRP, "kernel")]
region <リージョン名> {
    ...
};
```

`HRPPlugin#initialize`（50〜63行）が受理する第2引数（option）は **`"kernel"` / `"user"` / `"OutOfDomain"`** の3値——[[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]] の `"trusted"` / `"nontrusted"` / `"OutOfDomain"` とは**語彙が異なる**（`"OutOfDomain"` のみ共通）。同じ「信頼ドメイン境界」という概念を表しているにもかかわらず、姉妹プラグイン間で用語が統一されていない。不正な値を指定した場合はエラーを出しつつ `"kernel"` にフォールバックする（HRP2Plugin の `"trusted"` フォールバックと同じ設計）。

## 4. 動作: add_through_plugin の判定（HRP2Plugin との対比）

| # | 条件 | HRPPlugin が挿入するプラグイン | HRP2Plugin（対応する条件） |
|---|---|---|---|
| 1 | 結合先セルがカーネルオブジェクトセル（`HRPKernelObjectManager.include_celltype?`） | なし（`[]`） | 同じ（`HRP2KernelObjectPlugin.include_celltype?`） |
| 2 | 結合先ドメインが `"OutOfDomain"` | なし（`[]`） | 同じ |
| 3 | ユーザドメイン→カーネルドメイン | `HRPSVCThroughPlugin`（引数なし） | `HRP2SVCPlugin`（引数なし） |
| 4 | 異なるユーザドメイン間 | `HRPRPCPlugin`、**`"noClientSemaphore=false,PPAllocatorSize=256"`** | `HRP2RPCPlugin`、**`"channelCelltype=tMessagebufferChannel,noClientSemaphore=true"`** |
| 5 | 該当なし | `nil` を返し警告（`"warning: at HRP Join Check"`） | 同じ（`"at HRP2 Join Check"`） |

判定の骨格（5条件の構造）は完全に一致するが、**条件4で自動的に渡される RPC プラグイン引数がHRPとHRP2で異なる**——HRP はクライアント排他制御セマフォを付ける（`noClientSemaphore=false`）デフォルトで固定チャンネル型を指定せず、HRP2 は逆にセマフォを省略し (`noClientSemaphore=true`)、チャンネル型を `tMessagebufferChannel` に固定する。同じ骨格の上で異なるチューニングが選ばれている。

## 5. HRPKernelObjectManager / HRPSVCManage: HRP2 とは異なる実装方式

### 5.1 カーネルオブジェクトセルタイプの判定方式が異なる

[[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2KernelObjectPlugin]] は「そのプラグインを使う celltype が `initialize` 時に動的にクラス変数へ自己登録する」方式（`include_celltype?` は登録済みインスタンスの集合を見る）だったのに対し、**`HRPKernelObjectManager` は `gen_kernel_celltype.py` という Python スクリプトから生成された静的なセルタイプ名リスト**（`tKernel`・`tTask`・`tSemaphore`・`tEventflag`・`tDataqueue`・`tPriorityDataqueue`・`tMutex`・`tFixedSizeMemoryPool`・`tTimeEventHandler`・`tCyclicNotifier`・`tAlarmNotifier`・`tInterruptRequest`・`tISR`・`tInterruptHandler`・`tCpuExceptionHandler`・`tInitializeRoutine`・`tTerminateRoutine`・`tMessageBuffer`、計18種）を単純に `include?` で照合するだけ——**「実際にどのプラグインが使われたか」ではなく「セルタイプ名が既知のリストに載っているか」で判定する**、動的登録とは根本的に異なる方式。HRP2 にあった「HRP2KernelObjectPlugin を使わないセルタイプは判定対象にならない」という取りこぼしの可能性が、HRP 側では原理的に発生しない代わりに、セルタイプ名を変更した独自拡張には対応できない。

### 5.2 HRPSVCManage は node_root（リージョンツリーのルート）単位でスコープされる

HRP2SVCPlugin 内の `SVCManage`（[[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin]] 3.1節）はプロセス全体で1つのフラットな ID 空間（`@@id = 20` から採番）だったのに対し、`HRPSVCManage`（`HRPKernelObjectManager.rb` 73〜104行）は **`@@func_ids` が `node_root`（リージョンツリーのルート）をキーとするハッシュ**——複数のノード（≒複数の独立したビルド単位）を1プロセスで扱う場合でも SVC ID 空間が混線しない設計になっている。

## 6. GenAttMod / GenDefSvc: HRP と HRMP が共有し、FMP を明示的に除外するモジュール

`HRPPlugin` は `include GenAttMod` と `include GenDefSvc`（`tecslib/plugin/lib/GenAttMod.rb` に両モジュールが同居）でメモリ保護モジュール登録（`ATT_MOD`）と拡張サービスコール定義（`DEF_SVC`）の生成を委譲する——[[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2TaskPlugin]] が `gen_factory` を独自オーバーライドしてアドホックに実装していた `ATT_MOD` 登録処理を、HRP では再利用可能なモジュールへ整理したもの。

**発見**: `GenAttMod#gen_att_mod`（`GenAttMod.rb` 107〜194行）は `ct.get_domain_roots[ :HRMP ] == nil && ct.get_domain_roots[ :HRP ] == nil` の場合は処理をスキップし、コメントに **「FMP3 は、対象外となる」**（116行）と明記している——**`GenAttMod`/`GenDefSvc` は HRP と HRMP の2ファミリーで共有され、FMP は明示的に対象外**。北極星に一度も載っていなかった3ファミリーのうち、HRP と HRMP が近い設計を共有し、FMP だけが別系統であることがこのモジュールの分岐条件から確認できた。加えて、このファイルの `$Id` キーワードは `GenAttMod.rb` ではなく **`HRMPDomainPlugin.rb`** を指しており（37行）、もともと `HRMPDomainPlugin.rb` の一部だったコードが `GenAttMod.rb` として切り出された際に SVN の `$Id` が更新されなかった痕跡と考えられる——2節の「HRP2Plugin から HRPPlugin への複製」と対になる、もう一つの派生の痕跡。

## 7. 制約・注意点

- 本ノートは `HRPPlugin`・`HRPKernelObjectManager`・`HRPSVCManage`・共有モジュール `GenAttMod`/`GenDefSvc` のみを対象とする。ドメイン境界仲介プラグイン一式（`HRPKernelObjectPlugin`・`HRPRPCPlugin`・`HRPSVCThroughPlugin`・`HRPSVCSignaturePlugin`・`HRPSVCBodyCellPlugin`）は [[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin|別ノート]]（2026-08-15完成）参照。カーネルオブジェクト生成の具象サブクラス3種（`HRPTaskPlugin`・`HRPObjectPlugin`・`HRPHandlerPlugin`）も [[work/active/tecsgen-plugins/HRPKernelObjectPlugin|別ノート]]（2026-08-15完成）で完了し、HRPファミリー全10ファイルを完走した。
- CDL 実例はリポジトリ内に見つからず、3節の構文はソースからの逆算・未検証。
- HRP2 と HRP でドメイン種別のオプション文字列語彙が異なる（3節）ことは、両者を同時に扱うプロジェクトで混同しやすい落とし穴になりうる。

## Related

- [[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin]] — HRPファミリーのドメイン境界仲介プラグイン一式（本ノートが残した5ファイル分）
- [[work/active/tecsgen-plugins/HRP2Plugin]] — 対になる HRP2 側のドメインプラグイン。本ノート全体で対比の基準にした
- [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin]] — HRP2SVCPlugin/HRP2RPCPluginとの対比元
- [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin]] — HRP2KernelObjectPluginの動的登録方式との対比元（5.1節）
- [[tecsgen外部仕様]] — 6.3 標準付属プラグイン一覧
- [[North Star]] — プラグイン仕様書化の進捗管理。HRP・FMP・HRMP3ファミリーのうちHRPに初めて着手

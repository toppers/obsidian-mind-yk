---
date: 2026-08-14
description: "tecsgen 標準付属プラグイン RPCPlugin ファミリー（RPCPlugin・OpaqueRPCPlugin・SharedRPCPlugin・SharedOpaqueRPCPlugin）の仕様書。ThroughPluginとして呼び口結合の間にマーシャリング付きRPCチャンネルを自動生成し、専用タスクでサーバ側呼び出しを実行する。Transparent/Opaque×専用/共有の2軸4種を横断的に扱う"
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

# RPCPlugin 仕様書（RPC プラグインファミリー）

> [!info] 文書状態
> [[North Star]] の RPC カテゴリ4件（TransparentRPCPlugin・OpaqueRPCPlugin・SharedRPCPlugin・SharedOpaqueRPCPlugin）に対応。**「TransparentRPCPlugin」という表記は誤りで、実クラス名は単に `RPCPlugin`**（クラス内コメント「Transparent RPC プラグイン」・定数名 `TransparentRPCPluginArgProc` から確認、[[tecsgen外部仕様]] 6.3 を訂正）。4つとも `ThroughPlugin` の派生であり、[[work/active/tecsgen-plugins/TracePlugin|TracePlugin]] と同じ `through`/`in_through`/`out_through`/`to_through`/`from_through` の5構文で呼び出せる。一次資料は `tecslib/plugin/RPCPlugin.rb`・`OpaqueRPCPlugin.rb`・`SharedRPCPlugin.rb`・`SharedOpaqueRPCPlugin.rb`（計1363行）と共有モジュール `tecslib/plugin/lib/GenTransparentMarshaler.rb`・`GenOpaqueMarshaler.rb`・`GenParamCopy.rb`、加えて実行時サポート層 `tecs/rpc/`（`sChannel.cdl`・`tMessageBufferChannel.cdl` 等、実在するインフラ資産）。ソースの位置は他ノートと同じく `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\`。

## 1. 概要

**RPC プラグインファミリーは、`ThroughPlugin` として呼び口結合の間に「マーシャリング付き RPC チャンネル」を自動生成し、サーバ側の実処理を専用タスクで実行させることで、タスク境界・ドメイン境界をまたぐ呼び出しを透過的な受け口呼び出しに見せかける。** 4種は「マーシャリング方式（Transparent／Opaque）」と「チャンネルの扱い（専用／共有）」の2軸で整理できる。

| | 専用チャンネル（呼び口ごとに新規生成） | 共有チャンネル（複数の呼び口insertion間で再利用） |
|---|---|---|
| **Transparent**（内蔵の型付きマーシャラ、`sTDR`/`sEventflag` 固定） | `RPCPlugin`（＝North Star の「TransparentRPCPlugin」） | `SharedRPCPlugin`（`@@shared_channel_list` でチャンネルを共有） |
| **Opaque**（チャンネル実装をユーザーが差し替え可能） | `OpaqueRPCPlugin` | `SharedOpaqueRPCPlugin`（`sharedChannelName` オプションで共有グループを指定） |

## 2. レイヤー構造（`tecs/rpc/sChannel.cdl` より）

生成される RPC チャンネルは3層に分かれる。

1. **マーシャラ層**（プラグインごとに `Generate*Marshaler` モジュールが生成、シグニチャ固有）: 関数呼び出しの引数・戻り値を型ごとに送受信操作へ変換する。
2. **TDR 層**（`sTDR` シグニチャ、`tTDR`/`tNBOTDR` 等の実装セルタイプが `tecs/rpc/` に存在）: `int8_t`/`int16_t`/`int32_t`/`int64_t`/`float32_t`/`double64_t`/`bool_t`/`char_t` のような基本型（配列・構造体は要素ごと）を、下位のバイトストリームチャンネルとの送受信に変換する。
3. **チャンネル層**（`sChannel` シグニチャ: `send`/`flush`/`receive`/`end_receive`/`reset`）: 実際の通信路。`tMessageBufferChannel`・`tDataqueueOWChannel` 等、複数の実装が `tecs/rpc/` に用意されている。

Transparent 系（`RPCPlugin`/`SharedRPCPlugin`）はこの3層をすべて内部で組み立てる。Opaque 系（`OpaqueRPCPlugin`/`SharedOpaqueRPCPlugin`）は `clientChannelCelltype`/`serverChannelCelltype` オプションでチャンネル層の実装セルタイプをユーザーが指定できる——「opaque」＝マーシャラから見てチャンネルの中身が不透明（差し替え可能）という意味。

## 3. `RPCPlugin`（Transparent・専用）の動作

`gen_plugin_decl_code`（99〜221行）が、呼び口結合1件ごとに次の3つの composite celltype を動的に CDL として生成・import する。

```tecs-cdl
/****** Client Side Channel ******/
composite <RPCチャンネル名>_ClientSide {
    entry <シグニチャ> eThroughEntry;
    call sTDR       cTDR;
    call sEventflag cEventflag;
    cell <marshaler celltype> <シグニチャ>_marshaler { ... };  // 呼び元側の引数マーシャリング
};

/****** Server Side Channel ******/
[active]
composite <RPCチャンネル名>_ServerSide {
    attr { PRI taskPriority; size_t stackSize; ATR attribute; };
    call <シグニチャ> cServerCall;
    call sTDR       cTDR;
    call sEventflag cEventflag;
    cell <unmarshaler celltype> <シグニチャ>_unmarshaler { ... };
    cell tRPCDedicatedTaskMain RPCTaskMain { cMain = ..._unmarshaler.eUnmarshalAndCallFunction; };
    cell tTask Task { cTaskBody = RPCTaskMain.eMain; priority = taskPriority; ... };  // サーバ側専用タスク
};

/****** Client & Server Combined Channel ******/
[active]
composite <RPCチャンネル名> {
    entry <シグニチャ> eThroughEntry;
    call  <シグニチャ> cCall;
    cell <RPCチャンネル名>_ClientSide RPCChannel_ClientSide { ... };
    cell <RPCチャンネル名>_ServerSide RPCChannel_ServerSide { ... };
};
```

`gen_through_cell_code`（226〜301行）が、実際の呼び口結合位置にこのチャンネルセルを配置し、`through`（[[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]]/[[work/active/tecsgen-plugins/NotifierPlugin|NotifierPlugin]]で見た region 境界の仕組み）にしたがって適切な region に置く。サーバ側は `tTask`（専用タスク、`taskPriority`/`stackSize`/`attribute` を指定可能）上で受け口関数を実行するため、**呼び元と呼び先は異なるタスクコンテキストで実行される**（結果としてタスク間・ドメイン間を安全にまたげる）。

## 4. プラグイン引数（共通・抜粋）

`GenTransparentMarshaler`/`GenOpaqueMarshaler` が共通で持つ引数（`RPCPluginArgProc`）：

| 引数 | 意味 |
|---|---|
| `TDRCelltype` | 使用する TDR 実装セルタイプ（デフォルト `tTDR`） |
| `PPAllocatorSize` | oneway `[in]` 配列引数がある場合に必須のプリポストアロケータサイズ |
| `taskPriority`/`stackSize` | サーバ側専用タスクの優先度・スタックサイズ |
| `noClientSemaphore` | true でクライアント側の排他制御セマフォ生成を省略（`RPCPlugin`/`OpaqueRPCPlugin`） |
| `semaphoreCelltype` | 排他制御に使うセマフォセルタイプ（デフォルト `tSemaphore`） |

Opaque 系のみ追加で `clientChannelCelltype`/`serverChannelCelltype`/`clientChannelCell`/`serverChannelCell`/`clientChannelInitializer`/`serverChannelInitializer`/`clientErrorHandler`/`serverErrorHandler`/`substituteAllocator`/`noServerChannelOpenerCode` を持つ（チャンネル実装の差し替えに必要な引数群）。`SharedOpaqueRPCPlugin` のみ `sharedChannelName`（共有グループを識別する名前）を追加で持つ。

## 5. 制約・注意点

- 全4種のヘッダコメントに共通して次の前提（制限事項）が明記されている: **呼び元・呼び先でエンディアン、`char`/`short`/`int_t`/`long_t`/`intptr_t` のサイズ、有符号・無符号のサイズが同一であること**。異機種間・異エンディアン環境をまたぐ RPC は想定されていない。
- CDL 実例が一件もなく（`through(...)` での呼び出しをリポジトリ全体で検索してゼロ件）、4章の使用パターンは `gen_*_code` の出力からの逆算。
- **HRPRPCPlugin・HRP2RPCPlugin は本ファミリーとは別物**: [[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]] の `add_through_plugin`（ドメインをまたぐ結合への自動介入ロジック）が実際に自動選択するのは、この4種ではなくカーネル専用の `HRP2RPCPlugin`（`channelCelltype=tMessagebufferChannel` を固定指定）だった（`HRP2Plugin.rb` 108〜110行で確認）。本ノートの4種はユーザーが `through` 指定子で明示的に呼び出す汎用プラグインであり、ドメイン境界の自動RPC挿入とは別の使用文脈になる——両者は同じ `ThroughPlugin` 基盤を使うが別実装であり、混同しないこと。`HRPRPCPlugin`/`HRP2RPCPlugin` 自体の詳細仕様は未着手。
- **発見（2026-08-15、trunk r3301更新に伴う[[work/active/tecsgen-plugins/DataPumpHolderPlugin|DataPumpHolderPlugin]]執筆時）**: `RPCPlugin#gen_marshaler_celltype_`（195〜201行）が生成するCDLに `generate( TransparentRPCSignaturePlugin, ... )` という呼び出しが埋め込まれているが、**`TransparentRPCSignaturePlugin` という名前のクラス定義・エイリアスはリポジトリ全体のどこにも存在しない**（実際にTransparent方式マーシャラを実装しているのは新規発見の `TransparentMarshalerPlugin`）。同じ誤ったクラス名は `DataPumpHolderPlugin` が生成するCDLにも独立に埋め込まれており、単発の見落としではない。この生成コードパスが実際に実行された場合、プラグインロードに失敗する可能性がある——実行時の検証は未実施。詳細は [[work/active/tecsgen-plugins/DataPumpHolderPlugin|DataPumpHolderPlugin]] 3節参照。

## Related

- [[tecsgen外部仕様]] — 6.2 `MultiPlugin`／`ThroughPlugin` ディスパッチ対応表・6.3 標準付属プラグイン一覧（本ノートで訂正）
- [[work/active/tecsgen-plugins/TracePlugin]] — 同じ `ThroughPlugin` 基盤・同じ5構文
- [[work/active/tecsgen-plugins/HRP2Plugin]] — ドメイン境界の自動RPC挿入（`add_through_plugin`）が実際に選ぶのは本ファミリーではなく `HRP2RPCPlugin` だったという対比
- [[work/active/tecsgen-plugins/DataPumpHolderPlugin]] — `TransparentRPCSignaturePlugin` 参照切れを共有する新規発見ファミリー
- [[North Star]] — カーネル対応プラグイン仕様書化の進捗管理

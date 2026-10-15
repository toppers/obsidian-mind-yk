---
date: 2026-08-16
description: "tecsgen外部仕様書 第6章（プラグインシステム）— 概要、プラグイン呼び出し規約、標準付属プラグイン、プラグイン引数の文法。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen外部仕様]] (2026-08-16, 25KB threshold). Chapter 6 of 10.

## 6. プラグインシステム

### 6.1 概要

CDL の `[generate(PluginName, ...)]` 指定子によりプラグインを呼び出す。セルタイプレベルとセルレベルの両方でプラグインを適用できる。

### 6.2 プラグイン呼び出し規約

`generate` には文法上異なる2つの形式があり、混同しやすい（`tecslib/core/bnf.y.rb` 762行・853行で確認、[[work/active/tecsgen-plugins/NotifierPlugin\|NotifierPlugin]] 執筆時に発見・訂正）。

```tecs-cdl
// (1) specifier 形式 — celltype/cell の [ ] 内。signature 引数は取らない（bnf.y.rb 762行 "# celltype, cell"）
[generate(PluginName, "param1=val1, param2=val2")]
celltype tMyType { ... };

cell tMyType MyCell {
    [generate(PluginName, "options")]
    cCall = OtherCell.eEntry;
};

// (2) statement 形式 — 独立文。namespace_identifier を第2引数に取り、対象は signature・celltype・composite celltype・cell のいずれでもよい
//     （bnf.y.rb 853行のコメントは "# signature plugin" だが、`Generate#initialize`（generate.rb）が対象の種別を判定して `apply_plugin` を呼ぶ。2026-10-12 ソースで確認）
generate(PluginName, sMySignature, "param1=val1, param2=val2");
generate(PluginName, nNs::tMyCelltype, "options");   // celltype 対象
generate(PluginName, nNs::MyCell, "options");        // cell 対象（例: HRPSVCThroughPlugin が HRPSVCBodyCellPlugin をこの形式で発行、HRPSVCThroughPlugin.rb:153）
```

`generate` の2形式に加えて、CDL 上の**付与位置**によって呼び出し可能なプラグイン種別が決まる。全ロード窓口 `PluginModule#load_plugin(plugin_name, superClass)`（`tecslib/core/pluginModule.rb`）を経由し、位置ごとに次の `superClass` が渡される（[[work/active/tecsgen-plugins/MrubyBridgePlugin\|MrubyBridgePlugin]] 執筆時に全呼び出し元を特定・確認）。

| CDL 上の付与位置 | `superClass` |
|---|---|
| `celltype` の `[generate(...)]` | `CelltypePlugin` |
| `composite celltype` の `[generate(...)]` | `CompositePlugin` |
| `cell` の `[generate(...)]` | `CellPlugin` |
| `signature` の `[generate(...)]` 指定子、または statement 形式で対象が signature の場合 | `SignaturePlugin`（`signature.rb:155`・`314`） |
| statement 形式 `generate(Plugin, <対象>, "opts");` で対象が celltype／composite celltype／cell の場合 | 対象の種別に応じて `CelltypePlugin`／`CompositePlugin`／`CellPlugin`（`Generate#initialize` が `apply_plugin` に委譲） |
| `join` の `through` 指定子 | `ThroughPlugin` |
| `region` の `domain(...)` 指定子（[[work/active/tecsgen-plugins/HRP2Plugin\|HRP2Plugin]] 参照） | `DomainPlugin` |
| `class`（HRMP）指定子（[[work/active/tecsgen-plugins/NotifierPlugin\|NotifierPlugin]] 参照） | `ClassPlugin` |

**`MultiPlugin` ディスパッチ**: プラグインクラスが `MultiPlugin`（`Plugin` 系列ではなく `Node` を継承する別系統）を継承している場合、`load_plugin` はそのクラス自身ではなく `plClass.get_plugin(superClass)` が返すクラスをロードする。これにより、1つのプラグイン名（例: `MrubyBridgePlugin`）を celltype・composite celltype・cell・signature のいずれに書いても、位置に応じた別の具象クラスが自動的に選択される——プラグイン名と実際にロードされるクラスが一致しない唯一のケース。詳細は [[work/active/tecsgen-plugins/MrubyBridgePlugin]] を参照。

### 6.3 標準付属プラグイン

| カテゴリ       | プラグイン名                                                 | 用途                               |
| ---------- | ------------------------------------------------------ | -------------------------------- |
| カーネル対応     | [[work/active/tecsgen-plugins/ATK1Plugin\|ATK1Plugin]] | OSEK/VDX 準拠 TOPPERS/ATK1 対応（AUTOSAR OS 準拠ではない。AUTOSAR 対応の後継 ATK2 とは別系統）。実体は `ATK1KernelPlugin` 等7ファイル。詳細仕様は個別ノート参照 |
| カーネル対応     | [[work/active/tecsgen-plugins/HRP2Plugin\|HRP2Plugin]] | TOPPERS/HRP2 対応。詳細仕様は個別ノート参照     |
| カーネル対応     | [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin\|HRP2SVCPlugin・HRP2RPCPlugin・HRP2KernelObjectPlugin]] | HRP2Plugin がドメイン境界をまたぐ結合に自動挿入する仲介プラグイン2種＋カーネルオブジェクトセル判定基盤。詳細仕様は個別ノート参照 |
| カーネル対応     | [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin\|HRP2KernelObjectPlugin 具象サブクラス群]] | TOPPERS/HRP2カーネルオブジェクト（タスク・セマフォ等）生成プラグイン10種。単機能8種＋テーブル駆動の汎用2種（HRP2ObjectPlugin・HRP2HandlerPlugin）が単機能プラグインの範囲を上回るオブジェクト種別まで対応する二層構造。詳細仕様は個別ノート参照 |
| カーネル対応     | [[work/active/tecsgen-plugins/HRPPlugin\|HRPPlugin]] | TOPPERS/HRP（HRP2の前身カーネル）対応ドメインプラグイン。ドメイン種別の語彙（"kernel"/"user"/"OutOfDomain"）がHRP2（"trusted"/"nontrusted"）と異なる。コード中にHRP2Pluginからの複製・改変の痕跡あり。詳細仕様は個別ノート参照 |
| カーネル対応     | [[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin\|HRPKernelObjectPlugin・HRPRPCPlugin・HRPSVCThroughPlugin・HRPSVCSignaturePlugin・HRPSVCBodyCellPlugin]] | HRPPluginのドメイン境界仲介プラグイン一式。HRP2側にない関数単位のドメインアクセス制御（`restrict_acptn_<func>`）とOpaqueマーシャリングRPCを実装。詳細仕様は個別ノート参照 |
| カーネル対応     | [[work/active/tecsgen-plugins/HRPKernelObjectPlugin\|HRPKernelObjectPlugin 具象サブクラス群3種]] | TOPPERS/HRPカーネルオブジェクト生成プラグイン3種（HRPTaskPlugin・HRPObjectPlugin・HRPHandlerPlugin）。HRP2側の単機能8種＋汎用2種の二層構造と同型だが単機能側はTaskのみに縮小。HRPファミリー全10ファイル完走。詳細仕様は個別ノート参照 |
| カーネル対応     | [[work/active/tecsgen-plugins/FMPPlugin\|FMPPlugin・FMPObjectPlugin・FMPHandlerPlugin]] | TOPPERS/FMP3（マルチプロセッサ）対応。HRP/HRP2の`domain(...)`（信頼ドメイン境界）ではなく`class(...)`（`ClassPlugin`、プロセッサ配置境界）を使う別系統。全3ファイルで完走。詳細仕様は個別ノート参照 |
| カーネル対応     | [[work/active/tecsgen-plugins/HRMPPlugin\|HRMPPlugin・HRMPDomainPlugin・HRMPClassPlugin・HRMPKernelObjectPlugin]] | TOPPERS/HRMP3対応。`MultiPlugin`で`domain(...)`と`class(...)`両方にディスパッチし、HRPの信頼ドメイン軸とFMPのクラス（プロセッサ配置）軸を1カーネルに統合。SVC/RPC仲介はHRPSVCThroughPlugin/HRPRPCPluginを再利用し専用プラグインを持たない。全4ファイルで完走、北極星未追跡3ファミリー完了。詳細仕様は個別ノート参照 |
| カーネル対応     | [[work/active/tecsgen-plugins/NotifierPlugin\|NotifierPlugin]] | ASP3 タイムイベント通知。実クラス名は `NotifierPlugin`（`ASP3` は用途カテゴリの通称、`ASP3NotifierPlugin` というクラスは存在しない）。詳細仕様は個別ノート参照 |
| mruby ブリッジ | [[work/active/tecsgen-plugins/MrubyBridgePlugin\|MrubyBridgePlugin]] | mruby ↔ TECS ブリッジ。実体5ファイル（`MultiPlugin` ディスパッチの実例）。詳細仕様は個別ノート参照 |
| mruby ブリッジ | [[work/active/tecsgen-plugins/Mruby2CBridgePlugin\|Mruby2CBridgePlugin]] | TECS シグニチャを mruby インタプリタなしに C から mruby ブリッジ流儀で駆動可能にする合成プラグイン。内部で `MrubyBridgePlugin`・`TECS2CBridgePlugin`・`C2TECSBridgePlugin` を組み合わせる。詳細仕様は個別ノート参照 |
| mruby ブリッジ | [[work/active/tecsgen-plugins/MrubyInfoBridgePlugin\|MrubyInfoBridgePlugin]] | TECSInfo を使った mruby ブリッジ（V1.7.0）。実体3ファイル。MrubyBridgePlugin と違い対象セルを実行時に文字列パスで検索・検証してバインドする。詳細仕様は個別ノート参照 |
| トレース       | [[work/active/tecsgen-plugins/TracePlugin\|TracePlugin]] | `ThroughPlugin` の参照実装。受け口呼び出しの前後を引数値付きでsyslogへ記録。詳細仕様は個別ノート参照 |
| トレース       | TLVTracePlugin                                         | TLV 形式トレース。**このリポジトリに実体（`.rb`ファイル）が存在しない**——`TLVTrace` で全文検索してゼロ件。別リポジトリ／未実装の可能性、要確認 |
| RPC        | [[work/active/tecsgen-plugins/RPCPlugin\|RPCPlugin]]（実クラス名。「TransparentRPCPlugin」は誤記） | Transparent・専用チャンネル。詳細仕様は個別ノート参照 |
| RPC        | [[work/active/tecsgen-plugins/RPCPlugin\|OpaqueRPCPlugin]] | Opaque（チャンネル実装差し替え可）・専用チャンネル。詳細仕様は個別ノート参照 |
| RPC        | [[work/active/tecsgen-plugins/RPCPlugin\|SharedRPCPlugin]] | Transparent・共有チャンネル（「共有メモリ」ではなく複数呼び口間でのチャンネルインスタンス共有）。詳細仕様は個別ノート参照 |
| RPC        | [[work/active/tecsgen-plugins/RPCPlugin\|SharedOpaqueRPCPlugin]] | Opaque・共有チャンネル。詳細仕様は個別ノート参照 |
| C インタフェース  | [[work/active/tecsgen-plugins/CInterfaceBridgePlugin\|C2TECSBridgePlugin]] | C コード → TECS 受け口呼び出し。一次資料 `doc/C2TECSBrdigePlugin.txt`・実使用例2件あり。詳細仕様は個別ノート参照 |
| C インタフェース  | [[work/active/tecsgen-plugins/CInterfaceBridgePlugin\|TECS2CBridgePlugin]] | TECS セル → C 変換（実クラス名は `TECS2CBridgePlugin`。`TECS2CPlugin` というクラスは存在しない。[[work/active/tecsgen-plugins/Mruby2CBridgePlugin\|Mruby2CBridgePlugin]] 執筆時に判明）。単独使用例・一次資料はなく、実使用は Mruby2CBridgePlugin 内部生成のみ。詳細仕様は個別ノート参照 |
| 繰り返し生成     | [[work/active/tecsgen-plugins/RepeatCellPlugin\|RepeatCellPlugin]] | セル名末尾の数字を基準に count=N 回複製。CDLテキストを生成し再取り込みする方式。`allocator`/`id`/`through`指定子は複製に引き継がれない（著者コメントで既知の制約と明記）。詳細仕様は個別ノート参照（2026-08-15完成） |
| 繰り返し生成     | [[work/active/tecsgen-plugins/RepeatCellPlugin\|RepeatJoinPlugin]] | 呼び口配列の添字0の結合を種に count=N 回複製。CDLテキストを介さず`Join`オブジェクトを直接モデルへ追加する方式。詳細仕様は個別ノート参照（2026-08-15完成） |
| データ連携       | [[work/active/tecsgen-plugins/DataPumpHolderPlugin\|DataPumpHolderPlugin]] | データ生成側/消費側を疎結合にする2シグニチャ＋最大10種のセルタイプ/複合セルタイプを合成生成。trunk r3301更新で新規出現（2026-01-04、この調査で最も新しいプラグイン）。詳細仕様は個別ノート参照（2026-08-15完成） |
| RPC内部実装      | [[work/active/tecsgen-plugins/DataPumpHolderPlugin\|TransparentMarshalerPlugin]] | RPCPluginのTransparent方式マーシャラ/アンマーシャラ生成本体。trunk r3301更新で新規出現。生成CDLが参照する`TransparentRPCSignaturePlugin`という名前がリポジトリのどこにも定義されていない参照切れを発見。詳細仕様は個別ノート参照（2026-08-15完成） |
| Cインタフェース生成 | [[work/active/tecsgen-plugins/CIfGenPlugin\|CIfGenPlugin（`MultiPlugin`、実体3ファイル）]] | 非TECS Cコードから特定セルの受け口関数を直接呼び出せる`*_cif.h`ヘッダを生成。C2TECSBridgePlugin/TECS2CBridgePluginとは別系統（CDLグラフの外へセルを露出）。詳細仕様は個別ノート参照（2026-08-15完成） |
| C++インタフェース生成 | [[work/active/tecsgen-plugins/CppIfGenPlugin\|CppIfGenPlugin（`MultiPlugin`、実体3ファイル）]] | CIfGenPluginのC++版だが実装は別物——フラットマクロでなく、celltypeごとに1つのC++クラス（entry port単位でネストしたインタフェースクラス）を生成。`$Id`不一致がCIfGenPluginと一字一句同一で、CIfGenPlugin自体からの複製と推測。詳細仕様は個別ノート参照（2026-08-15完成） |
| TECSInfo         | [[work/active/tecsgen-plugins/TECSInfoPlugin\|TECSInfoPlugin・TECSInfoCompoPlugin（実体2ファイル）]] | MrubyInfoBridgePluginが実行時に使う`TECSInfo`イントロスペクションAPIの生成側と確認。CDLモデル全体（セルタイプ・セル・シグニチャ等）を実行時参照可能にするCデータ構造一式を生成、`--unoptimize-entry`を自動強制する副作用あり。詳細仕様は個別ノート参照（2026-08-15完成） |

### 6.4 プラグイン引数の文法

プラグイン引数は `param=value` 形式のカンマ区切りリスト。値に特殊文字を含む場合は引用符で囲む。

---


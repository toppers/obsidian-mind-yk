---
date: 2026-05-31
tags: [tecs, plugin]
type: concept
status: active
description: "tecsgenの機能を拡張するプラグイン群。カーネル対応・[[mruby-tecs]]ブリッジ・RPC・トレース等。"
---

# TECS プラグイン

TECSプラグインは、[[wiki-tecsgen]]の機能を拡張するモジュールです。

## 種類

### カーネル対応プラグイン

- [[plugin-notifier]] ([[asp3-tecs]])
- 詳細リファレンスは [[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]]・[[work/active/tecsgen-plugins/ATK1Plugin|ATK1Plugin]]（TECS外部仕様書シリーズ、2026-08-14）に作成済み。ATK1Plugin は OSEK/VDX 準拠 ATK1 向けで、AUTOSAR OS 準拠の [[atk2-tecs|ATK2]] とは別系統
- HRP2Plugin のドメイン境界仲介プラグイン2種＋基盤クラスは [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin|HRP2SVCPlugin・HRP2RPCPlugin・HRP2KernelObjectPlugin]]（2026-08-15完成）参照。カーネルオブジェクト生成の具象サブクラス10種は [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2KernelObjectPlugin 具象サブクラス群]]（2026-08-15完成、単機能8種＋テーブル駆動の汎用2種の二層構造）参照でHRP2系ファミリーは完走。
- `HRP`（無印、HRP2の前身カーネル）ファミリーは**全10ファイル完走（2026-08-15）**。エントリポイントは [[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin・HRPKernelObjectManager]]——HRP2Pluginを複製・改名して作られた痕跡がコード中に残る。ドメイン境界仲介プラグイン一式は [[HRPDomainBoundaryPlugin(AIが説明用に作成)|HRPKernelObjectPlugin・HRPRPCPlugin・HRPSVCThroughPlugin・HRPSVCSignaturePlugin・HRPSVCBodyCellPlugin]]——HRP2側にない関数単位ドメインアクセス制御とOpaqueマーシャリングRPCを発見。具象サブクラス3種は [[work/active/tecsgen-plugins/HRPKernelObjectPlugin|HRPKernelObjectPlugin 具象サブクラス群]]——HRP2と同じ二層構造だが単機能側はTaskのみに縮小
- `FMP`（TOPPERS/FMP3マルチプロセッサカーネル）ファミリーは**全3ファイル完走（2026-08-15）**。[[work/active/tecsgen-plugins/FMPPlugin|FMPPlugin・FMPObjectPlugin・FMPHandlerPlugin]]——HRP/HRP2の`DomainPlugin`（`domain(...)`、信頼ドメイン境界）とは別系統の`ClassPlugin`（`class(...)`、プロセッサ配置境界）を使うと判明。クロスプロセッサRPC仲介は実在しないクラス名を参照する死コードのみで未実装
- `HRMP`（TOPPERS/HRMP3対応）ファミリーは**全4ファイル完走（2026-08-15）**。[[work/active/tecsgen-plugins/HRMPPlugin|HRMPPlugin・HRMPDomainPlugin・HRMPClassPlugin・HRMPKernelObjectPlugin]]——`MultiPlugin`で`domain(...)`/`class(...)`両方にディスパッチし、HRPの信頼ドメイン軸とFMPのクラス軸を1カーネルに統合する設計（名前どおり「HR(P)+MP」）。SVC/RPC仲介は専用プラグインを持たずHRP側をそのまま再利用。**これで北極星に一度も載っていなかった3ファミリー（HRP・FMP・HRMP）すべてが完了**
- [[PluginCoverageAudit(AIが説明用に利用)|プラグインカバレッジ監査]]（2026-08-15）: カーネルドメイン系完走を機に`tecslib/plugin/`全83ファイルを完全ファイル一覧と突き合わせ。**カーネルドメイン系の外に3つの新規未追跡領域を発見**——`CIfGenPlugin`・`CppIfGenPlugin`（ともに`MultiPlugin`、C/C++インタフェース生成と推測）・`TECSInfoPlugin`（MrubyInfoBridgePluginが使う`TECSInfo`APIの生成側と推測）。カタログには載っていたが個別仕様化していなかった`RepeatCellPlugin`・`RepeatJoinPlugin`も発見
  - [[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin]]（2026-08-15完成）: 非TECS Cコードから特定セルの受け口を直接呼べる`*_cif.h`ヘッダを生成する機構と判明。[[plugin-c2tecs|C2TECSBridgePlugin]]がCDL結合グラフの内側へCを持ち込むのと逆方向。3ファイルすべての`$Id`が自分自身でなく複製元の基底クラスファイル名を指す一貫した痕跡あり
  - [[work/active/tecsgen-plugins/CppIfGenPlugin|CppIfGenPlugin]]（2026-08-15完成）: CIfGenPluginのC++版だが実装は別物——マクロでなくcelltype単位のC++クラス・シグニチャ単位の抽象インタフェースを生成。`$Id`不一致の文字列がCIfGenPluginと完全一致し、共通テンプレートでなくCIfGenPlugin自体からの複製と推測
  - [[work/active/tecsgen-plugins/TECSInfoPlugin|TECSInfoPlugin]]（2026-08-15完成）: [[plugin-mruby-info-bridge|MrubyInfoBridgePlugin]]が使う`TECSInfo`実行時イントロスペクションAPIの供給元と確認。CDLモデル全体を実行時参照可能にするCデータ構造一式を生成、一時CDLファイル生成+`Import.new`という他に例のない手法、`--unoptimize-entry`自動強制の副作用あり
  - [[work/active/tecsgen-plugins/RepeatCellPlugin|RepeatCellPlugin・RepeatJoinPlugin]]（2026-08-15完成）: セル名末尾の数字を自動インクリメントしてN個複製。RepeatCellPluginはCDLテキスト生成+再取り込み、RepeatJoinPluginは`Join`オブジェクト直接追加という異なる実現方式。**これでカバレッジ監査の4候補すべてが完了**
- trunk最新化に伴う再監査（2026-08-15）: `svn info`でSVN作業コピーが trunk r3302 以降へ更新済みと判明（当初「3301」と記録、r3301 は trunk のリビジョンではないため2026-10-22訂正）、`tecslib/plugin/`のファイル数が83→85に増加。新規発見: [[work/active/tecsgen-plugins/DataPumpHolderPlugin|DataPumpHolderPlugin・TransparentMarshalerPlugin]]（2026-08-15完成）——DataPumpHolderPluginはデータ生成側/消費側を疎結合にする合成生成プラグイン（この調査で最も新しい、唯一ソース自身に設計ドキュメントを持つ）、TransparentMarshalerPluginは[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]]のTransparent方式マーシャラ実装本体。両者が生成するCDLと既存のRPCPlugin自身のコードが、定義の存在しないクラス名`TransparentRPCSignaturePlugin`を共通して参照している参照切れを発見し、RPCPlugin.mdにも追記（2026-10-22 追記: この参照切れは trunk r3307 で`TransparentRPCSignaturePlugin.rb`が追加され解消。[[work/active/tecsgen-plugins/DataPumpHolderPlugin|経緯]]）。既知の未確認事項はTLVTracePlugin（実体不明）のみ

### mrubyブリッジプラグイン

- [[plugin-mruby-bridge]] — MrubyBridgePlugin（詳細は [[work/active/tecsgen-plugins/MrubyBridgePlugin|MrubyBridgePlugin 仕様書]] 参照、2026-08-14完成）
- [[plugin-mruby-info-bridge]] — MrubyInfoBridgePlugin（詳細は [[work/active/tecsgen-plugins/MrubyInfoBridgePlugin|MrubyInfoBridgePlugin 仕様書]] 参照、2026-08-14完成。mrubyブリッジ系3件すべて完了）

### RPCプラグイン

- RPCPlugin（実クラス名。「TransparentRPCPlugin」は誤記）, OpaqueRPCPlugin, SharedRPCPlugin, SharedOpaqueRPCPlugin（詳細は [[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin 仕様書]] 参照、2026-08-14完成。4種を横断的に1ノートで扱う）

### Cインタフェースプラグイン

- [[plugin-c2tecs]] — C2TECSBridgePlugin（C → TECS 受け口呼び出し）
- TECS2CBridgePlugin（TECS 受け口 → C 変換、逆方向。単独スタブページなし）（両者とも詳細は [[CInterfaceBridgePlugin(説明用にAIが作成)|C2TECSBridgePlugin・TECS2CBridgePlugin 仕様書]] 参照、2026-08-14完成。名前の付いたカテゴリ完走）

### その他

- [[plugin-repeat-cell]] — RepeatCellPlugin
- TracePlugin（詳細は [[work/active/tecsgen-plugins/TracePlugin|TracePlugin 仕様書]] 参照、2026-08-14完成）
- TLVTracePlugin（未作成。リポジトリに実体が見つからず要確認——[[work/active/tecsgen-plugins/TracePlugin|TracePlugin 仕様書]] 冒頭参照）

## See Also

- [[wiki-tecsgen]]
- [[tecs-overview]]

## Counter-Arguments and Gaps

多くのプラグインリファレンスが未作成 (to be written)。

---
date: 2026-08-20
description: "work/active/tecsgen-plugins/ 配下の全プラグイン仕様書・監査ノートへのインデックス"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
  - plugin
  - index
---

# tecsgen プラグイン仕様書 インデックス

`work/active/tecsgen-plugins/` 配下の全ノートへのリンク一覧。全体の進捗・未追跡領域は [[PluginCoverageAudit(AIが説明用に利用)|PluginCoverageAudit(AIが説明用に利用)]] を参照。

## ノート一覧

- [[work/active/tecsgen-plugins/ATK1Plugin|ATK1Plugin]] — ATK1*Plugin（7ファイル）。OSEK/VDX 準拠 TOPPERS/ATK1 の OIL オブジェクトを CDL セル属性から生成する celltype プラグイン群
- [[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin]] — CIfGenPlugin・CIfGenCelltypePlugin・CIfGenCellPlugin。非TECS Cコードから受け口を直接呼び出せる `*_cif.h` ヘッダ生成
- [[CInterfaceBridgePlugin(説明用にAIが作成)|CInterfaceBridgePlugin(説明用)]] — C2TECSBridgePlugin・TECS2CBridgePlugin。プレーンCコードとTECS受け口/呼び口間の相互ブリッジセル生成
- [[work/active/tecsgen-plugins/CppIfGenPlugin|CppIfGenPlugin]] — CppIfGenPlugin・CppIfGenCelltypePlugin・CppIfGenCellPlugin。CIfGenPluginのC++版（本物のC++クラス生成）
- [[work/active/tecsgen-plugins/DataPumpHolderPlugin|DataPumpHolderPlugin]] — DataPumpHolderPlugin・TransparentMarshalerPlugin。trunk の r3302（release 1.9.1）で追加された2ファイル
- [[work/active/tecsgen-plugins/FMPPlugin|FMPPlugin]] — FMPPlugin・FMPObjectPlugin・FMPHandlerPlugin。TOPPERS/FMP3マルチプロセッサカーネル対応（クラス境界方式）
- [[work/active/tecsgen-plugins/HRMPPlugin|HRMPPlugin]] — HRMPPlugin・HRMPDomainPlugin・HRMPClassPlugin・HRMPKernelObjectPlugin。TOPPERS/HRMP3対応、HRPとFMPの軸を統合
- [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin|HRP2DomainBoundaryPlugin]] — HRP2SVCPlugin・HRP2RPCPlugin・HRP2KernelObjectPlugin。HRP2Pluginのドメイン境界仲介機構
- [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2KernelObjectPlugin]] — HRP2KernelObjectPluginの具象サブクラス10種。TOPPERS/HRP2カーネルオブジェクト生成
- [[work/active/tecsgen-plugins/HRP2Plugin|HRP2Plugin]] — HRP2Plugin本体。regionのdomain指定子でTOPPERS/HRP2信頼ドメイン境界を宣言
- [[HRPDomainBoundaryPlugin(AIが説明用に作成)|HRPDomainBoundaryPlugin(AIが説明用に作成)]] — HRPKernelObjectPlugin（抽象基底）・HRPRPCPlugin等5ファイル。HRPファミリーのドメイン境界仲介機構
- [[work/active/tecsgen-plugins/HRPKernelObjectPlugin|HRPKernelObjectPlugin]] — HRPKernelObjectPluginの具象サブクラス3種（HRPTaskPlugin・HRPObjectPlugin・HRPHandlerPlugin）
- [[work/active/tecsgen-plugins/HRPPlugin|HRPPlugin]] — HRPPlugin本体とHRPKernelObjectManager。TOPPERS/HRPカーネル向けドメインプラグイン
- [[work/active/tecsgen-plugins/Mruby2CBridgePlugin|Mruby2CBridgePlugin]] — mrubyインタプリタなしにCコードからmrubyブリッジ流儀でTECSシグニチャを駆動する合成プラグイン
- [[work/active/tecsgen-plugins/MrubyBridgePlugin|MrubyBridgePlugin]] — MrubyBridgePlugin（実体5ファイル）。mrubyスクリプトからTECS受け口を呼び出すブリッジセルタイプ生成
- [[work/active/tecsgen-plugins/MrubyInfoBridgePlugin|MrubyInfoBridgePlugin]] — MrubyInfoBridgePlugin（実体3ファイル）。TECSInfo APIを使う動的版mrubyブリッジ
- [[work/active/tecsgen-plugins/NotifierPlugin|NotifierPlugin]] — ASP3カーネルのタイムイベント通知（周期・アラーム）セルタイププラグイン
- [[PluginCoverageAudit(AIが説明用に利用)|PluginCoverageAudit(AIが説明用に利用)]] — `tecslib/plugin/`全83ファイルとの突き合わせ監査。未追跡領域の発見記録
- [[work/active/tecsgen-plugins/tecsgen-plugins SVN履歴一覧|tecsgen-plugins SVN履歴一覧]] — `tecslib/plugin/*Plugin.rb` 76ファイルのうち74件のSVN履歴（最古・最新のリビジョンとコミット数、2026-10-22 取得）。残り2件の履歴は DataPumpHolderPlugin に記載
- [[work/active/tecsgen-plugins/RepeatCellPlugin|RepeatCellPlugin]] — RepeatCellPlugin・RepeatJoinPlugin。セルの繰り返し生成機構
- [[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]] — RPCPlugin・OpaqueRPCPlugin・SharedRPCPlugin・SharedOpaqueRPCPlugin。呼び口結合間のRPCチャンネル自動生成
- [[work/active/tecsgen-plugins/TECSInfoPlugin|TECSInfoPlugin]] — TECSInfoPlugin・TECSInfoCompoPlugin。CDLモデル全体の実行時イントロスペクション機構
- [[work/active/tecsgen-plugins/TracePlugin|TracePlugin]] — ThroughPluginの参照実装。受け口呼び出しをsyslogへトレース記録

## Description（AIへの質問と回答の生記録）

`Description/` 配下は `verbatim: true` の生キャプチャ（frontmatter の必須項目は問わない）。

- [[HRP2のgenerate文一覧]] — HRP2系プラグインを呼ぶ generate 文の一覧
- [[namespace の使い方]] — CDL の namespace の使い方
- [[plugin-category]] — プラグインの分類表
- [[region を解釈するのはどこか]] — region を解釈する Region クラスの所在
- [[TECSInfoPluginをgenerate文で呼び出すと何を生成されるのか]] — TECSInfoPlugin を generate 文で呼んだときの生成物

## Related

- [[tecsgen外部仕様]] — 6.3 標準付属プラグイン一覧
- [[tecsgen内部仕様]]
- [[work/Index]]

---
date: 2026-09-22
description: "tecsgen-python3（Ruby版tecsgenのPython3移植）のプラグイン仕様書インデックスの骨子。Ruby版 tecsgen-plugins の21ノート構成に対応させた移植対応表のみ確定、各プラグインの仕様は未執筆（2026-09-22時点）"
project: tecsgen-python3
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

# tecsgen プラグイン-python3 仕様書 インデックス

> [!info] 文書状態
> **骨子のみ（2026-09-22）** — Ruby 版 [[tecsgen-plugins]] の仕様書構成に対応する移植対応表を置いただけの段階。Python3 版のプラグインは1件も実装・仕様化されていない。Python3 版コード（`E:/Ccur/python3/tecsgen-python3`）は未調査（TBC）。

Ruby 実装のプラグイン仕様書は [[tecsgen-plugins]] をインデックスとする21ノート（＋カバレッジ監査）にまとまっており、`tecslib/plugin/` の全83ファイル（直下76＋`lib/`7、2026-08-15 の [[work/active/tecsgen-plugins/PluginCoverageAudit|PluginCoverageAudit]] 実測）を対象としている。本書はその Python3 移植側のインデックスとして、同じ粒度（1ファミリー＝1ノート）でノートを起こす方針を採る。

プラグイン機構そのもの（ロード規約・ディスパッチ）は [[tecsgen-python3内部仕様]] 9章、CDL から見たプラグインの使い方は [[tecsgen-python3外部仕様]] 6章の担当。本書は個々のプラグインの移植状況を追う。

## 移植方針（未決定事項を含む）

- **プラグインの記述言語が Ruby から Python3 に変わる** — Ruby 版は `plugin.rb`/`pluginModule.rb` による動的ロードと `MultiPlugin` ディスパッチ（`MultiPlugin < Node`、`Plugin` の子ではない）。Python3 版はモジュール import ベースになるため、全プラグインが機械的移植ではなく書き直しになる。
- **移植の受入基準は生成物の一致** — 各プラグインが出力する CDL／C コードが Ruby 版と一致することを基準にする（[[tecsgen-python3内部仕様]] 8章と共通）。
- **移植対象範囲は未決定（要決定）** — 83ファイル全量を移植するのか、まず参照実装（TracePlugin）＋RPC 系に絞るのかが決まっていない。mruby 系ブリッジ（MrubyBridge・MrubyInfoBridge・Mruby2CBridge、計11ファイル）を移植対象に含めるかも未決定。決定したら Decision Record 化する。
- **Ruby版の既知の問題3件を持ち込まない** — [[tecsgen内部仕様]] 9.7 記録の `TransparentRPCSignaturePlugin` 参照切れ、FMP の RPC 死コード、CppIfGen の二重無効化コード（いずれも実行時の再現確認なし）。該当プラグインの移植時に扱いを決める。

## 移植対応表（Ruby版ノート → Python3版）

| Ruby版ノート | 対象 | 優先度（案・TBC） | Python3版の状態 |
|---|---|---|---|
| [[work/active/tecsgen-plugins/TracePlugin\|TracePlugin]] | ThroughPlugin の参照実装 | 高（最小の移植検証対象） | 未着手 |
| [[work/active/tecsgen-plugins/RPCPlugin\|RPCPlugin]] | RPC 4種＋マーシャラ共有モジュール | 高 | 未着手 |
| [[work/active/tecsgen-plugins/RepeatCellPlugin\|RepeatCellPlugin]] | RepeatCell・RepeatJoin | 中 | 未着手 |
| [[work/active/tecsgen-plugins/NotifierPlugin\|NotifierPlugin]] | ASP3 タイムイベント通知 | 中 | 未着手 |
| [[work/active/tecsgen-plugins/CIfGenPlugin\|CIfGenPlugin]] | `*_cif.h` 生成（MultiPlugin） | 中 | 未着手 |
| [[work/active/tecsgen-plugins/CppIfGenPlugin\|CppIfGenPlugin]] | CIfGen の C++ 版（MultiPlugin） | 中（既知の問題あり） | 未着手 |
| [[work/active/tecsgen-plugins/CInterfaceBridgePlugin\|CInterfaceBridgePlugin]] | C2TECSBridge・TECS2CBridge | 中 | 未着手 |
| [[work/active/tecsgen-plugins/TECSInfoPlugin\|TECSInfoPlugin]] | 実行時イントロスペクション生成側 | 中 | 未着手 |
| [[work/active/tecsgen-plugins/HRP2Plugin\|HRP2Plugin]] | HRP2 本体 | 低 | 未着手 |
| [[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin\|HRP2DomainBoundaryPlugin]] | HRP2 ドメイン境界仲介 | 低 | 未着手 |
| [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin\|HRP2KernelObjectPlugin]] | HRP2 具象サブクラス10種 | 低 | 未着手 |
| [[work/active/tecsgen-plugins/HRPPlugin\|HRPPlugin]] | HRP 本体・KernelObjectManager | 低 | 未着手 |
| [[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin\|HRPDomainBoundaryPlugin]] | HRP ドメイン境界仲介5ファイル | 低 | 未着手 |
| [[work/active/tecsgen-plugins/HRPKernelObjectPlugin\|HRPKernelObjectPlugin]] | HRP 具象サブクラス3種 | 低 | 未着手 |
| [[work/active/tecsgen-plugins/FMPPlugin\|FMPPlugin]] | FMP3 マルチプロセッサ対応 | 低（既知の問題あり） | 未着手 |
| [[work/active/tecsgen-plugins/HRMPPlugin\|HRMPPlugin]] | HRMP3 対応（HRP×FMP 統合） | 低 | 未着手 |
| [[work/active/tecsgen-plugins/ATK1Plugin\|ATK1Plugin]] | OSEK/VDX ATK1（7ファイル） | 低 | 未着手 |
| [[work/active/tecsgen-plugins/DataPumpHolderPlugin\|DataPumpHolderPlugin]] | DataPumpHolder・TransparentMarshaler | 低 | 未着手 |
| [[work/active/tecsgen-plugins/MrubyBridgePlugin\|MrubyBridgePlugin]] | mruby ブリッジ（実体5ファイル） | 対象外候補（要決定） | 未着手 |
| [[work/active/tecsgen-plugins/MrubyInfoBridgePlugin\|MrubyInfoBridgePlugin]] | 動的版 mruby ブリッジ（3ファイル） | 対象外候補（要決定） | 未着手 |
| [[work/active/tecsgen-plugins/Mruby2CBridgePlugin\|Mruby2CBridgePlugin]] | mruby 不要の合成プラグイン | 対象外候補（要決定） | 未着手 |

優先度は移植検証のしやすさから置いた**案であり未決定（TBC）**。カーネル依存の強い HRP/HRP2/FMP/HRMP/ATK1 を「低」としているのは移植の難易度ではなく、動作確認に実カーネル環境が要るためという理由による。

Python3 版のノートを起こす際は `work/active/tecsgen-plugins-python3/<PluginName>.md` とし、本表の「Python3版の状態」欄からリンクする。

## Notes

### Ruby版との対応で注意する点（未検証・TBC）

- **ノート粒度はファイル数と一致しない** — Ruby 版は「1ファミリー＝1ノート」で21ノート／83ファイル。Python3 版で実装単位が変われば粒度も変わりうる。
- **Plugin 基底クラス群8ファイル**（`CelltypePlugin`/`CompositePlugin`/`CellPlugin`/`SignaturePlugin`/`ThroughPlugin`/`DomainPlugin`/`ClassPlugin`/`MultiPlugin`）は Ruby 版では個別ノートを作らず [[tecsgen外部仕様]] 6.2 の概念記述で扱っている。Python3 版でも同様に内部仕様9章側で扱う想定。
- **マーシャリング共有モジュール4件**（`lib/GenTransparentMarshaler.rb` 等）は各利用プラグインのノートに分散記述されている。Python3 版で共通モジュールとして切り出すなら独立ノートが要る。
- **総ファイル数を固定値として前提にしない** — Ruby 版監査の教訓（17件→約79件→実測83件と推移）。Python3 版でも都度数え直す。

## Action Items

- [ ] 移植対象範囲を決定（全83ファイル vs 段階移植、mruby 系の扱い）— Decision Record 化
- [ ] TracePlugin を最小の移植検証対象として先行実装し、プラグインロード規約を確定
- [ ] 確定したロード規約を [[tecsgen-python3内部仕様]] 9章へ反映
- [ ] RPC 系＋マーシャラ共有モジュールの移植方針を決定
- [ ] Ruby版既知の問題3件（CppIfGen・FMP・TransparentRPCSignature）の扱いを決定
- [ ] Python3 版コードの現状（既存プラグイン実装の有無）を確認して本表を更新

## Context

- [[tecsgen-python3]] — 親ノート、作業全体の進捗管理
- [[tecsgen-plugins]] — Ruby 実装版のプラグイン仕様書インデックス（移植元・構成の基準）
- [[work/active/tecsgen-plugins/PluginCoverageAudit|PluginCoverageAudit]] — Ruby 版の全83ファイル突き合わせ監査（2026-08-15）
- [[tecsgen-python3内部仕様]] — 9章がプラグイン機構本体
- [[tecsgen-python3外部仕様]] — 6章がCDLから見たプラグイン
- Python3版最新コード `E:/Ccur/python3/tecsgen-python3`
- Ruby版最新コード `E:/Crepo/toppers-tecs-svn/toppers/tecsgen/branches/ykominami_r3033`

## Related

- [[tecsgen-python3]]
- [[tecsgen-plugins]] — Ruby実装版（移植元）
- [[tecsgen-python3内部仕様]]
- [[tecsgen-python3外部仕様]]
- [[tecsgen]] — Ruby実装版
- [[TECS開発]] — 開発進捗全体
- [[reference/Ruby動的ロードとPython対応|Ruby動的ロードとPython対応]] — `plugin.rb`/`pluginModule.rb`の動的ロードをPython importベースへ置き換える際の対応表（Action Items「プラグインロード規約を確定」の参照先）

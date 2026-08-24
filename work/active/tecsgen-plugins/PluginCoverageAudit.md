---
date: 2026-08-15
description: "tecslib/plugin/全83ファイルの完全ファイル一覧と既存仕様書ノートとの突き合わせ監査。既知5カテゴリ＋HRP2/HRP/FMP/HRMP完走後もなお2つの新規MultiPluginファミリー（CIfGen・CppIfGen）とTECSInfoPluginが未追跡と判明"
project: TECS
quarter: Q3-2026
status: active
tags: [work-note, tecs, tecsgen, spec, plugin]
---

# tecsgen プラグイン カバレッジ監査（2026-08-15）

[[work/active/tecsgen-plugins/HRMPPlugin|HRMPファミリー完走]]で北極星未追跡3ファミリー（HRP・FMP・HRMP）がすべて終わったのを機に、`tecslib/plugin/`（`lib/`サブディレクトリ含む）を`Glob`で完全に洗い出し、これまでに書いた全ノートと突き合わせた。結果——**「名前の付いた5カテゴリ＋HRP2/HRP/FMP/HRMPを完走した」だけでは、実は`tecslib/plugin/`の全ファイルをカバーしきれていなかった**。

## 1. 全体件数

`Glob "*.rb"`で確認した実ファイル数は**83ファイル**（`tecslib/plugin/`直下76＋`lib/`7）。北極星が最初に前提としていた「17件」はもちろん、10件目のノートで暫定的に置いた「約79ファイル」ともわずかにずれている——正確な数は都度数え直す必要があり、これ自体が「固定の総数を前提にしない」という10件目以降の方針を裏付けている。

## 2. カバー済み（既存ノートで完全に扱われている）

| カテゴリ | ファイル数 | 対応ノート |
|---|---|---|
| ATK1（OSEK/VDX） | 7 | [[work/active/tecsgen-plugins/ATK1Plugin\|ATK1Plugin]] |
| HRP2本体＋境界仲介 | 4 | [[work/active/tecsgen-plugins/HRP2Plugin\|HRP2Plugin]]・[[work/active/tecsgen-plugins/HRP2DomainBoundaryPlugin\|HRP2DomainBoundaryPlugin]] |
| HRP2具象サブクラス | 10 | [[work/active/tecsgen-plugins/HRP2KernelObjectPlugin\|HRP2KernelObjectPlugin]] |
| NotifierPlugin | 1 | [[work/active/tecsgen-plugins/NotifierPlugin\|NotifierPlugin]] |
| MrubyBridgePlugin一式＋共有モジュール2 | 7 | [[work/active/tecsgen-plugins/MrubyBridgePlugin\|MrubyBridgePlugin]] |
| Mruby2CBridgePlugin | 1 | [[work/active/tecsgen-plugins/Mruby2CBridgePlugin\|Mruby2CBridgePlugin]] |
| MrubyInfoBridgePlugin一式 | 3 | [[work/active/tecsgen-plugins/MrubyInfoBridgePlugin\|MrubyInfoBridgePlugin]] |
| TracePlugin | 1 | [[work/active/tecsgen-plugins/TracePlugin\|TracePlugin]] |
| RPC4種 | 4 | [[work/active/tecsgen-plugins/RPCPlugin\|RPCPlugin]] |
| Cインタフェースブリッジ2種 | 2 | [[work/active/tecsgen-plugins/CInterfaceBridgePlugin\|CInterfaceBridgePlugin]] |
| HRP（無印）全ファイル | 10 | [[work/active/tecsgen-plugins/HRPPlugin\|HRPPlugin]]・[[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin\|HRPDomainBoundaryPlugin]]・[[work/active/tecsgen-plugins/HRPKernelObjectPlugin\|HRPKernelObjectPlugin]] |
| FMP全ファイル | 3 | [[work/active/tecsgen-plugins/FMPPlugin\|FMPPlugin]] |
| HRMP全ファイル | 4 | [[work/active/tecsgen-plugins/HRMPPlugin\|HRMPPlugin]] |
| Plugin基底クラス群（実装対象でなく分類そのもの） | 8 | `CelltypePlugin`/`CompositePlugin`/`CellPlugin`/`SignaturePlugin`/`ThroughPlugin`/`DomainPlugin`/`ClassPlugin`/`MultiPlugin`——[[tecsgen外部仕様]] 6.2で概念として既述、個別スペックは不要 |
| マーシャリング共有モジュール | 4 | `lib/GenTransparentMarshaler.rb`・`lib/GenOpaqueMarshaler.rb`・`lib/GenParamCopy.rb`・`lib/GenHRP2Marshaler.rb`——[[work/active/tecsgen-plugins/RPCPlugin\|RPCPlugin]]・[[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin\|HRPRPCPlugin]]等の各ノートで使用実績を記述済み |
| GenAttMod/GenDefSvc | 1 | [[work/active/tecsgen-plugins/HRPPlugin\|HRPPlugin]] 6節 |

**合計 67ファイル**が既存ノートでカバー済み。

## 3. 発見: 未追跡の新規プラグインファミリーが2つ、単体プラグインが1つ

北極星が一度も追跡していなかったのはHRP・FMP・HRMPの3ファミリーだけではなかった。

### 3.1 CIfGenPlugin ファミリー（3ファイル、`MultiPlugin`）——完全未追跡

`CIfGenPlugin.rb`（`class CIfGenPlugin < MultiPlugin`）・`CIfGenCelltypePlugin.rb`・`CIfGenCellPlugin.rb`。名前と`MultiPlugin`継承——[[work/active/tecsgen-plugins/MrubyBridgePlugin|MrubyBridgePlugin]]・[[work/active/tecsgen-plugins/HRMPPlugin|HRMPPlugin]]に続く**この調査シリーズ4件目の`MultiPlugin`ディスパッチ実例**——から、CDL上の付与位置（celltype/cell）に応じて`CIfGenCelltypePlugin`/`CIfGenCellPlugin`のいずれかへ自動振り分けされる、C言語向けの何らかのインタフェース生成プラグインだと推測できる。[[work/active/tecsgen-plugins/CInterfaceBridgePlugin|C2TECSBridgePlugin/TECS2CBridgePlugin]]（`SignaturePlugin`系、シグニチャ単位のC↔TECS変換）とは別系統——`CIfGen`という名前と`Celltype`/`Cell`という2つのディスパッチ先から、セルタイプ／セル単位でCヘッダ相当のインタフェースを生成する仕組みと推測されるが、未読のため詳細・CDL構文は完全に未検証。

### 3.2 CppIfGenPlugin ファミリー（3ファイル、`MultiPlugin`）——完全未追跡

`CppIfGenPlugin.rb`（`class CppIfGenPlugin < MultiPlugin`）・`CppIfGenCellPlugin.rb`・`CppIfGenCelltypePlugin.rb`。CIfGenPluginとまったく同じ3ファイル構成（本体＋Celltype版＋Cell版）を持つ、C++版の対になるファミリー——**この調査シリーズ5件目の`MultiPlugin`実例**。CIfGen/CppIfGenの2ファミリーがペアで存在すること自体、[[work/active/tecsgen-plugins/CInterfaceBridgePlugin|C2TECSBridgePlugin/TECS2CBridgePlugin]]で見た「対称的な名前を持つプラグインが実態も対称とは限らない」教訓を踏まえ、実際に読むまで対称性を前提にしないほうがよい。

### 3.3 TECSInfoPlugin ファミリー（2ファイル）——完全未追跡

`TECSInfoPlugin.rb`（`class TECSInfoPlugin < CelltypePlugin`）・`TECSInfoCompoPlugin.rb`（複合セルタイプ版と推測）。[[work/active/tecsgen-plugins/MrubyInfoBridgePlugin|MrubyInfoBridgePlugin]]執筆時に見つけた「`TECSInfo`という実行時イントロスペクションAPI」——`MrubyInfoBridgeCellPlugin`が実行時に文字列パスでセルを検索するのに使っていた仕組み——の**生成側**がこのプラグインである可能性が高い。つまりMrubyInfoBridgePluginは消費者、TECSInfoPluginは提供者という関係にあると推測されるが、これも未読のため未検証。

### 3.4 RepeatCellPlugin・RepeatJoinPlugin——「知っていたが書いていなかった」2ファイル

[[tecsgen外部仕様]] 6.3表には「繰り返し生成」カテゴリとして`RepeatCellPlugin`（セルをcount=N回繰り返し生成）・`RepeatJoinPlugin`（結合配列をcount=N回繰り返し生成）が最初から記載されていたが、**個別ノートへのリンクが一度も張られておらず、実際のソースを読んでの詳細仕様化は行われていなかった**——CIfGen/CppIfGen/TECSInfoのような「存在自体を知らなかった」ギャップとは異なる、「カタログには載せたが本文を書き忘れていた」という別種のギャップ。

## 4. 発見: HRP2周辺の小さな取りこぼし2件

- **`HRP2Cache.rb`**——中身は`$Id`キーワードのみのコメント2行で実質空ファイル。ドキュメント化すべき内容が無いため対応不要と判断。
- **`HRP2PostHook.rb`**（`class HRP2PostHook`）——[[work/active/tecsgen-plugins/HRP2KernelObjectPlugin|HRP2KernelObjectPlugin]]に密結合した小さな支援クラス（「カーネルオブジェクトセルタイプはメモリ保護コード生成をスキップする」というポストフック）。独立した家族ではなく、HRP2KernelObjectPlugin.mdへの追記候補として残す。

## 5. 確認: OpaqueMarshalerPlugin は新規ギャップではない

`OpaqueMarshalerPlugin.rb`（`class OpaqueMarshalerPlugin < SignaturePlugin`）は`Grep`で参照元を確認したところ`HRPRPCPlugin.rb`からのみ参照されていた——[[work/active/tecsgen-plugins/HRPDomainBoundaryPlugin|HRPDomainBoundaryPlugin]] 6節で「Opaqueマーシャリング」とだけ記述していたものの具体的な実装クラス名であり、新規の未追跡ファミリーではなく既存ノートの記述をピンポイントに補強できる対象。

## 6.5 追記（2026-08-15、trunk更新反映）

ユーザー指示「tecsgenのtrunkの最新の状態を元に、tecsgen プラグイン仕様書を更新して」を受けて`E:\Crepo\ykominami-svn-2\tecsgen\`のSVN作業コピーを確認したところ、本監査時点（リビジョン不明・ファイル数83）から**リビジョン3301（2026-01-13）へ更新されており、ファイル数は85へ増加**していた。差分は`DataPumpHolderPlugin.rb`・`TransparentMarshalerPlugin.rb`の2ファイル——詳細仕様は[[work/active/tecsgen-plugins/DataPumpHolderPlugin|DataPumpHolderPlugin]]参照。これで本監査後に追加された既知の未追跡ファイルはすべて回収済み。**今後同様の更新確認をする場合は`svn info`でリビジョンを確認し、`tecslib/plugin/`の完全ファイル一覧（Glob）を取り直して差分を突き合わせる**、という手順を踏むこと。

## 6. 残タスクの整理

| 対象 | 状態 | 優先度の目安 |
|---|---|---|
| CIfGenPlugin（3ファイル） | 未読・未着手 | 高（完全未追跡の新規ファミリー） |
| CppIfGenPlugin（3ファイル） | 未読・未着手 | 高（同上） |
| TECSInfoPlugin（2ファイル） | 未読・未着手 | 中（MrubyInfoBridgePluginとの関係を検証する動機がある） |
| RepeatCellPlugin・RepeatJoinPlugin（2ファイル） | カタログ済み・未着手 | 低（小規模・構造は`ThroughPlugin`系と推測） |
| HRP2PostHook.rb | 未反映 | 低（既存ノートへの追記で足りる） |
| OpaqueMarshalerPlugin.rb | 実質確認済み | 対応不要（既存ノートの記述で十分） |
| TLVTracePlugin | 実体不明（別セッションで確認済み） | 対応不要（実体なし） |

**tecsgen外部仕様 6.3の表・北極星は、このカバレッジ監査の結果を踏まえて更新した**——「全カーネルドメインファミリー完了」を「カーネルドメインファミリーは完了、ただしC/C++インタフェース生成系とTECSInfo系という別の未追跡領域が新たに判明」という、より正確な状態に書き直す。

## Related

- [[tecsgen外部仕様]] — 6.3 標準付属プラグイン一覧（本監査の結果を反映）
- [[work/active/tecsgen-plugins/HRMPPlugin|HRMPPlugin]] — 直前に完走した北極星未追跡3ファミリーの最後の1つ
- [[work/active/tecsgen-plugins/CInterfaceBridgePlugin|CInterfaceBridgePlugin]] — CIfGen/CppIfGenと名前が紛らわしいが別系統（SignaturePlugin系 vs MultiPlugin系）
- [[work/active/tecsgen-plugins/MrubyInfoBridgePlugin|MrubyInfoBridgePlugin]] — TECSInfoPluginとの消費者/提供者関係が疑われる対比元
- [[North Star]] — プラグイン仕様書化の進捗管理。本監査でスコープを再拡張

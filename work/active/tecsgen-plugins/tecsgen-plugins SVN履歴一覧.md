---
date: 2026-10-22
description: "tecsgen 標準付属プラグイン76ファイルのうち、個別調査済みの2件を除く74件のSVN履歴一覧（最古・最新のリビジョンと日付、コミット数）。SVN作業コピー r3307 で取得"
project: TECS
quarter: Q4-2026
status: active
tags: [work-note, tecs, tecsgen, plugin, svn]
---

# tecsgen プラグインのSVN履歴一覧（74件）

`E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen\tecslib\plugin\*Plugin.rb` の76ファイル（一覧は [[work/active/tecsgen-plugins/plugin_list.txt|plugin_list.txt]]）のうち、`TransparentMarshalerPlugin`・`TransparentRPCSignaturePlugin` を除く74件について、各ファイルの `svn log -v`（作業コピー r3307、2026-10-22 取得）から最古・最新のコミットを集めた。2件は [[work/active/tecsgen-plugins/DataPumpHolderPlugin|DataPumpHolderPlugin]] 2〜3節に履歴を記録済み。

関連: [[work/active/tecsgen-plugins/tecsgen-plugins|tecsgen-plugins]]（プラグイン仕様書の索引）、[[PluginCoverageAudit(AIが説明用に利用)|プラグインカバレッジ監査]]。

> [!info] 読み方
> - 「最古」は `svn log` が名前変更・コピーをたどった先の最古のコミット。`branches/...` と出るものは、ブランチ上の履歴までたどった結果で、trunk に入った日とは限らない。
> - 「名前変更前」の4件（`Cell`・`Celltype`・`Signature`・`Through`）は旧ファイル名（小文字の `celltypePlugin.rb` など）だった時期のパスが取れていない。旧名は r1407 の移動ログから推測したもので、未確認 (TBC)。
> - 最新が r2952・r2955（2018-05-07）のものは、ヘッダや `$Id` を直す一括コミットだと思われる（推測）。実質的に中身が変わった最後の日とは限らない。
> - コミットメッセージと変更ファイルの内訳は取っていない（必要なら再取得）。

## 一覧（最古のリビジョン順）

| プラグイン | コミット数 | 最古 | 最古の場所 | 最新 |
|---|---|---|---|---|
| [[RPCPlugin SVN履歴_\|`RPCPlugin.rb`]] | 62 | r134 2008-06-10 | trunk（旧配置）（追加） | r3302 2026-06-07 |
| [[ThroughPlugin SVN履歴_\|`ThroughPlugin.rb`]] | 55 | r134 2008-06-10 | 名前変更前（旧名、パス未取得）（—） | r3225 2021-09-26 |
| [[TracePlugin SVN履歴_\|`TracePlugin.rb`]] | 42 | r134 2008-06-10 | trunk（旧配置）（追加） | r2952 2018-05-07 |
| [[OpaqueRPCPlugin SVN履歴_\|`OpaqueRPCPlugin.rb`]] | 59 | r205 2009-01-03 | trunk（旧配置）（追加） | r3155 2020-06-28 |
| [[SharedRPCPlugin SVN履歴_\|`SharedRPCPlugin.rb`]] | 48 | r489 2009-09-25 | trunk（旧配置）（追加） | r3155 2020-06-28 |
| [[CelltypePlugin SVN履歴_\|`CelltypePlugin.rb`]] | 29 | r1258 2011-02-28 | 名前変更前（旧名、パス未取得）（—） | r3302 2026-06-07 |
| [[SignaturePlugin SVN履歴_\|`SignaturePlugin.rb`]] | 27 | r1258 2011-02-28 | 名前変更前（旧名、パス未取得）（—） | r3225 2021-09-26 |
| [[SharedOpaqueRPCPlugin SVN履歴_\|`SharedOpaqueRPCPlugin.rb`]] | 27 | r1362 2011-05-03 | trunk（追加） | r3155 2020-06-28 |
| [[ATK1AlarmPlugin SVN履歴_\|`ATK1AlarmPlugin.rb`]] | 21 | r1407 2011-05-21 | branches/V1.B.0-trunk（追加） | r2955 2018-05-07 |
| [[ATK1ISRPlugin SVN履歴_\|`ATK1ISRPlugin.rb`]] | 21 | r1407 2011-05-21 | branches/V1.B.0-trunk（追加） | r2955 2018-05-07 |
| [[ATK1KernelPlugin SVN履歴_\|`ATK1KernelPlugin.rb`]] | 23 | r1407 2011-05-21 | branches/V1.B.0-trunk（追加） | r2955 2018-05-07 |
| [[ATK1ResourcePlugin SVN履歴_\|`ATK1ResourcePlugin.rb`]] | 21 | r1407 2011-05-21 | branches/V1.B.0-trunk（追加） | r2955 2018-05-07 |
| [[ATK1TaskPlugin SVN履歴_\|`ATK1TaskPlugin.rb`]] | 26 | r1407 2011-05-21 | branches/V1.B.0-trunk（追加） | r2955 2018-05-07 |
| [[CellPlugin SVN履歴_\|`CellPlugin.rb`]] | 16 | r1612 2011-11-27 | 名前変更前（旧名、パス未取得）（—） | r2952 2018-05-07 |
| [[RepeatCellPlugin SVN履歴_\|`RepeatCellPlugin.rb`]] | 12 | r1612 2011-11-27 | branches/V1.C.0-trunk/test/cellPlugin/RepeatCellPlugin.rb（追加） | r2952 2018-05-07 |
| [[RepeatJoinPlugin SVN履歴_\|`RepeatJoinPlugin.rb`]] | 11 | r1612 2011-11-27 | branches/V1.C.0-trunk/test/cellPlugin/RepeatJoinPlugin.rb（追加） | r2952 2018-05-07 |
| [[ATK1DelayTaskPlugin SVN履歴_\|`ATK1DelayTaskPlugin.rb`]] | 14 | r1807 2012-07-04 | trunk（追加） | r2955 2018-05-07 |
| [[ATK1EventPlugin SVN履歴_\|`ATK1EventPlugin.rb`]] | 13 | r1837 2012-07-15 | trunk（追加） | r2952 2018-05-07 |
| [[MrubyBridgePlugin SVN履歴_\|`MrubyBridgePlugin.rb`]] | 30 | r1906 2012-11-10 | trunk（追加） | r2952 2018-05-07 |
| [[OpaqueMarshalerPlugin SVN履歴_\|`OpaqueMarshalerPlugin.rb`]] | 10 | r1935 2013-03-31 | trunk（追加） | r3159 2020-07-05 |
| [[C2TECSBridgePlugin SVN履歴_\|`C2TECSBridgePlugin.rb`]] | 12 | r1948 2013-04-30 | trunk（追加） | r2952 2018-05-07 |
| [[TECS2CBridgePlugin SVN履歴_\|`TECS2CBridgePlugin.rb`]] | 11 | r1948 2013-04-30 | trunk（追加） | r2952 2018-05-07 |
| [[Mruby2CBridgePlugin SVN履歴_\|`Mruby2CBridgePlugin.rb`]] | 9 | r1951 2013-05-01 | trunk（追加） | r2952 2018-05-07 |
| [[DomainPlugin SVN履歴_\|`DomainPlugin.rb`]] | 13 | r2040 2014-04-14 | trunk（追加） | r3159 2020-07-05 |
| [[HRP2AlarmHandlerPlugin SVN履歴_\|`HRP2AlarmHandlerPlugin.rb`]] | 7 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[HRP2CyclicHandlerPlugin SVN履歴_\|`HRP2CyclicHandlerPlugin.rb`]] | 7 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[HRP2DataqueuePlugin SVN履歴_\|`HRP2DataqueuePlugin.rb`]] | 6 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[HRP2EventflagPlugin SVN履歴_\|`HRP2EventflagPlugin.rb`]] | 6 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[HRP2FixedSizeMemoryPoolPlugin SVN履歴_\|`HRP2FixedSizeMemoryPoolPlugin.rb`]] | 6 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[HRP2HandlerPlugin SVN履歴_\|`HRP2HandlerPlugin.rb`]] | 8 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[HRP2KernelObjectPlugin SVN履歴_\|`HRP2KernelObjectPlugin.rb`]] | 8 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[HRP2ObjectPlugin SVN履歴_\|`HRP2ObjectPlugin.rb`]] | 6 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[HRP2Plugin SVN履歴_\|`HRP2Plugin.rb`]] | 8 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[HRP2PriorityDataqueuePlugin SVN履歴_\|`HRP2PriorityDataqueuePlugin.rb`]] | 6 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[HRP2RPCPlugin SVN履歴_\|`HRP2RPCPlugin.rb`]] | 7 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[HRP2SVCPlugin SVN履歴_\|`HRP2SVCPlugin.rb`]] | 7 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[HRP2SemaphorePlugin SVN履歴_\|`HRP2SemaphorePlugin.rb`]] | 6 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[HRP2TaskPlugin SVN履歴_\|`HRP2TaskPlugin.rb`]] | 10 | r2224 2015-08-22 | trunk（追加） | r2952 2018-05-07 |
| [[NotifierPlugin SVN履歴_\|`NotifierPlugin.rb`]] | 28 | r2292 2015-11-24 | trunk（追加） | r3185 2020-11-11 |
| [[TECSInfoPlugin SVN履歴_\|`TECSInfoPlugin.rb`]] | 17 | r2622 2017-01-04 | branches/TECSInfo（追加） | r3159 2020-07-05 |
| [[MrubyBridgeCellPlugin SVN履歴_\|`MrubyBridgeCellPlugin.rb`]] | 10 | r2633 2017-04-02 | branches/TECSInfo（追加） | r3225 2021-09-26 |
| [[MrubyBridgeCelltypePlugin SVN履歴_\|`MrubyBridgeCelltypePlugin.rb`]] | 9 | r2633 2017-04-02 | branches/TECSInfo（追加） | r3077 2019-06-09 |
| [[MrubyBridgeSignaturePlugin SVN履歴_\|`MrubyBridgeSignaturePlugin.rb`]] | 11 | r2633 2017-04-02 | branches/TECSInfo（追加） | r3225 2021-09-26 |
| [[MultiPlugin SVN履歴_\|`MultiPlugin.rb`]] | 6 | r2633 2017-04-02 | branches/TECSInfo（追加） | r3263 2022-12-30 |
| [[CompositePlugin SVN履歴_\|`CompositePlugin.rb`]] | 4 | r2638 2017-05-29 | branches/TECSInfo（追加） | r2952 2018-05-07 |
| [[MrubyBridgeCompositePlugin SVN履歴_\|`MrubyBridgeCompositePlugin.rb`]] | 4 | r2638 2017-05-29 | branches/TECSInfo（追加） | r2952 2018-05-07 |
| [[HRPHandlerPlugin SVN履歴_\|`HRPHandlerPlugin.rb`]] | 4 | r2816 2018-03-13 | trunk（追加） | r2952 2018-05-07 |
| [[HRPKernelObjectPlugin SVN履歴_\|`HRPKernelObjectPlugin.rb`]] | 5 | r2816 2018-03-13 | trunk（追加） | r2952 2018-05-07 |
| [[HRPObjectPlugin SVN履歴_\|`HRPObjectPlugin.rb`]] | 3 | r2816 2018-03-13 | trunk（追加） | r2952 2018-05-07 |
| [[HRPPlugin SVN履歴_\|`HRPPlugin.rb`]] | 9 | r2816 2018-03-13 | trunk（追加） | r3191 2020-12-20 |
| [[HRPRPCPlugin SVN履歴_\|`HRPRPCPlugin.rb`]] | 12 | r2816 2018-03-13 | trunk（追加） | r3241 2021-11-21 |
| [[HRPTaskPlugin SVN履歴_\|`HRPTaskPlugin.rb`]] | 4 | r2816 2018-03-13 | trunk（追加） | r2952 2018-05-07 |
| [[MrubyInfoBridgeCellPlugin SVN履歴_\|`MrubyInfoBridgeCellPlugin.rb`]] | 1 | r3079 2019-06-09 | trunk（追加） | r3079 2019-06-09 |
| [[MrubyInfoBridgePlugin\|`MrubyInfoBridgePlugin.rb`]] | 1 | r3079 2019-06-09 | trunk（追加） | r3079 2019-06-09 |
| [[MrubyInfoBridgeSignaturePlugin SVN履歴_\|`MrubyInfoBridgeSignaturePlugin.rb`]] | 2 | r3079 2019-06-09 | trunk（追加） | r3225 2021-09-26 |
| `TECSInfoCompoPlugin.rb` | 1 | r3079 2019-06-09 | trunk（追加） | r3079 2019-06-09 |
| [[ClassPlugin SVN履歴_\|`ClassPlugin.rb`]] | 5 | r3089 2019-08-15 | trunk（追加） | r3211 2021-03-21 |
| [[FMPHandlerPlugin SVN履歴_\|`FMPHandlerPlugin.rb`]] | 9 | r3089 2019-08-15 | trunk（追加） | r3263 2022-12-30 |
| [[FMPObjectPlugin SVN履歴_\|`FMPObjectPlugin.rb`]] | 10 | r3089 2019-08-15 | trunk（追加） | r3263 2022-12-30 |
| [[FMPPlugin SVN履歴_\|`FMPPlugin.rb`]] | 13 | r3089 2019-08-15 | trunk（追加） | r3245 2021-12-18 |
| [[HRPSVCBodyCellPlugin SVN履歴_\|`HRPSVCBodyCellPlugin.rb`]] | 3 | r3159 2020-07-05 | trunk（追加） | r3172 2020-08-31 |
| [[HRPSVCSignaturePlugin SVN履歴_\|`HRPSVCSignaturePlugin.rb`]] | 2 | r3159 2020-07-05 | trunk（追加） | r3176 2020-10-25 |
| [[HRPSVCThroughPlugin SVN履歴_\|`HRPSVCThroughPlugin.rb`]] | 2 | r3159 2020-07-05 | trunk（追加） | r3165 2020-08-15 |
| [[HRMPClassPlugin SVN履歴_\|`HRMPClassPlugin.rb`]] | 9 | r3165 2020-08-15 | trunk（追加） | r3241 2021-11-21 |
| [[HRMPDomainPlugin SVN履歴_\|`HRMPDomainPlugin.rb`]] | 5 | r3165 2020-08-15 | trunk（追加） | r3211 2021-03-21 |
| [[HRMPKernelObjectPlugin SVN履歴_\|`HRMPKernelObjectPlugin.rb`]] | 8 | r3165 2020-08-15 | trunk（追加） | r3241 2021-11-21 |
| [[HRMPPlugin SVN履歴_\|`HRMPPlugin.rb`]] | 10 | r3165 2020-08-15 | trunk（追加） | r3225 2021-09-26 |
| [[CppIfGenCellPlugin SVN履歴_\|`CppIfGenCellPlugin.rb`]] | 2 | r3263 2022-12-30 | trunk（追加） | r3269 2023-07-26 |
| [[CppIfGenCelltypePlugin SVN履歴_\|`CppIfGenCelltypePlugin.rb`]] | 3 | r3263 2022-12-30 | trunk（追加） | r3269 2023-07-26 |
| [[CppIfGenPlugin SVN履歴_\|`CppIfGenPlugin.rb`]] | 2 | r3263 2022-12-30 | trunk（追加） | r3269 2023-07-26 |
| [[CIfGenCellPlugin SVN履歴_\|`CIfGenCellPlugin.rb`]] | 1 | r3265 2023-01-03 | trunk（追加） | r3265 2023-01-03 |
| [[CIfGenCelltypePlugin SVN履歴_\|`CIfGenCelltypePlugin.rb`]] | 2 | r3265 2023-01-03 | trunk（追加） | r3269 2023-07-26 |
| [[CIfGenPlugin SVN履歴_\|`CIfGenPlugin.rb`]] | 1 | r3265 2023-01-03 | trunk（追加） | r3265 2023-01-03 |
| [[DataPumpHolderPlugin\|`DataPumpHolderPlugin.rb`]] | 1 | r3302 2026-06-07 | trunk（追加） | r3302 2026-06-07 |

## 傾向

- **最古**: `RPCPlugin`・`TracePlugin`・`ThroughPlugin`（r134、2008-06-10）が最初。続いて `OpaqueRPCPlugin`（r205、2009-01）、`SharedRPCPlugin`（r489、2009-09）。
- **世代**: ATK1 系（2011-05）、RepeatCell / RepeatJoin（2011-11）、MrubyBridge 系（2012-11〜2017）、HRP2 系14件（r2224、2015-08-22）、HRP 系（r2816、2018-03-13）、FMP 系・Class（r3089、2019-08）、HRMP 系（r3165、2020-08）、CppIfGen 系（r3263、2022-12-30）、CIfGen 系（r3265、2023-01-03）、DataPumpHolder（r3302、2026-06-07）の順に増えている。
- **2020年以降も更新されているもの**: `RPCPlugin`・`CelltypePlugin`（r3302）、`SignaturePlugin`・`ThroughPlugin`・`MrubyBridgeCellPlugin`・`MrubyBridgeSignaturePlugin`・`MrubyInfoBridgeSignaturePlugin`（r3225）、`MultiPlugin`・`FMPHandlerPlugin`・`FMPObjectPlugin`・`CppIfGen*`（r3263〜r3269）。
- **コミットが1回だけ**: `CIfGenPlugin`・`CIfGenCellPlugin`・`DataPumpHolderPlugin`・`MrubyInfoBridgePlugin`・`MrubyInfoBridgeCellPlugin`・`TECSInfoCompoPlugin`。
- **コミット数が多い**: `RPCPlugin` 62、`OpaqueRPCPlugin` 59、`ThroughPlugin` 55、`SharedRPCPlugin` 48、`TracePlugin` 42。

## Related

- [[work/active/tecsgen-plugins/DataPumpHolderPlugin|DataPumpHolderPlugin]] — 調査済み2件（`TransparentMarshalerPlugin`・`TransparentRPCSignaturePlugin`）の履歴
- [[work/active/tecsgen-plugins/RPCPlugin SVN履歴_|RPCPlugin SVN履歴_]] — `RPCPlugin` 自身のSVN履歴（62コミットの全履歴と、r3306・r3307 時点の検証）
- [[work/active/tecsgen-plugins/tecsgen-plugins|tecsgen-plugins]] — 索引

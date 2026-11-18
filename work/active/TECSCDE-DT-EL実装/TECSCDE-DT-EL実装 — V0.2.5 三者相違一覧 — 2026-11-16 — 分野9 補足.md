---
date: 2026-11-16
description: "V0.2.5 三者相違一覧の分野9（診断・ログ・制約・IF一覧）のうち、照合表（コード・IPC）・未確認・解消済み・集計。25KB閾値で表と分けた。原文のまま。"
project: TECS
quarter: Q4-2026
status: active
verbatim: true
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

# TECSCDE-DT-EL実装 — V0.2.5 三者相違一覧 — 2026-11-16 — 分野9 補足

[[TECSCDE-DT-EL実装 — V0.2.5 三者相違一覧 — 2026-11-16]]の分割ノート（分野9 診断・ログ・制約・IF一覧の補足）。原文のまま。相違の表は[[TECSCDE-DT-EL実装 — V0.2.5 三者相違一覧 — 2026-11-16 — 分野9]]。

### コード照合表（一致分を含む全数）

ソース全体を `[EW]-[A-Z…]` で検索した結果（`E-DT-EL` 等の文書名の一部は除外）と、外部 09・内部 08/4H/8B/9.7/9C/7F/04E〜04G の表・本文を1対1で突き合わせました。「ソース」欄の重大度は生成箇所で確認したものです。

| コード | 外部仕様 | 内部仕様 | ソース（重大度・生成箇所） | 判定 |
|---|---|---|---|---|
| `G1015` | 09 9.1（G-code 相当の構文エラー。文言は tecsgen と一致を要しない） | 4H 4B.7 | error・`cdl/messages.ts:53-55`、`cdl/cst.ts:639` | 一致（位置ジャンプ不可は表#7） |
| `G1016` | 同上 | 4H 4B.7 | error・`cdl/messages.ts:49-51`、`cdl/cst.ts:632,641` | 一致（同上） |
| tecsgen の G/S コード | 09 9.1（tecsgen の文言をそのまま） | 9.4・9.7 | 行の severity のまま・`diagnostics/tecsgen-result-parser.ts:42-98` | 一致。コードが無い行は `ERROR`／`WARNING` をコードにする（未確認1） |
| `W-DUP-CELL` | 09 9.2（名前「セル名重複」のみ） | TS 8.3、4H | warning・`cdl/messages.ts:57-64`、`document-builder.ts:508` | 一致（外部にコード無し: 表#9） |
| `W-UNRESOLVED-CELLTYPE` | 09 9.2（名前のみ）。親 9.3.2 の例文と一致 | TS 8.3、4H | warning・`messages.ts:66-73`、`document-builder.ts:699`、`diagnostics/integrity.ts:23` | 重複計上（表#5） |
| `W-MISSING-JOIN-TARGET` | 09 9.2（名前のみ）。親 9.3.2 の例文と一致 | TS 8.3、4H | warning・`messages.ts:75-83`、`document-builder.ts:868` | 一致 |
| `W-COMPOSITE-UNSUPPORTED` | 09 9.2「存在自体は警告としない」 | 08「DT-ELでは使わない」 | 定数のみ・`messages.ts:30`（生成なし） | 一致 |
| `W-LAYOUT-DISCARDED` | 09 9.2（名前「レイアウト破棄」のみ） | TS 8.3、4H | warning・`tool-info.ts:352,375,387,422,435`、`document-builder.ts:608,617,627,635` | 一致（外部にコード無し: 表#9） |
| `W-LAYOUT-PARSE-ERROR` | 無し | 4H | warning・`tool-info.ts:319` | 外部に無い（表#8） |
| `W-NEWER-FORMAT` | 無し | 4H | warning・`tool-info.ts:303` | 外部に無い（表#8） |
| `W-UNRESOLVED-REF-FILE` | 09 9.2（名前「参照ファイル未解決」のみ） | TS 8.3、08、4H | warning・`messages.ts:119-125`、`integrity.ts:30`、`import-resolution.ts:190,198` | コード一致。文言は diff-05 #11 |
| `W-REQUIRE-PORT-HIDDEN` | 09 9.2 本文 | 4H、05B | warning・`messages.ts:105-112`、`document-builder.ts:724` | コード一致（数え方は担当外） |
| `W-PORT-SIGNATURE-UNRESOLVED` | 09 9.2 本文 | 03、4H | warning・`document-builder.ts:407-412` | コード一致（文言形式: 表#12、移動不可: 表#7） |
| `W-JOIN-INDEX-INCONSISTENT` | 09 9.2 表 | 4H に無い（diff-08 #16） | warning・`messages.ts:95-103`、`document-builder.ts:727` | 一致 |
| `W-AUTO-LAYOUT-OVERFLOW` | 09 9.2 表 | 4H、08 8.4 | warning・`messages.ts:86-91`、`document-builder.ts:664`、`auto-place-actions.ts:27` | 文言・場面が相違（表#11） |
| `W-ACTIVE-TOP-OVERFLOW` | 09 9.2 表 | 08 8.5（案） | warning・`messages.ts:175-181`、`shell.ts:441` | 文言の一部欠落・内部が案のまま（表#10） |
| `W-ACTIVE-TOP-FAILED` | 09 9.2 表 | 08 8.5（案） | warning・`messages.ts:187-193`、`shell.ts:437` | 一致（内部が案のまま: 表#10） |
| `W-PAPER-CONFLICT` | 09 9.2 表 | 08 8.6（案） | 無し | 未実装（diff-05 #16、三者監査#27） |
| `W-PAPER-INVALID` | 09 9.2 表 | 08 8.6（案） | 無し | 未実装（同上） |
| `W-C-TYPE-UNRESOLVED` | 無し | 03、4H | warning・`document-builder.ts:381-384` | 外部に無い（表#8）、文言（表#12） |
| `W-ARRAY-SIZE-UNRESOLVED` | 無し | 無し | warning・`document-builder.ts:413-418` | 両仕様に無い（表#8） |
| `W-REGION-MISMATCH` | 無し | 03、4H | warning・`document-builder.ts:676-679` | 外部に無い（表#8） |
| `W-CPP-FALLBACK` | 09 本文にコード名なし（V0.2.1 用ノート 2.1） | 08、4H、09E | warning・`messages.ts:133-156`、`import-resolution.ts:94` | diff-08 #2・#9 |
| `W-CDECL-PARSE` | 無し | 03、4H、9B | warning・`messages.ts:163-169`、`import-resolution.ts:98` | diff-08 #9 |
| `E-TECSGEN-NOT-FOUND` | 09 9.4 表 | 08、9.7 | error・`tecsgen-result-parser.ts:21,62` | コード・重大度一致（案内文は diff-08 #11） |
| `E-TECSGEN-NO-PERMISSION` | 09 9.4 表 | 08、9.7 | error・`tecsgen-result-parser.ts:23,62` | 一致 |
| `E-TECSGEN-TIMEOUT` | 09 9.4 表 | 08、9.7 | error・`tecsgen-result-parser.ts:25,62` | 一致 |
| `E-TECSGEN-OUTPUT-OVERFLOW` | 09 9.4 表 | 08、9.7 | error・`tecsgen-result-parser.ts:27,62` | 一致 |
| `E-TECSGEN-LAUNCH-FAILED` | 09 9.4 表 | 08、9.7 | error・`tecsgen-result-parser.ts:29,62` | 一致 |
| `E-TECSGEN-FAILED` | 09 9.4 表（非0終了で書式一致のエラー行が無い。終了コードと抜粋） | 08、9.7 | error・`tecsgen-result-parser.ts:31,71-73`、`tecsgen/failure-summary.ts:38-46` | 一致 |
| `W-PLUGIN-TYPE-LOAD` | 09 9.4 表 | 08、9.7 | warning・`messages.ts:224-231`、`plugin-type-provider.ts:106,120,142`ほか、`file-actions.ts:160,167,177`、`internal/processor.ts:79`、`internal/worker.ts:157` | コード一致（文言は diff-08 #10） |
| `W-PLUGIN-UNSUPPORTED` | 09 9.4 表 | 9D 9D.6 | warning・`messages.ts:212-219`、`internal/processor.ts:96` | 一致 |
| `W-TECSGEN-VERSION-OLD` | 09 9.4 表 | 08、9C | warning・`app/tecsgen-version.ts:56-64` | 一致 |
| `W-TECSGEN-VERSION-UNKNOWN` | 09 9.4 表 | 08、9C | warning・`app/tecsgen-version.ts:52-54,69-75` | コード一致（理由の文言は diff-08 #18） |
| `W-LOG-WRITE-FAILED` | 09 9.5 表 | 02 2.4、監査対応59-69 #66 | warning・`app/log-warning.ts:11-17`（`messages.ts:199-205` は未使用） | コード一致。経路の漏れ（表#1）、二重定義（表#13） |
| `E-EXPORT-FAILED` | 無し | 7F 7.10.8 | error・`app/shell.ts:584` | diff-04 #13 |
| `E-EXPORT-TOO-LARGE` | 無し | 7F 7.10.8 | error・`app/shell.ts:584` | diff-04 #13 |
| `W-ARRAY-PORT-INSERT-REJECTED` | 無し | 08 8.1・04E 4E.6（案） | 無し | diff-06 #7 |
| `W-ARRAY-PORT-DELETE-REJECTED` | 無し | 08 8.2・04F 4F.6（案） | 無し | diff-06 #7 |
| `W-RELAYOUT-FAILED` | 無し | 08 8.4・04G 4G.6（案） | 無し | diff-06 #7 |
| 発生源 `input` の診断 | 09 9.1「対象なし」 | 08「現行実装は`input`の診断を生成しない」 | 無し | 一致 |

集計: ソースが生成するコードは33種（G 2、W 23、E 8。`W-COMPOSITE-UNSUPPORTED` は定数のみで数えない）。外部仕様がコードを表・本文で定めるもの17種は、すべてソースと重大度が一致（文言の相違は表#10・#11、diff-08）。外部仕様が名前だけで挙げるもの5種（表#9）、外部仕様に無いもの9種（表#8 の5種、別担当の4種）、`G1015`・`G1016` は外部が「G-code 相当」と総称。仕様にあってソースに無いもの5種（`W-PAPER-*` 2、拒否通知の案3）。

### IPC照合表（一致分を含む全数）

方向: invoke = renderer→main（`ipcMain.handle`）、send = renderer→main（`ipcMain.on`）、push = main→renderer（`webContents.send`）。行番号は `TecscdeApi` が `src/shared/ipc-types.ts`、preload が `src/preload/index.mts`、ゲートウェイが `src/renderer/gateways/` の各ファイルです。「内部仕様」欄はチャネル名またはメソッドが現れるノートです。

| チャネル | 方向 | `TecscdeApi` | preload | main（file:line） | ゲートウェイ | 内部仕様 | 判定 |
|---|---|---|---|---|---|---|---|
| `cdl:grammar-assets` | invoke | `cdl.loadGrammarAssets` :253-255 | :36 | `ipc.ts:40-48` | 無し（`main.ts:37`・`file-actions.ts:128` が直接） | 2.4 表、9B | ゲートウェイ不経由（表#3） |
| `file:readDefinitionFile` | invoke | :257 | :39 | `ipc.ts:63` | `FileGateway` :23 | 無し（10.4 は既存API再利用） | 仕様に無い（表#16） |
| `file:planCdlFileLists` | invoke | :258 | :40 | `ipc.ts:64` | :24 | 10.4、7G | 一致 |
| `file:applyCdlFileLists` | invoke | :259 | :41 | `ipc.ts:65` | :25 | 10.4、7G | 一致 |
| `file:confirmCdlFileLists` | invoke | :260 | :42 | `ipc.ts:66-72` | :26 | 無し | 仕様に無い（表#16） |
| `file:save` | invoke | :261（`void \| SourceWriteReceipt`） | :43 | `ipc.ts:49` | :27-29 | 07。10.8 は `file:saveSource`（案） | diff-04 #25 |
| `file:chooseSavePath` | invoke | :262（省略可） | :44 | `ipc.ts:50` | :31-33 | 10.8 `chooseSavePath`（案）。チャネル名なし | diff-04 #25 |
| `file:saveAs` | invoke | :263 | :45-46 | `ipc.ts:51-53` | :35-37 | 07、2.4 | 一致 |
| `file:chooseExportPath` | invoke | :264 | :50-51 | `ipc.ts:57-58` | :47-49 | 7F | 一致 |
| `file:export` | invoke | :265 | :47 | `ipc.ts:54` | :39-41 | 07、7F、10.9 | diff-04 #12 |
| `file:exportPdf` | invoke | :266 | :48-49 | `ipc.ts:55-56` | :43-45 | 7F | 一致 |
| `file:chooseFolder` | invoke | :268 | :52 | `ipc.ts:60` | :52-54 | 2.4、7B | 一致 |
| `file:listDirectory` | invoke | :270 | :53 | `ipc.ts:61` | :57-59 | 2.4、7B | 一致 |
| `file:openPath` | invoke | :272 | :54 | `ipc.ts:62` | :62-64 | 2.4、7B | 一致 |
| `file:openPaths` | invoke | :273（`paths` 配列、省略可） | :55 | `ipc.ts:73` | :66-68 | 10.6・7I（`OpenPathsRequest`） | diff-05 #2 |
| `file:confirmDiscardChanges` | invoke | :275 | :56 | `ipc.ts:75` | :71-73 | 2.4、7B | 一致 |
| `file:saveSession` | invoke | :280-285 | :57-69 | `ipc.ts:78-89` | :76-89 | 2.4、7H、10.5 | 一致（旧引数形の併存は diff-04 の範囲） |
| `file:resolveImports` | invoke | :287-291 | :70-74 | `ipc.ts:91-95` | :92-98 | 2.4、7D、10.2 | 一致 |
| `file:parseTecsgenOptionsFile` | invoke | :293 | :75-76 | `ipc.ts:97` | :101-103 | 2.4、7C | 一致 |
| `tecsgen:generate` | invoke | :297 | :79-80 | `ipc.ts:99` | `TecsgenGateway` :11-13 | 2.4、9、10.2 | 一致 |
| `tecsgen:generatedTypes` | invoke | :298 | :81-82 | `ipc.ts:100-102` | :15-17 | 2.4、9（10.2 の I 行に無い） | 一致（10.2 の記載漏れ: 表#16） |
| `tecsgen:preprocess` | invoke | :299 | :83-84 | `ipc.ts:103-109` | :19-21 | 2.4、9、10.2 | 一致（9 本文の古さは diff-08 #17） |
| `tecsgen:version` | invoke | :300 | :85 | `ipc.ts:110` | :23-25 | 2.4、9C、10.4 | 一致 |
| `tecsgen:checkPath` | invoke | :301 | :86 | `ipc.ts:111` | :7 | 9D、10.4 | 一致 |
| `tecsgen:commandLine` | invoke | :302 | :87 | `ipc.ts:112-118` | :8-10 | 無し（09D はコピーの規則のみ） | 仕様にチャネル無し（表#16） |
| `clipboard:writeText` | invoke | :305 | :92 | `ipc.ts:147` | `ClipboardGateway` :6-8 | 2.4、04、10.2 | 一致（コメントの誤り: 表#17） |
| `clipboard:readText` | invoke | :306 | :93 | `ipc.ts:148` | :10-12 | 2.4、04、10.2 | 一致 |
| `settings:get` | invoke | :317 | :96 | `ipc.ts:139-141` | `SettingsGateway` :7-9 | 2.4、03 | 一致 |
| `settings:getToolSettings` | invoke | :318 | :97 | `ipc.ts:119` | :11（`file-actions.ts:105` は直接） | 9D、10.4 | 一致（直接呼び出し: 表#3） |
| `settings:updateToolSettings` | invoke | :319 | :98 | `ipc.ts:120` | :12-14 | 9D、10.4 | 一致 |
| `settings:chooseTecsgenPath` | invoke | :320 | :99 | `ipc.ts:132-136` | :15 | 9D、10.4 | 一致 |
| `settings:chooseCppPath` | invoke | :321 | :100 | `ipc.ts:137` | :16 | 09E | 一致 |
| `settings:getAppInformation` | invoke | :322 | :101 | `ipc.ts:121` | :17 | 無し（2.5 は `versions` と define） | 仕様に無い（表#16。版情報の経路は diff-01 #8） |
| `settings:getCdlFilesRoot` | invoke | :323 | :102 | `ipc.ts:122` | :18 | 無し | diff-01 #6 |
| `settings:setCdlFilesRoot` | invoke | :324 | :103 | `ipc.ts:123-126` | :19 | 無し | diff-01 #6 |
| `settings:chooseCdlFilesRoot` | invoke | :325 | :104 | `ipc.ts:127-131` | :20 | 無し | diff-01 #6 |
| `log:append` | invoke | `log.append` :331-333（`LogAppendResult`） | :121 | `ipc.ts:142` | `LogGateway` :7-9（`file-actions.ts:185` は直接） | 2.4（名前空間・`newFailure`。チャネル名なし） | 型一致。結果を捨てる経路あり（表#1・#3） |
| `window:setDirty` | send | `window.setDirty` :310 | :107 | `index.ts:119` | `WindowGateway` :5-7 | 2.4、07、7J、10.8 | 一致 |
| `window:closeState` | send | `window.replyCloseState` :313 | :118 | `close-state-bridge.ts:58`（`ipc.on`） | 無し（`main.ts:50,54` が直接） | 7J 7J.9、10.8 | ゲートウェイ不経由（表#3） |
| `window:requestCloseState` | push | `window.onRequestCloseState` :311 | :108-112 | `close-state-bridge.ts:59` | 無し（`main.ts:46`） | 7J 7J.9、10.8 | 同上 |
| `window:cancelCloseState` | push | `window.onCancelCloseState` :312 | :113-117 | `close-state-bridge.ts:69` | 無し（`main.ts:57`） | 7J 7J.9、10.8 | 同上 |
| `app:bootstrap` | push | `onBootstrap` :339 | :124-126 | `index.ts:166,169` | 無し（`main.ts:86`） | 2.4、07、7H、7I、10.5 | 一致（ゲートウェイ不経由: 表#3） |
| `app:fileBrowserRoot` | push | `onRestoreFileBrowserRoot` :344 | :128-130 | `index.ts:182` | `FileGateway` :106-108 | 2.4、7B | 一致 |
| （チャネル無し）`versions` | 値 | :252 | :29-34 | — | 無し（`main.ts:72`） | 2.5 | 一致（2.4 表に無いのは diff-01 #7） |
| `file:readTextForView` | — | 無し | 無し | 無し | 無し | 8B 8B.3、10.7（案） | 未実装（表#7、三者監査#50） |
| `file:saveSource` | — | 無し | 無し | 無し | 無し | 7J、10.8（案） | diff-04 #25 |
| `app:openRequest` | — | 無し | 無し | 無し | 無し | 7K、10.10（案） | diff-05 #1、diff-01 #22 |

集計: 実装のチャネルは43（invoke 37、send 2、push 4）。`TecscdeApi`・preload・main の三者は、全チャネルで名前と引数が一致しました。チャネル名またはメソッドが内部仕様のどこにも無いものは8（`file:readDefinitionFile`・`file:confirmCdlFileLists`・`tecsgen:commandLine`・`settings:getAppInformation`・`settings:*CdlFilesRoot` の3つ・`log:append` のチャネル名）。ゲートウェイを通らない使用は7チャネルと `versions`。仕様にあって実装に無いものは3で、いずれも「案」です。

### 未確認（相違として断定しないもの）

1. **tecsgen の行にコードが無いときのコード欄**: `src/renderer/diagnostics/tecsgen-result-parser.ts:85,95` は、本文が `G1015 …` のようにコードで始まらない行のコードを `ERROR`／`WARNING` にし、パネル・ログに `[ERROR] …` と出ます。外部 9.1・9.5 規定6 はこの場合のコード欄を定めていません。実際の tecsgen の出力にコードの無い行があるかは確かめていません。
2. **消えて再び現れた診断の再記録**: `src/renderer/app/diagnostics-logger.ts:35-39` は直前の一覧との差分だけを書くため、いったん消えた診断が再び現れると同じ行がもう一度記録されます。外部 9.5 規定8「同じ診断を繰り返し書かない」の「新しく現れた」に当たるかの解釈が定まっていません（内部の監査対応59-69 #67 は「診断の消滅と再出現」を試験項目に挙げますが、期待値を書いていません）。
3. **ログ先頭行の日時の基準**: `src/main/log-service.ts:104` は先頭行に UTC（`toISOString()`、末尾 `Z`）を、ファイル名（`:21-25`）はローカル時刻を使います。外部 9.5 規定3・5 はそれぞれ「ローカル時刻」「ISO 8601 の日時」で矛盾はしませんが、同じ起動時刻が2通りに表されます。
4. **`LOCALAPPDATA` が無い Windows**: `src/main/app-settings.ts:121-126` は環境変数 `LOCALAPPDATA` が無いと `userData`（Roaming）へ置きます。外部 9.5 規定2 は Windows を Local AppData に固定しますが、この場合の扱いを定めていません。通常の環境では起きないため、相違とはしません。
5. **外部 10.4 #3（意味論的検証は範囲外）と型・シグニチャの解決警告**: `W-PORT-SIGNATURE-UNRESOLVED`・`W-C-TYPE-UNRESOLVED`・`W-ARRAY-SIZE-UNRESOLVED` は、シグニチャ・C 型・定数式を解決しようとした結果の警告で、意味論的検証に近いものです。外部 9.2 は `W-PORT-SIGNATURE-UNRESOLVED` を採用しているため、10.4 #3 の「範囲外」がどこまでを指すかは判断を保留します。
6. **診断パネルの件数表示の文言**: `src/renderer/app/diagnostics-panel.ts:51` は「⚠ N エラー / M 警告」です。親 9.3.2 の「エラー N件・警告 M件」が例示か書式の規定かを読み取れず、三者監査#52 の範囲（diff-02 #19）でもあるため挙げません。
7. **外部第10章のその他の項目**: 10.1（文字コード・`__location_information__`・`base_dir`）、10.2（編集可否）、10.3（`require`・ポート）、10.4 #1（複合セルタイプ）は、それぞれ diff-05・diff-03・diff-06・diff-08 の担当範囲と重なるため、本表では照合していません。10.1 #6（版の確認、V1.3.1.0 以降）は `src/renderer/app/tecsgen-version.ts:12,51-66` で一致を確認しました。

### 過去の監査で指摘され、V0.2.5 で解消を確認した項目（表に含めない）

計8件: 三者監査 #63（ログ先頭行の版。`src/main/log-service.ts:104`、`src/main/index.ts:49`）、#64（固定の `logs/`、cwd を使わない。`src/main/app-settings.ts:121-131`、`src/main/index.ts:47-49`）、#65（新しい30個を残す。`src/main/log-service.ts:11,41-60`、`src/main/index.ts:48`）、#66（画面への一度限りの警告・ログへ書かない。`src/main/log-service.ts:110-116`、`src/renderer/app/log-warning.ts:23-33`、`src/renderer/app/diagnostics-logger.ts:22-25`。ただし通らない経路が残る〔表#1〕。再通知は diff-01 #17）、#67（区切り行だけのログを作らない。`diagnostics-logger.ts:29-46`。ただし取り込み方式の行は別〔表#2〕）、#68（1診断1物理行。`src/renderer/diagnostics/format.ts:9-28`）、差分一覧 #3（tecsgen の起動失敗の種類別診断。`tecsgen-result-parser.ts:19-75`）、差分一覧 #7（起動時の版確認と警告。`src/renderer/app/tecsgen-version.ts`、`src/renderer/main.ts:81-83`）。

### 集計

- 表の件数: 17件
- 種別（重複計上）: A 5件（#2・#8・#9・#11・#14）、B 9件（#1・#2・#4・#5・#7・#8・#10・#11・#12）、C 13件（#1・#2・#3・#5・#6・#7・#8・#9・#10・#13・#15・#16・#17）
- 状態: 新規 16件、既知・未解消 1件（#7＝三者監査#50）、仕様が未実装・延期と明記 0件


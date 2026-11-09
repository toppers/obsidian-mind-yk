---
date: 2026-11-09
description: "三者監査9〜18の内部仕様契約補足。既決要件と現行コードの差を区別する。"
project: TECS
quarter: Q4-2026
status: active
tags: [work-note, tecs, tecscde, spec]
---

# TECSCDE-DT-EL内部仕様 - 監査対応 09-18 読み込みと設定

[[TECSCDE-DT-EL内部仕様]]の補足。[[TECSCDE-DT外部仕様 - 監査対応 09-18 読み込みと設定]]と対になる。

2026-11-09の確定契約・実装境界を記す。関連する旧時点の実装記録を、今回のコードの適合確認として扱わない。既存の決定と未決事項（TBC）を維持し、未決を完成済みにしない。仕様を修正してもソース修正が必要な項目は未実装のままである。

## 監査9

**ファイル関連付けの複数入力・既起動インスタンスへの配送・受付キューが未実装**

[[TECSCDE-DT外部仕様 - 監査対応 09-18 読み込みと設定#監査9]]に対応する。

7KのLaunchOpenRequestにrequestId・入力元・パス列・送信元cwdを保持し、送信元で確定した値をsingle-instance配送へ渡します。macOSの配列通知アダプタとWindows/Linuxの関連付けモードを分離し、収集中・確定待機・処理終了を管理します。最初はbootstrap、以後はopenRequestとして7Iへ接続します。rendererの要求guardはキューから読み込み開始時に発行し、受信だけで先行操作を失効させません。現行pendingOpenPathの単数上書きはこの契約へ未対応です。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/main/index.ts:44` — `let pendingOpenPath: string | null = null;`
- `src/main/index.ts:55` — `pendingOpenPath = path;`
- `src/main/index.ts:121` — `win.webContents.once("did-finish-load", async () => {`

**受入条件**: A B Aの主A/順A B、独立要求順序、重複配送抑止／既起動配送、初期受付未確定中fallback抑止、明示入力失敗／OSごとの実機確認はtests/verificationへ。設定登録だけで成功扱いにしない

参照: [[TECSCDE-DT-EL内部仕様 - 07K 関連付け入力の収集と一括オープン]]、[[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約]]、[[TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧]]。

## 監査10

**起動・ブラウザ等の拡張子判定に、大文字小文字を区別する処理が残る**

[[TECSCDE-DT外部仕様 - 監査対応 09-18 読み込みと設定#監査10]]に対応する。

Nodeに依存しない共有の形式判定関数へ三拡張子の識別を集約し、mainのargv選択・起動分岐、FileService.isBrowsable、rendererのファイルクリック分岐を同じ判定へ接続します。種別判定と正規化済みパスによる同一性判定を混同せず、表示・I/O用パスは受け取った表記を保持します。OPTIONS_EXTENSIONの大小文字区別とendsWith分岐は現行HEADに残っており、確定した外部規則が未反映です。7Kの配送経路も同じ形式判定を利用します。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/main/file-service.ts:21` — `const OPTIONS_EXTENSION = /\.tecsgen-opts$/;`
- `src/main/index.ts:48` — `(a) => a.endsWith(".cde") || a.endsWith(".cdl") || a.endsWith(".tecsgen-opts"),`
- `src/main/index.ts:125` — `if (pendingOpenPath.endsWith(".tecsgen-opts")) {`

**受入条件**: 大文字/混在文字の三拡張子を各入口で同一識別／日本語/空白入りパスを改変しない／CLIは依然として対象の先頭1件

参照: [[TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合]]、[[TECSCDE-DT-EL内部仕様 - 07K 関連付け入力の収集と一括オープン]]。

## 監査11

**-S配下の_CDL_FILES.txtによる探索が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 09-18 読み込みと設定#監査11]]に対応する。

ImportResolutionOptionsへsystemDirsを追加し、resolveImportClosure・resolveAllImports・resolveAddedReferenceからFileService.resolveImportsへ渡します。mainのCdlFileLists.lookupは候補のdirname単位で一覧をキャッシュし、listed/unlisted/probeを返します。候補順を維持してlistedのみ一覧のパス、probeは通常読取、unlistedは除外します。Windowsの大小文字、区切り、先頭./、空行等は既決書式に従います。現行型とresolveOneには一覧判定がなく、07Eの実装記録をこのHEADの完了証明にはしません。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/main/file-service.ts:173` — `return Promise.all(requests.map((request) => this.resolveOne(request, searchDirs, options.importPath…`
- `src/renderer/app/import-resolution.ts:102` — `const options: ImportResolutionOptions = { baseDir: toolInfo.baseDir, importPaths: toolInfo.importPa…`
- `src/shared/ipc-types.ts:96` — `export interface ImportResolutionOptions {`

**受入条件**: 自身/子/孫の一覧、親一覧不使用、非掲載でも他探索先へ進む／一覧読取不能/掲載先不在/import_C/-S外／同一解決内キャッシュと次回open時再取得

参照: [[TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡]]、[[TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合]]、[[TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧]]。

## 監査12

**絶対パスの-I・-Sをjoinで連結し、探索先を壊す**

[[TECSCDE-DT外部仕様 - 監査対応 09-18 読み込みと設定#監査12]]に対応する。

FileService.resolveOneの候補構築はjoin(dir,p,specifier)の無条件連結をやめ、探索先pの絶対/相対を確定してからspecifierを接続します。07EのcandidatesForでresolve(dir,p)を使う契約と、opts親基点の追加列を分離し、通常tool_info側の探索順は保持します。候補の正規化は同一性検査にも利用し、I/Oは候補順で試します。07Eは修正済みと記録していますが、現行HEADの185行は旧joinのままであり、設計契約と別checkoutの履歴を区別する注記が必要です。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/main/file-service.ts:185` — `importPaths.map((p) => (p === "." ? join(dir, request.specifier) : join(dir, p, request.specifier)))…`

**受入条件**: Windows別ドライブ絶対-I/-S、UNCと相対探索先／optsとCDLの親が異なるケース、cwd変更／絶対パスを前のdirへ連結しない候補配列検査

参照: [[TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡]]、[[TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合]]。

## 監査13

**basenameだけの既読キャッシュが、別ディレクトリの同名ファイルを誤解決する**

[[TECSCDE-DT外部仕様 - 監査対応 09-18 読み込みと設定#監査13]]に対応する。

resolveImportClosureのknownByBaseによる成功判定を廃止し、mainが確定したcanonicalPathを共通のパス正規化キーで照合します。manualの絶対パスは直接照合できますが、相対importのspecifierは検索コンテキストなしに既読キーへ変換しません。探索済み結果のキャッシュは少なくとも解決元と探索条件を区別し、systemDirs/一覧判定を迂回しない構造にします。同じcanonicalPathなら既存のソースを再利用し、別ディレクトリの同名ソースは独立して保持します。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/import-resolution.ts:119` — `knownByBase.set(baseName(r.path), r);`
- `src/renderer/app/import-resolution.ts:129` — `const found =`
- `src/renderer/app/import-resolution.ts:132` — `knownByBase.get(baseName(req.specifier));`

**受入条件**: 既読A/xに対するimport B/x、manual B/x／同名別dirの並存、同じ正規化パスだけ重複抑止／一覧非掲載の候補がbasename経由で復活しない

参照: [[TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡]]、[[TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合]]、[[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約]]。

## 監査14

**設定の読み込み・部分更新・書き込みを直列化せず、並行更新を失う可能性がある**

[[TECSCDE-DT外部仕様 - 監査対応 09-18 読み込みと設定#監査14]]に対応する。

mainのsaveAppSettingsを唯一の更新入口とし、enqueueSettingsUpdateで読込・正規化・patchマージ・mkdir・write全体を一つのキュー項目にします。書込直前だけの直列化では同じ旧JSONからの更新消失を防げません。folder/session/tool設定の各APIはこの入口を共用し、一件のreject後も後続処理を進めます。未知項目を保持する単独mergeは現コードにもありますが、同時更新の排他は未実装です。失敗結果は元の要求へ返し、古い応答で新しい保存状態表示を戻しません。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/main/app-settings.ts:69` — `const current = await loadAppSettings();`
- `src/main/app-settings.ts:72` — `await fs.writeFile(join(dir, "settings.json"), JSON.stringify({ ...current, ...patch }));`

**受入条件**: folderとsession同時更新、同項目連続更新／未知項目保持と先行書込失敗後の継続／読込順も含めた遅延制御でlost updateを再現防止

参照: [[TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計]]、[[TECSCDE-DT-EL内部仕様 - 07H セッション保存と復元]]、[[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理]]。

## 監査15

**設定・セッションの実行時型検証と正規化がない**

[[TECSCDE-DT外部仕様 - 監査対応 09-18 読み込みと設定#監査15]]に対応する。

loadAppSettingsはJSON.parseの戻り値をunknownとしてnormalizeAppSettingsへ渡します。通常object検査、fileBrowserRoot等の既知型検査、SessionSnapshotの配列要素型・主/参照集合とsourceOrder整合を段階検査します。明示された不正順序は無効であり旧順序へ補正しません。allowEditSystemDefinedは真偽値trueだけ有効とします。正規化だけでファイルを書き直さず、read-merge-write時に未知項目を保存します。現コードのas AppSettingsとmainのproperty参照だけではこの契約を満たしません。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/main/app-settings.ts:51` — `return JSON.parse(raw) as AppSettings;`
- `src/main/index.ts:157` — `const lastSession = settings.lastSession;`

**受入条件**: null/配列/数値JSON、不正sessionだが有効folderあり／旧主省略nullと旧順序省略、有効空session／文字列true/不正配列要素/指定済order不一致

参照: [[TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計]]、[[TECSCDE-DT-EL内部仕様 - 07H セッション保存と復元]]、[[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約]]。

## 監査16

**「消去」で保持すべき参照ソースの本文・未保存編集をモデルから落とす**

[[TECSCDE-DT外部仕様 - 監査対応 09-18 読み込みと設定#監査16]]に対応する。

newDocumentはTecscdeDocument.emptyを全体へloadDocumentする方法をやめ、SourceId単位で主に属する状態だけを除き、参照の現在モデル・元ソース・保存baselineを維持して空主を組み立てます。主削除で成立しなくなる結合は所属と端点の整合を既存規則で再検査し、参照本文を再読して編集を上書きしません。新主には空baselineを登録し、DirtyTrackerは保持ソースごとの差分を集約します。sourceOrderは保持参照の順を使い、7Iのguardで一回適用し固定sessionを保存します。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/file-actions.ts:163` — `const referenceFilePaths = store.getReferenceFilePaths();`
- `src/renderer/app/file-actions.ts:165` — `const document = TecscdeDocument.empty();`
- `src/renderer/app/file-actions.ts:166` — `store.loadDocument(document, null, [], referenceFilePaths, referenceSources, []);`

**受入条件**: 参照ソース編集中の消去で本文/モデル/baseline/dirty保持／取消は全状態不変、参照なしは空clean／消去後session再起動はディスク版参照を復元し未保存本文は再現しない

参照: [[TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合]]、[[TECSCDE-DT-EL内部仕様 - 07J 保存チェックポイントと未保存判定]]、[[TECSCDE-DT-EL内部仕様 - 07H セッション保存と復元]]。

## 監査17

**主ファイル未確定時のCtrl＋手動追加を無通知で拒否する**

[[TECSCDE-DT外部仕様 - 監査対応 09-18 読み込みと設定#監査17]]に対応する。

addAsReferenceのif(!editablePath)returnを除き、nullable primaryを持つコンテキストでresolveAddedReferenceへ接続します。manualの絶対パスを最初の入力にし、その親と対象tool_infoから再帰importを解決し、存在しない主パスのdirnameを推測しません。現在の未保存主モデル・既存参照・baselineを保持して新規通常ソースだけを追加し、sourceOrderと参照集合を一括更新します。7I.7のguardを最初のawait前に固定し、失敗/失効時は旧状態を保ちます。成功後だけ固定sessionを保存します。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/file-actions.ts:183` — `if (!editablePath) return; // 消去直後など編集対象未確定では参照追加の起点が無い`

**受入条件**: 新規空図/消去直後のCtrl追加と再帰import／未保存主を保持しprimary nullのまま、重複追加no-op／追加失敗/遅延競合で図とsession不変

参照: [[TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合]]、[[TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合]]、[[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約]]。

## 監査18

**CDLファイル一覧生成のサービス・IPC・操作入口が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 09-18 読み込みと設定#監査18]]に対応する。

7GのplanCdlFileListsとapplyCdlFileListsをshared/main/preload/FileGatewayで接続します。mainはplanIdと各既存内容のhashを保持し、確認後のapply前に全対象の前提を再検査し、変化していれば書込なしでchangedを返します。子一覧を先に原子的置換し、全件成功後にroot一覧を作ります。途中失敗はwrittenPathsを返して一括rollbackを保証せず、成功件数とskippedSameを区別します。生成は履歴/dirtyを変更しません。10.4の旧create単段APIは7Gの二段階契約へ参照統一が必要です。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/main/file-service.ts:37` — `export class FileService {`
- `src/main/ipc.ts:33` — `ipcMain.handle("file:export", (_e, path: string, data: string) => fileService.exportFile(path, data)…`
- `src/shared/ipc-types.ts:134` — `readonly file: {`

**受入条件**: new/same/differs、取消、計画後の外部変更／深い階層/リンク/大文字CDL/日本語パス/順序とLF／子失敗/ルート失敗/0件、文書dirty不変

参照: [[TECSCDE-DT-EL内部仕様 - 07G V0.2.0CDLファイル一覧生成]]、[[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、[[TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧]]。

## Related

- [[TECSCDE-DT-EL内部仕様]]
- [[TECSCDE-DT外部仕様 - 監査対応 09-18 読み込みと設定]]

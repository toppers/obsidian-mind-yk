---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様 第7章（ファイルI/O設計）— mainのFileService（dialog+fs、アトミック書き込み）とrendererのFileGatewayによるElectron固有実装。7B〜7Eは別ノート。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - architecture
---

> [!info] V0.2.0差分設計（2026-11-06）
> V0.2.0のCDLファイル一覧生成は[[TECSCDE-DT-EL内部仕様 - 07G V0.2.0CDLファイル一覧生成]]、定義ファイルの読取専用表示は[[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成#2B.3 プロパティと定義ファイルウィンドウ|2B.3]]で追加します。差分章は実装前の内部設計です。


Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 7 of 11. Electron固有化の中心章の1つ。

## 7. ファイルI/O設計

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様第5章]]の規定（真の上書き保存、ファイル関連付け、複数ファイル対応）を実現する。[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 07 ファイルI-O設計|TECSCDE-TS内部仕様第7章]]が提案した`FileIOStrategy`インタフェース（Electron/Tauri両対応のためのStrategyパターン）は、**本書ではTauriとの両立を考慮する必要がなくなったため廃止し**、Electronの`fs`・`dialog`を直接使う設計に置き換える。

### 7.1 `FileService`クラス（mainプロセス）

> [!note] `openDialog()`の撤回（2026-09-21）
> 複数ファイルを同時選択するOSネイティブの「開く」ダイアログは、ファイルブラウザと役割が重複するため撤回した。**コマンドライン引数は7.4節の先頭検索に従い、最初の対象ファイル1件だけを読み込む**（2026-11-07、監査#5。旧要約の「最後を主ファイル」を訂正）。ファイル関連付けで複数ファイルが渡る場合の従来の規定と、`.tecsgen-opts`内で列挙されたCDLの最後を主ファイルとする規定は、コマンドライン引数の1件選択とは区別する。システム定義CDL（`-S`配下、第7C章7.7.4節）を除く、ユーザ定義CDL由来のセルはどのファイルでも編集可能とする（DT外部仕様第5章）。

```ts
// main/file-service.ts
class FileService {
  constructor(private readonly window: BrowserWindow) {}

  async save(path: string, content: string): Promise<void> {
    await this.writeAtomic(path, content); // 7.2節参照
  }

  async saveAsDialog(suggestedName: string, content: string): Promise<string | null> {
    const result = await dialog.showSaveDialog(this.window, {
      defaultPath: suggestedName,
      filters: [{ name: 'CDE files', extensions: ['cde'] }],
    });
    if (result.canceled || !result.filePath) return null;
    await this.writeAtomic(result.filePath, content);
    return result.filePath;
  }

  async exportFile(path: string, data: ExportData): Promise<void> {
    const content = typeof data === 'string' ? data : Buffer.from(data);
    await this.writeAtomic(path, content); // Bufferへの変換はmain内だけ
  }

  private async writeAtomic(path: string, content: string | Buffer): Promise<void> {
    const tmpPath = `${path}.tmp-${process.pid}`;
    await fs.promises.writeFile(tmpPath, content);
    await fs.promises.rename(tmpPath, path); // OSのファイルシステムレベルでアトミック
  }
}
```

`writeAtomic`は[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様5.4節]]が要件とする「書き込み失敗時に既存データを失わない」を、**一時ファイル書き込み＋リネーム**で実現する——`fs.promises.rename`は同一ファイルシステム内であればOSレベルでアトミックであり、書き込み途中でプロセスが異常終了しても元のファイルは無傷のまま残る。

### 7.2 IPCハンドラの登録（main）

```ts
// main/ipc.ts
const fileService = new FileService(mainWindow);

ipcMain.handle('file:save', (_e, path: string, content: string) => fileService.save(path, content));
ipcMain.handle('file:saveAs', (_e, content: string, suggestedName: string) => fileService.saveAsDialog(suggestedName, content));
ipcMain.handle('file:export', (_e, path: string, data: ExportData) => fileService.exportFile(path, data));
```

### 7.3 `FileGateway`クラス（renderer）

第2章2.4節で示したとおり、preloadが`window.tecscde.file`として公開するAPIを、rendererの`FileGateway`が薄くラップする。

```ts
// renderer/gateways/file-gateway.ts（ExportDataはsharedから型だけをimport）
class FileGateway {
  save(path: string, content: string): Promise<void> { return window.tecscde.file.save(path, content); }
  saveAs(content: string, suggestedName: string): Promise<string | null> { return window.tecscde.file.saveAs(content, suggestedName); }
  export(path: string, data: ExportData): Promise<void> { return window.tecscde.file.export(path, data); }
}
```

`DirtyTracker`は[[TECSCDE-DT-EL内部仕様 - 07J 保存チェックポイントと未保存判定|7J]]のソース別保存状態と一意な履歴位置の契約へ変更する（2026-11-08、監査#21）。TS内部仕様第7章の`History.past.length`だけによる判定は継承しない。保存成功した状態だけをbaselineへ採用し、Undo後の分岐、保存中新編集、一部失敗を現在の保存対象状態との比較で判定する。UIとmainの終了確認も同じ結果を使う。三者監査#3で確認した現行コード`5cf2d85`は履歴長判定と完了時の`markSaved()`を使っており、この確定契約は未反映。保存チケット・ソース別baseline・保存先別キューの責務と対応状況は7J.0・7J.4・7J.7を正とする。

**exportの型境界（2026-11-08、監査#28）**: `ExportData = string | Uint8Array`を`shared/ipc-types.ts`で定義し、renderer・preload・mainのIPC受信と`FileService.exportFile`で共用する。mainは値を検査してから受け取り、バイト列を`Buffer.from(data)`へ変換し、内部の`writeAtomic(string | Buffer)`へ渡す。preloadは変換せず中継し、rendererからNodeのBufferを要求しない。詳細と確認条件は[[TECSCDE-DT-EL内部仕様 - 07F エクスポート設計（たたき台）|7F.7.10.7]]を参照。実装適合は未確認。

### 7.4 起動時のファイルオープン経路（コマンドライン引数・ファイル関連付け）

**2026-11-08、監査#22で入口を統一**: 詳細な受信・コード例は[[TECSCDE-DT-EL内部仕様 - 07K 関連付け入力の収集と一括オープン|7K]]を正とする。CLIは先頭の対象1件、関連付けは境界付きの複数パス列を受け、単数の`pendingOpenPath`に複数イベントを上書きする旧例は使わない。

```ts
// mainの入口。補助関数とOSアダプタは7Kで定義する契約案。
const isStartupFile = (path: string): boolean => /\.(?:cde|cdl|tecsgen-opts)$/i.test(path);
const invocation = parseLaunchOpenRequest(applicationArgs, process.cwd());
// kind==='cli'だけ対象の最初の1件をfindで選ぶ。
// kind==='association'は受信順のパス列と要求境界を保持する。
```

要求はrenderer準備前にもキューで保持する。通常CDLの関連付けバッチは最後を主ファイルとし、役割・sourceOrderを[[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約|7I]]へ明示して一括読み込みする。CLI等の単独optsはファイル内の列挙を7Iへ渡す。初期受付が確定するまでlastSession／samplesへ先行fallbackせず、初回だけ`app:bootstrap`、既起動時は`app:openRequest`を使う。形式識別は大小文字非区別とし、元のパス表記は変更しない（監査#31の契約を維持）。

macOSはOSの配列通知を受ける追加アダプタを設計し、標準open-fileにバッチ終端があるとは仮定しない。Windows/Linuxの起動モード識別・既起動instanceへの転送も7Kに従う。新入口の実装適合は未確認。

### 7.5 インポート参照先の解決

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様5.1節]]・[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05A 開く（読み込み）|5.3節]]および同第8章8.1節が規定する参照先の自動追跡（`FileService.resolveImports()`）の詳細設計は、[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|第7D章（具体アルゴリズム・tecsgen本体との対応検証）]]・[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章（renderer側オーケストレーション・import_C境界・統合ポイント）]]に分離した（2026-09-22、25KB閾値。旧稿にあった「tecsgen本体の探索順序とは異なる（inferred・未検証）」という警告は、`Importable#find_file`の実ソース検証により第7D章7.5.3節で対応関係を確定し解消済み）。

### 7.6 ファイルブラウザ（サイドパネル）

`FileService`拡張・IPC・`FileBrowserView`・ルートフォルダの永続化（Local AppData）と起動時自動復元を含む全体設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計|第7B章（ファイルブラウザ設計）]]に分離（2026-09-22、25KB閾値）。

### 7.7 読み込み経路の統合

前回セッションの復元・ファイルブラウザからの追加読み込み・消去ボタン・tecsgenオプション形式ファイルの一括読み込み・import自動追跡との統一（第11章11.2節#7〜#11）の設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|第7C章（読み込み経路の統合）]]にまとめた。

### 7.8 入力の文字コードと非UTF-8入力（2026-10-21、ソースの確認に基づく。同日、外部仕様を実装に合わせて改訂）

**外部仕様の規定**（[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|DT外部仕様5.1節]]、2026-10-21改訂。以前は「UTF-8に限る」としていた）: 読み込みはUTF-8を優先し、できなければShift_JIS、EUC-JPの順で復号する。復号できた符号は通知しない。三つとも失敗した通常CDLは読み込めず、参照先なら`W-UNRESOLVED-REF-FILE`とする。ただし`.tecsgen-opts`は、下表と7.7.4節のとおりUTF-8で読み直して解析を続ける（2026-11-07、監査#7。外部仕様の要約にも経路別の例外を明記）。保存・書き出しは常にUTF-8。判定は復号の成否なので誤判定による文字化けがありうる。旧世代の`__location_information__`形式は、エラーにせず読み込んで無視する（外部仕様5.1節、2026-10-22改訂）。

**実装**（`main/file-service.ts`の`decodeBuffer`、`main/tecsgen-runner.ts`の`generatedCdlSources`の読解。テストは読んでいない）は、この規定と一致する: ファイルのバイト列を、`TextDecoder`の`fatal`指定で **UTF-8 → Shift_JIS → EUC-JP** の順に試し、最初に成功したものを文字列にする。

| 経路 | 実装 | 非UTF-8（レガシー符号）のとき |
|---|---|---|
| ファイルを開く（起動引数、ファイルブラウザ、前回セッション、サンプル）: `readPaths` | `decodeBuffer` | 受理して読み込む。診断は出ない |
| `import`の自動追跡: `resolveImports`（7.5節） | `decodeBuffer` | 同上。三つとも失敗したときだけ`error: "not-utf8"`を返す |
| `.tecsgen-opts`の解析（7.7.4節） | `decodeBuffer`、失敗なら`utf-8`で読み直す | 受理して読む |
| Plugin生成CDLの取り込み（9.7節） | `TextDecoder`でUTF-8→Shift_JIS→EUC-JP | 同上。いずれも失敗すれば例外 |
| 保存: `FileService.save` | 文字列を`fs.writeFile`（一時ファイル＋リネーム、7.1節） | 常にUTF-8で書く（レガシー符号の保存手段は無い） |
| tecsgenの起動（9章） | `TecsgenCommandBuilder`が先頭に`-k utf8`を付ける（11.2節#6） | 自動保存（9.5節）でUTF-8になってから渡る |

- **三つとも失敗した場合**: `readPaths`の`decodeBuffer`は最後の`euc-jp`の例外をそのまま投げる。`resolveImports`は例外を握って`error: "not-utf8"`を返し、rendererは参照先が読み込めなかったものとして`W-UNRESOLVED-REF-FILE`に変換する（`not-utf8`と`not-found`は区別されない。7.5.6節）。
- **`__location_information__`形式の読み飛ばし**（2026-10-22）: 外部仕様に合わせ、旧世代のtecscde（Ruby版）が書く`__location_information__ { … }`ブロック（`__cell__`・`__join__`・`HBar`・`VBar`を含む）を、エラーにせず読み込んで無視する。実装は`ToolInfoValidator.extractBlocks`（`cdl/tool-info.ts`）の末尾の`blankLocationInformation`で、`__tool_info__`と同じく、キーワードから対応する閉じ波括弧までを空白（改行は残す）に置き換えてからtree-sitterへ渡す。行番号と文字位置は変わらない。ブロックの中身は文字列を含まないので、波括弧の対応だけで終端を決める。閉じていない場合は何もしない（その場合は通常の構文エラーになる）。ローダ（`CdlDocumentLoader`）とシリアライザの再解析検証は同じ`extractBlocks`を通るので、読み込みと保存のどちらでも同じ扱いになる。シリアライザは原文のテンプレートを編集するため、保存してもブロックは元の位置にそのまま残る。ブロックの内容（座標・ポート位置・バー位置）は使わない——`__tool_info__("tecscde")`が優先される現行の仕様と矛盾しないためで、旧形式の位置を復元する機能は無い。テストは`tests/renderer/location-information.test.ts`。

> [!note] 残る論点（要判断）
> 1. **保存時の無通知の符号変換**: レガシー符号のファイルを開いて保存すると、そのファイルがUTF-8に書き換わる。外部仕様はこれを仕様として認めた（通知なし）。他のツール（tecsgenの`-k`指定がレガシー符号前提のビルド等）が元の符号を前提にしていると壊れうる点は、既知の限界として残る。通知を足すかは未決。
> 2. **判定の曖昧さ**: Shift_JISとEUC-JPは、`fatal`指定でも短いバイト列やASCII混じりでは誤って成功しうる。符号を利用者が指定する手段は無い。
> 3. **7.5.2節の`not-utf8`の設計**: 当初の`fs.readFile(path, "utf-8")`は不正バイトを置換文字にするだけで例外にならない（7D）。実装は`TextDecoder`の`fatal`で検出する形に変わっており、`not-utf8`になるのは三つの符号のいずれでも復号できないファイルに限られる。
> 4. ~~**`__location_information__`形式**: 検出してファイル単位のエラーにする処理が無い~~ → **解決（2026-10-22）**: 外部仕様を「エラーにせず読み込んで無視する」に改め、実装を揃えた（上の「読み飛ばし」）。

### 7.9 終了確認と保存待機（2026-11-09、三者監査#4）

[[TECSCDE-DT外部仕様 - 05 ファイル操作|外部5.7]]に従い、通常closeを同期中断し、rendererの保存結果反映後の最新dirtyと、mainの受理済み書込完了を確認してから閉じる。**確定契約は[[TECSCDE-DT-EL内部仕様 - 07J 保存チェックポイントと未保存判定|7J.9]]を正とする**。shared／preload／gateway／mainの対応は第10章10.8に揃える。

- `window:setDirty`は通常通知として残すが、falseというだけでcloseを通さない。queryId付き`window:requestCloseState`／`window:closeState`で最新状態を照合する。
- 編集と新規要求の適用を止めても、開始済み保存の完了・checkpoint反映は進める。rendererのタイムアウトでmainの保存待機を打ち切らない。
- dirtyまたは状態不明は「保存せずに終了」「キャンセル」で確認し、キャンセルを既定にする。`window:cancelCloseState`で通常操作へ戻し、待機中の保存成功は維持する。
- 閉じる許可は1回の終了トランザクションに限定し、古い回答・別ウィンドウ・連続closeで誤許可や二重確認をしない。`beforeunload`は使わず、止められないOS終了は対象外。

**従来版の記録（2026-10-22）**: cached dirtyとネイティブ2択は実装・実機確認済みだった。従来はfalse／通知なしなら即closeし、応答不能時も最後の通知へ依存した。旧コード例・旧テストはこの方式だけの記録であり、新契約の実装例・受入条件にはしない。

**現行確認（2026-11-09）**: `5cf2d85`は旧方式のままで、保存待機・問い合わせ・取消通知は未実装。`main/close-guard.ts`、mainのIPC配線・書込キュー、shared／preload／`WindowGateway`、rendererの終了応答・保存コーディネータの修正が必要。

### 7.10 エクスポート（SVG・PNG・PDF）（2026-10-22、たたき台）

設計のたたき台は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07F エクスポート設計（たたき台）|第7F章]]に置いた。renderer で SVG を組み立て、PNG は canvas、PDF は main の非表示ウィンドウ（`printToPDF`）で生成する案。決定ではなく、未決事項は第7F章の末尾にある。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|TECSCDE-DT-EL内部仕様 第7D章（7.5節、resolveImports()具体アルゴリズムの分離先）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|TECSCDE-DT-EL内部仕様 第7E章（7.5節続き、renderer側統合の分離先）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計|TECSCDE-DT-EL内部仕様 第7B章（7.6節、ファイルブラウザ設計の分離先）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|TECSCDE-DT-EL内部仕様 第7C章（7.7節、読み込み経路の統合の分離先）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様 第5章（本章が実装する外部仕様）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 03 画面構成|TECSCDE-DT外部仕様 第3章（3.5.1節、7.6節が実装するファイルブラウザの画面規定）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 07 ファイルI-O設計|TECSCDE-TS内部仕様 第7章（元の設計。DirtyTrackerは7Jで置き換え、FileIOStrategyは本章で廃止）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（プロセス配置の根拠）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様 第11章（11.2節#4、ファイルブラウザ採用の決定記録）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

- [[TECSCDE-DT-EL内部仕様 - 監査対応 39-48 編集と表示]] — 該当する監査項目の契約補足（2026-11-09）。

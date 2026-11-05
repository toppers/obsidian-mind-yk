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

Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 7 of 11. Electron固有化の中心章の1つ。

## 7. ファイルI/O設計

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様第5章]]の規定（真の上書き保存、ファイル関連付け、複数ファイル対応）を実現する。[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 07 ファイルI-O設計|TECSCDE-TS内部仕様第7章]]が提案した`FileIOStrategy`インタフェース（Electron/Tauri両対応のためのStrategyパターン）は、**本書ではTauriとの両立を考慮する必要がなくなったため廃止し**、Electronの`fs`・`dialog`を直接使う設計に置き換える。

### 7.1 `FileService`クラス（mainプロセス）

> [!note] `openDialog()`の撤回（2026-09-21）
> 複数ファイルを同時選択するOSネイティブの「開く」ダイアログは、ファイルブラウザと役割が重複するため撤回した。コマンドライン引数・ファイル関連付けで複数ファイルが渡る場合は最後を主ファイル、他を追加読み込みファイルとする。システム定義CDL（`-S`配下、第7C章7.7.4節）を除く、ユーザ定義CDL由来のセルはどのファイルでも編集可能とする（DT外部仕様第5章）。

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

  async exportFile(path: string, data: Buffer | string): Promise<void> {
    await this.writeAtomic(path, data);
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
ipcMain.handle('file:export', (_e, path: string, data: Buffer | string) => fileService.exportFile(path, data));
```

### 7.3 `FileGateway`クラス（renderer）

第2章2.4節で示したとおり、preloadが`window.tecscde.file`として公開するAPIを、rendererの`FileGateway`が薄くラップする。

```ts
// renderer/file-gateway.ts
class FileGateway {
  save(path: string, content: string): Promise<void> { return window.tecscde.file.save(path, content); }
  saveAs(content: string, suggestedName: string): Promise<string | null> { return window.tecscde.file.saveAs(content, suggestedName); }
  export(path: string, data: Buffer | string): Promise<void> { return window.tecscde.file.export(path, data); }
}
```

`DirtyTracker`クラス（未保存状態の管理、`History.past.length`基準）は[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 07 ファイルI-O設計|TECSCDE-TS内部仕様第7章]]の設計を**そのまま踏襲、変更なし**——プロセス境界とは無関係な純粋なrenderer側の状態である。

### 7.4 起動時のファイルオープン経路（コマンドライン引数・ファイル関連付け）

[[TECSCDE-DT外部仕様]]5.3節が新設した2経路（コマンドライン引数・ファイル関連付け）は、mainプロセスの起動処理で扱う。

```ts
// main/index.ts
let pendingOpenPath: string | null = null;

// Windows/Linux: コマンドライン引数、または .cde ファイルの「アプリで開く」
const argPath = process.argv.find(a => a.endsWith('.cde') || a.endsWith('.cdl'));
if (argPath) pendingOpenPath = argPath;

// macOS: Dockアイコンへのドロップ、Finderでの「このアプリで開く」
app.on('open-file', (event, path) => {
  event.preventDefault();
  pendingOpenPath = path;
});
```

`pendingOpenPath`は、rendererプロセスの初期化完了後にIPC（`app:pendingOpenPath`のような専用チャネル、または起動時に一度だけ送るイベント）で渡し、`FileGateway`を介さず直接`FileService.openPath(path)`（`openDialog`のダイアログを介さない版、7.1節に追加が必要）を呼んで読み込む。

> [!note] 実装での設計更新（2026-09-10 / 2026-09-16）
> - **起動時ドキュメント供給（`app:bootstrap`）**: renderer からの `file://` fetch が CORS 制約を受けるため、Main プロセスが `did-finish-load` 後に `app:bootstrap` IPC で初期ドキュメントのソーステキスト群（CLI 指定ファイル、または `public/samples`）を 1 回だけプッシュ供給する方式を採用。
> - **tree-sitter WASM ロード**: 同じく renderer からの直接 fetch が困難なため、Main プロセスが `fs`（asar 透過）で WASM バイナリを読み出し、IPC 経由で renderer へバイト列を渡して初期化する構成を採用。

### 7.5 インポート参照先の解決

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様5.1節]]・[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05A 開く（読み込み）|5.3節]]および同第8章8.1節が規定する参照先の自動追跡（`FileService.resolveImports()`）の詳細設計は、[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|第7D章（具体アルゴリズム・tecsgen本体との対応検証）]]・[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章（renderer側オーケストレーション・import_C境界・統合ポイント）]]に分離した（2026-09-22、25KB閾値。旧稿にあった「tecsgen本体の探索順序とは異なる（inferred・未検証）」という警告は、`Importable#find_file`の実ソース検証により第7D章7.5.3節で対応関係を確定し解消済み）。

### 7.6 ファイルブラウザ（サイドパネル）

`FileService`拡張・IPC・`FileBrowserView`・ルートフォルダの永続化（Local AppData）と起動時自動復元を含む全体設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計|第7B章（ファイルブラウザ設計）]]に分離（2026-09-22、25KB閾値）。

### 7.7 読み込み経路の統合

前回セッションの復元・ファイルブラウザからの追加読み込み・消去ボタン・tecsgenオプション形式ファイルの一括読み込み・import自動追跡との統一（第11章11.2節#7〜#11）の設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|第7C章（読み込み経路の統合）]]にまとめた。

### 7.8 入力の文字コードと非UTF-8入力（2026-10-21、ソースの確認に基づく。同日、外部仕様を実装に合わせて改訂）

**外部仕様の規定**（[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|DT外部仕様5.1節]]、2026-10-21改訂。以前は「UTF-8に限る」としていた）: 読み込みはUTF-8を優先し、できなければShift_JIS、EUC-JPの順で復号する。復号できた符号は通知しない。どれでも復号できなければ読み込めない（参照先なら`W-UNRESOLVED-REF-FILE`）。保存・書き出しは常にUTF-8。判定は復号の成否なので誤判定による文字化けがありうる。旧世代の`__location_information__`形式は、エラーにせず読み込んで無視する（外部仕様5.1節、2026-10-22改訂）。

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

### 7.9 ウィンドウを閉じるときの未保存確認（2026-10-22、設計。同日実装し、実機で確認済み）

**外部仕様の規定**（[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 03 画面構成|DT外部仕様3.1節]]、[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|5.7節]]、2026-10-22改訂）: 未保存の変更がある状態でウィンドウを閉じようとしたら、OSネイティブの確認ダイアログ（保存せずに終了／キャンセル）を出す。ブラウザの`beforeunload`には依存しない。

**従来の実装の問題**（実機確認、2026-10-22。下の設計で解消）: `renderer/app/shell.ts`の`bindBeforeUnload`は、`isDirty()`が真のとき`beforeunload`で`preventDefault()`と`returnValue = ""`を行うだけで、mainにも対応する処理が無い。実機では、未保存の変更があっても閉じるボタンで確認なしに終了し、変更が失われた。`beforeunload`が止まらない理由は未調査だが、本設計は`beforeunload`に頼らないので、原因が分からなくても成立する。

**方針**: 確認はmainのウィンドウの`close`イベントで行う。rendererは未保存かどうかを、変わるたびにmainへ知らせておく（`close`の中でrendererへ問い合わせて待つと、`close`の同期的な中断と非同期の応答が噛み合わないため）。

```ts
// main/close-guard.ts（新規）。ウィンドウごとに1つ。
class CloseGuard {
  private dirty = false;      // rendererが最後に知らせた値
  private confirmed = false;  // 利用者が「保存せずに終了」を選んだ
  private asking = false;     // ダイアログ表示中（二重表示を防ぐ）

  constructor(private readonly win: BrowserWindow) {
    win.on('close', (event) => {
      if (!this.dirty || this.confirmed) return;   // そのまま閉じる
      event.preventDefault();
      void this.confirmAndClose();
    });
  }

  setDirty(dirty: boolean): void { this.dirty = dirty; }

  private async confirmAndClose(): Promise<void> {
    if (this.asking) return;
    this.asking = true;
    try {
      const result = await dialog.showMessageBox(this.win, {
        type: 'warning',
        buttons: ['保存せずに終了', 'キャンセル'],
        defaultId: 1, cancelId: 1,
        message: '未保存の変更があります',
        detail: '保存せずに終了すると、現在の変更内容は失われます。',
      });
      if (result.response === 0) { this.confirmed = true; this.win.close(); }
    } finally { this.asking = false; }
  }
}
```

- **IPC**: rendererからmainへ一方向の`window:setDirty`（`ipcRenderer.send`。応答は不要）。`ipcMain.on`で受け、送信元の`webContents`に対応する`CloseGuard.setDirty`を呼ぶ。`createWindow`が`CloseGuard`を作って保持する（`FileService`と同じくウィンドウごと）。preloadの公開は`window.tecscde.window.setDirty(dirty: boolean)`。
- **renderer**: `AppShell`は`bindBeforeUnload`を**廃止**し、代わりにストアの購読（`store.subscribe`）で`isDirty()`の値が変わったときだけ`setDirty`を送る。起動直後の`false`も送る。ファイルの読み込み・新規作成・保存でも`isDirty()`が変わるので、同じ経路で届く。`beforeunload`は残さない——残すと`close`の確認後の`win.close()`でも`beforeunload`が再び走り、終了が止まるか、挙動が二重になる。
- **経路の網羅**: OSの閉じるボタン、`app.quit()`による終了、将来のメニューの終了は、いずれもウィンドウの`close`を通るので、同じ確認になる（`app.quit()`が各ウィンドウの`close`を呼び、`preventDefault`で終了が中断されることは、Electronの仕様の理解に基づく。実機では未確認）。`before-quit`は使わない（ウィンドウが複数ある場合に、どのウィンドウの未保存かを区別できないため。現在は1ウィンドウのみ）。
- **ダイアログの選択肢**: 7.6.4節の`confirmDiscardChanges`と同じく2択（保存せずに終了／キャンセル）。「保存してから終了」の3択は採らない。文言はファイルを開く前の確認と揃える。
- **フォールバック**: rendererが応答しない・クラッシュしたときは、最後に知らせた`dirty`で判断する。知らせが一度も無ければ`false`（確認せずに閉じる）。OSのシャットダウンなど、アプリが止められない終了は対象外。
- **実装**（2026-10-22）: `main/close-guard.ts`（`CloseGuard`）、`main/index.ts`（`createWindow`での生成と`ipcMain.on("window:setDirty")`）、`preload/index.mts`と`shared/ipc-types.ts`（`window.tecscde.window.setDirty`）、`renderer/gateways/window-gateway.ts`、`renderer/app/shell.ts`（`bindDirtyReport`。`bindBeforeUnload`は廃止）。実機で、未保存での閉じる操作に確認が出ること、「キャンセル」で閉じないこと、「保存せずに終了」で終了すること、保存後は確認なしで閉じることを確認した。
- **テスト**: `dirty=false`のとき`close`が通る／`dirty=true`で`close`が止まりダイアログが出る／「保存せずに終了」で閉じる／「キャンセル」で閉じない／ダイアログ表示中の二重`close`で二重表示しない／`setDirty`が送信元のウィンドウにだけ効く。

> [!note] 外部仕様との関係と残る論点
> 1. 外部仕様3.1節は「メニューの File > Exit」を終了経路に挙げるが、現行実装は`Menu.setApplicationMenu(null)`（`main/index.ts`）でアプリケーションメニューを外している。終了メニューは未実装である。メニューを設けた場合も、終了は上のとおり`close`を通る。
> 2. `beforeunload`が確認なしに終了した原因（ソース上は`beforeunload`の登録も`isDirty()`も結線されている）は未調査。調べる場合は、`beforeunload`の呼び出しの有無、Electronの既定の挙動、ユーザー操作の有無を見る。
### 7.10 エクスポート（SVG・PNG・PDF）（2026-10-22、たたき台）

設計のたたき台は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07F エクスポート設計（たたき台）|第7F章]]に置いた。renderer で SVG を組み立て、PNG は canvas、PDF は main の非表示ウィンドウ（`printToPDF`）で生成する案。決定ではなく、未決事項は第7F章の末尾にある。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|TECSCDE-DT-EL内部仕様 第7D章（7.5節、resolveImports()具体アルゴリズムの分離先）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|TECSCDE-DT-EL内部仕様 第7E章（7.5節続き、renderer側統合の分離先）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計|TECSCDE-DT-EL内部仕様 第7B章（7.6節、ファイルブラウザ設計の分離先）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|TECSCDE-DT-EL内部仕様 第7C章（7.7節、読み込み経路の統合の分離先）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様 第5章（本章が実装する外部仕様）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 03 画面構成|TECSCDE-DT外部仕様 第3章（3.5.1節、7.6節が実装するファイルブラウザの画面規定）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 07 ファイルI-O設計|TECSCDE-TS内部仕様 第7章（DirtyTrackerの一次情報源、FileIOStrategyは本章で廃止）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（プロセス配置の根拠）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様 第11章（11.2節#4、ファイルブラウザ採用の決定記録）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

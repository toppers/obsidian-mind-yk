---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第7章（ファイルI/O設計）— mainプロセスのFileServiceクラス（dialog+fs、アトミック書き込み）とrenderer側FileGatewayによるElectron固有実装。"
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

```ts
// main/file-service.ts
class FileService {
  constructor(private readonly window: BrowserWindow) {}

  async openDialog(): Promise<OpenResult | null> {
    const result = await dialog.showOpenDialog(this.window, {
      properties: ['openFile', 'multiSelections'],
      filters: [{ name: 'CDE files', extensions: ['cde', 'cdl'] }],
    });
    if (result.canceled || result.filePaths.length === 0) return null;
    const paths = result.filePaths;
    const editablePath = paths[paths.length - 1]!; // 最後に選択したファイルを編集対象とする
    const contents = await Promise.all(paths.map(p => fs.promises.readFile(p, 'utf-8')));
    return {
      editable: { path: editablePath, content: contents[contents.length - 1]! },
      references: paths.slice(0, -1).map((p, i) => ({ path: p, content: contents[i]! })),
    };
  }

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

ipcMain.handle('file:open', () => fileService.openDialog());
ipcMain.handle('file:save', (_e, path: string, content: string) => fileService.save(path, content));
ipcMain.handle('file:saveAs', (_e, content: string, suggestedName: string) => fileService.saveAsDialog(suggestedName, content));
ipcMain.handle('file:export', (_e, path: string, data: Buffer | string) => fileService.exportFile(path, data));
```

### 7.3 `FileGateway`クラス（renderer）

第2章2.4節で示したとおり、preloadが`window.tecscde.file`として公開するAPIを、rendererの`FileGateway`が薄くラップする。

```ts
// renderer/file-gateway.ts
class FileGateway {
  open(): Promise<OpenResult | null> { return window.tecscde.file.open(); }
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

### 7.5 インポート参照先の解決

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様5.1・5.3節]]および同第8章8.1節が規定する参照先の自動追跡は、rendererのモジュールBが抽出したインポート要求をmainの`FileService`へ渡して実現する。

```ts
interface ImportRequest {
  readonly kind: 'import' | 'import_C';
  readonly specifier: string;
}

interface ImportResolutionOptions {
  readonly baseDir?: string;
  readonly importPaths: readonly string[];
  readonly cpp?: string;
}

interface ResolvedImport {
  readonly request: ImportRequest;
  readonly canonicalPath?: string;
  readonly content?: string;
  readonly error?: 'not-found' | 'not-utf8' | 'read-failed';
}
```

`FileGateway.resolveImports(editablePath, requests, options)`は専用IPCを介して`FileService.resolveImports()`を呼ぶ。mainは、編集対象ファイルのディレクトリ、`base_dir`、`import_path`の順に候補を正規化して存在を検証し、実在したファイルをUTF-8として読み取って返す。rendererは返されたCDLを再びモジュールBへ渡し、追加の`import`／`import_C`を再帰的に解決する。循環参照と重複読み込みはmainが返す正規化済み絶対パスをキーにrenderer側で抑止する。

`base_dir`・`import_path`・`cpp`の保存値は解決処理へ入力するだけで、正規化結果や現在の環境に合わせてモデル内の値を書き換えない。解決失敗は例外で全体を中断せず、第8章の診断へ変換する。`import_C`で用いる`cpp`は第9章9.6節へ渡す起動候補であり、`FileService`自身は外部プロセスを起動しない。

## Related

- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様 第5章（本章が実装する外部仕様）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 07 ファイルI-O設計|TECSCDE-TS内部仕様 第7章（DirtyTrackerの一次情報源、FileIOStrategyは本章で廃止）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（プロセス配置の根拠）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

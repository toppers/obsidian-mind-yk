---
date: 2026-09-21
description: "TECSCDE-DT-EL内部仕様書 第7章7.6節（ファイルブラウザ設計）— 階層ツリー表示のサイドパネル。FileService拡張・IPC・FileBrowserView・ルートフォルダの永続化（Local AppData）と起動時自動復元。第7章から分離（2026-09-22、25KB閾値）。同日、7.6.4節に未保存確認（FileService.confirmDiscardChanges、OSネイティブdialog.showMessageBox）の設計を実装。"
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

Domain note split from [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章]] (2026-09-22, 25KB threshold)。第7章7.6節（[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 03 画面構成|TECSCDE-DT外部仕様3.5.1節]]・[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|同5.3節]]が採用したファイルブラウザ機能）をverbatimで分離。

## 7.6 ファイルブラウザ（サイドパネル） — 2026-09-21追加

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 03 画面構成|TECSCDE-DT外部仕様3.5.1節]]・[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|同5.3節]]が新規に採用した機能。[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|第2章]]の原則（`fs`を直接扱うのはmainのみ、renderer側はIPC越しのGateway経由）をそのまま適用する。

> [!note] 訂正
> [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|第11章]]11.2節#4は以前「mainプロセスに`fs.readdir`（`FileService`の拡張）が既にある」と記載していたが誤りだった。2026-09-21時点の[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]の`FileService`にディレクトリ列挙機能は存在せず、本節の設計は新規実装として書き下ろす。

### 7.6.1 `FileService`の拡張（main）

```ts
// main/file-service.ts に追加
export interface DirEntry {
  readonly name: string;
  readonly path: string;
  readonly kind: 'directory' | 'file';
}

class FileService {
  // ...既存メソッド（第7章7.1節）...

  /** 実機確認で判明（2026-09-21）: 毎回同じ既定ディレクトリが出るのは不便なため、
   * 直前に選んだフォルダを`defaultPath`として渡し、次回のダイアログの初期位置にする。 */
  private lastChosenFolder: string | undefined;

  async chooseFolder(): Promise<string | null> {
    const result = await dialog.showOpenDialog(this.window, {
      properties: ['openDirectory'],
      defaultPath: this.lastChosenFolder,
    });
    if (result.canceled || result.filePaths.length === 0) return null;
    this.lastChosenFolder = result.filePaths[0]!;
    return this.lastChosenFolder;
  }

  /** 3.5.1節: ディレクトリ直下のみを1階層返す。ツリー展開のたびにrendererから呼ばれる。 */
  async listDirectory(dirPath: string): Promise<DirEntry[]> {
    const entries = await fs.promises.readdir(dirPath, { withFileTypes: true });
    return entries
      .filter((e) => e.isDirectory() || /\.(cde|cdl)$/i.test(e.name))
      .map((e) => ({
        name: e.name,
        path: path.join(dirPath, e.name),
        kind: e.isDirectory() ? ('directory' as const) : ('file' as const),
      }))
      .sort((a, b) => (a.kind !== b.kind ? (a.kind === 'directory' ? -1 : 1) : a.name.localeCompare(b.name)));
  }
}
```

**設計判断**: 起動時にツリー全体を再帰的に読み込まず、ディレクトリ展開のたびに1階層ずつ`listDirectory`を呼ぶ（遅延展開）。tecsgenプロジェクトは本アプリに関係のない大きなサブディレクトリ（生成物・ビルド成果物等）を含みうるため、全体を先読みする設計は採らない。

### 7.6.2 IPC・preload・`FileGateway`の拡張

```ts
// main/ipc.ts に追加
ipcMain.handle('file:chooseFolder', () => fileService.chooseFolder());
ipcMain.handle('file:listDirectory', (_e, dirPath: string) => fileService.listDirectory(dirPath));
ipcMain.handle('file:openPath', (_e, path: string) => fileService.openPath(path));
```

`file:openPath`は第7章7.4節で導入済みの`FileService.openPath()`（起動時専用だった）を、ファイルブラウザのクリックからも呼べるよう新たにIPC公開する。

```ts
// shared/ipc-types.ts の TecscdeApi.file に追加
chooseFolder(): Promise<string | null>;
listDirectory(dirPath: string): Promise<DirEntry[]>;
openPath(path: string): Promise<OpenResult>;
```

`FileGateway`は既存3メソッド（第7章7.3節）と同じ薄いラップを追加するのみ。

### 7.6.3 `FileBrowserView`（renderer、モジュールG）

既存の`PaletteView`・`NavigatorView`等（第2章2.3節・[[TECSCDE-DT-EL実装]]）と同じ「専用DOM要素を受け取り`AppStore`を購読して描画する」パターンに従う。

```ts
// renderer/app/file-browser-panel.ts
export class FileBrowserView {
  private root: string | null = null;
  private readonly expanded = new Set<string>();
  private readonly children = new Map<string, DirEntry[]>(); // pathごとの展開キャッシュ

  constructor(
    private readonly el: HTMLElement,
    private readonly store: AppStore,
    private readonly gateway: FileGateway,
    private readonly onOpen: (path: string) => void, // クリック時に7.6.4のopenFromPathを呼ぶ
  ) {}

  async chooseRoot(): Promise<void> {
    const dir = await this.gateway.chooseFolder();
    if (!dir) return;
    this.root = dir;
    this.expanded.clear();
    this.children.clear();
    await this.loadChildren(dir);
    this.render();
  }

  private async loadChildren(dirPath: string): Promise<void> {
    if (this.children.has(dirPath)) return;
    this.children.set(dirPath, await this.gateway.listDirectory(dirPath));
  }

  // render(): 展開状態(expanded)とキャッシュ(children)からツリーのDOMを組み立てる。
  // store.filePath と一致するノードへ強調表示クラスを付与する
  // （3.5.1節「現在編集対象になっているファイルの強調表示」）。
  render(): void { /* ... */ }
}
```

`expanded`・`children`はクラス内部の状態としてのみ保持し、`AppStore`にもCDEファイルの保存内容にも含めない（3.5.1節「ツリーの展開状態はアプリケーション実行中の状態としてのみ保持する」）。

### 7.6.4 未保存確認 — 2026-09-22実装

外部仕様5.3節・5.7節は「ファイルブラウザ経由のファイルを開く操作は未保存の変更がある場合5.7節の確認を経る」と規定する。実現手段は[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様5.7節（2026-09-22追加）]]のとおりOSネイティブの確認ダイアログ（`dialog.showMessageBox`）とする——3.6.2節が禁じるのは表示内容を制御できないブラウザ標準`confirm`であり、OSネイティブAPIは対象外（`dialog.showSaveDialog`等の既存採用と同じ扱い）。

新規クラスは設けず、既に`window`と`electron.dialog`を持つ`FileService`（第7章7.1節）にメソッドを追加する——専用の確認ダイアログ機構を独立させるほどの複雑さではなく、`dialog.showOpenDialog`/`dialog.showSaveDialog`と同じ技術的関心事のため。

```ts
// main/file-service.ts に追加
async confirmDiscardChanges(): Promise<boolean> {
  const result = await dialog.showMessageBox(this.window, {
    type: 'warning',
    buttons: ['保存せずに開く', 'キャンセル'],
    defaultId: 1,
    cancelId: 1,
    message: '未保存の変更があります',
    detail: '保存せずに別のファイルを開くと、現在の変更内容は失われます。',
  });
  return result.response === 0;
}
```

```ts
// main/ipc.ts に追加
ipcMain.handle('file:confirmDiscardChanges', () => fileService.confirmDiscardChanges());
```

```ts
// shared/ipc-types.ts の TecscdeApi.file に追加
confirmDiscardChanges(): Promise<boolean>;
```

`FileGateway`は既存メソッドと同じ薄いラップを追加する。`file-actions.ts`の`openFromPath`は、`store.isDirty()`が真の場合にのみ確認を挟む——ダイアログの表示自体を最小限にする（未保存でなければ即座に開く）。

```ts
// renderer/app/file-actions.ts の openFromPath を変更
export async function openFromPath(store: AppStore, gateway: FileGateway, path: string): Promise<void> {
  if (store.isDirty()) {
    const proceed = await gateway.confirmDiscardChanges();
    if (!proceed) return;
  }
  const result = await gateway.openPath(path);
  applyOpenResult(store, result);
}
```

「保存してから開く」という3択（保存する／保存しない／キャンセル）は採用しない——外部仕様5.7.2節の元規定はブラウザの`beforeunload`（離れる／キャンセルの2択）を踏まえたものであり、「破棄の確認」という言葉のとおり2択（保存せずに開く／キャンセル）に留める。保存してから別ファイルを開きたい場合は、利用者が先に「保存」操作を行う。

**未保存確認の対象は本節（ファイルブラウザ経由）のみ**——コマンドライン引数・ファイル関連付け経由の起動時オープン（第7章7.4節）はアプリ起動時点であり編集中のドキュメントが存在しないため対象外。新規作成機能はDT-EL版に未実装のため、5.7.2節が定めるもう一方の対象（新規作成）は本節の対象外のまま残る（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|第11章]]参照）。

### 7.6.5 `AppShell`への配線

`index.html`にサイドパネル用の`#file-browser`要素と、ツールバーに`data-action="openFolder"`ボタンを追加する。`AppShell`は他パネル（7.6.3節）と同様にコンストラクタで`FileBrowserView`を生成し、`runAction`に`case 'openFolder':`を追加して`chooseRoot()`を呼ぶ。

> [!note] `open`アクションの撤去（2026-09-21）
> 第7章7.1節の撤回に伴い、ツールバーの`data-action="open"`ボタン・`Ctrl+O`キーボードショートカット・`runAction`の`case 'open':`・`file-actions.ts`の`openViaDialog()`をいずれも削除する。編集対象を選ぶツールバー操作は`openFolder`（フォルダ選択→ファイルブラウザのクリック）のみになる。

### 7.6.6 ルートフォルダの永続化と起動時の自動復元 — 2026-09-21追加

[[TECSCDE-DT外部仕様]]3.5.1節が新設した規定。ツリーの展開状態・選択位置（7.6.3節）とは異なり、ルートフォルダの選択自体はセッションをまたいで維持する利用者設定として扱う。既存の`FileService`（1ウィンドウに紐づくダイアログ操作）とは異なる関心事（ウィンドウ非依存のアプリケーション設定）のため、別モジュールに切り出す。

```ts
// main/app-settings.ts
export interface AppSettings {
  readonly fileBrowserRoot?: string;
}

export async function loadAppSettings(): Promise<AppSettings> {
  try {
    const raw = await fs.promises.readFile(settingsPath(), 'utf-8');
    return JSON.parse(raw) as AppSettings;
  } catch {
    return {}; // 初回起動・壊れた設定ファイルはいずれも「設定なし」として扱う
  }
}

export async function saveAppSettings(settings: AppSettings): Promise<void> {
  const dir = settingsDir();
  await fs.promises.mkdir(dir, { recursive: true });
  await fs.promises.writeFile(path.join(dir, 'settings.json'), JSON.stringify(settings));
}

/**
 * 2026-09-22訂正: `app.getPath('userData')`（Windowsでは`%APPDATA%`＝Roaming）は
 * ドメイン環境でローミングプロファイルが有効だと複数PC間で同期されうる。ファイルブラウザの
 * ルートフォルダは各PC固有のローカルパスを指すため、ローミングされると別PCでは無効なパスが
 * 復元されてしまう——PC固有の設定は明示的にLocal AppData配下へ置く。Windows以外に
 * Roaming/Localの区別は無いため、Windows以外では`userData`のままでよい。
 */
function settingsDir(): string {
  if (process.platform === 'win32' && process.env.LOCALAPPDATA) {
    return path.join(process.env.LOCALAPPDATA, 'tecscde-dt-el');
  }
  return app.getPath('userData');
}

function settingsPath(): string {
  return path.join(settingsDir(), 'settings.json');
}
```

設定ファイルはCDEファイルと異なり壊れても実害が「記憶が1件失われる」程度に留まるため、第7章7.1節の`writeAtomic`のような一時ファイル＋リネームは要求しない。`app.getPath('userData')`と異なりLocal AppData配下の`tecscde-dt-el/`ディレクトリはElectronが自動生成しないため、`saveAppSettings()`は書き込み前に`mkdir(..., { recursive: true })`する。

**保存のタイミング**: `chooseFolder()`が成功するたびに（＝フォルダを選び直すたびに）保存する。「終了時にまとめて保存」ではなく都度保存とするのは、異常終了（クラッシュ・強制終了）でも直前の選択が残るようにするため。

```ts
// main/file-service.ts の chooseFolder() を変更
async chooseFolder(): Promise<string | null> {
  const result = await dialog.showOpenDialog(this.window, {
    properties: ['openDirectory'],
    defaultPath: this.lastChosenFolder,
  });
  if (result.canceled || result.filePaths.length === 0) return null;
  this.lastChosenFolder = result.filePaths[0]!;
  await saveAppSettings({ fileBrowserRoot: this.lastChosenFolder });
  return this.lastChosenFolder;
}
```

**起動時の自動復元**: `main/index.ts`の起動処理で`loadAppSettings()`を読み、`fileBrowserRoot`があれば`did-finish-load`後（第7章7.4節の`app:bootstrap`と同じタイミング）に専用IPCで送る。ドキュメントのブートストラップとは独立した関心事のため、`app:bootstrap`のペイロードに混ぜず別チャネルにする。

> [!bug] `chooseFolder()`のダイアログ初期位置が復元されない（実機確認で発見、2026-09-21）
> `FileService.lastChosenFolder`（`chooseFolder()`の`defaultPath`に使う、7.6.1節）はインスタンスのメモリ上の状態であり、`loadAppSettings()`による起動時の復元では更新されない。結果、再起動直後に一度も`chooseFolder()`を呼んでいない状態で「フォルダを開く」を押すと、`defaultPath`が`undefined`のままOS既定のディレクトリ（Windowsでは通常Documents）が開いてしまう——ファイルブラウザ自体は正しく前回のルートを復元して表示するため、この不整合は気づきにくい。**対処**: `FileService`に`primeLastChosenFolder(path: string): void`を追加し、起動時の復元と同じタイミングで呼んで`lastChosenFolder`を先に埋めておく。

```ts
// main/file-service.ts に追加
primeLastChosenFolder(path: string): void {
  this.lastChosenFolder = path;
}
```

```ts
// main/index.ts（did-finish-loadハンドラに追加）
const settings = await loadAppSettings();
if (settings.fileBrowserRoot) {
  fileService.primeLastChosenFolder(settings.fileBrowserRoot);
  win.webContents.send('app:fileBrowserRoot', settings.fileBrowserRoot);
}
```

```ts
// shared/ipc-types.ts の TecscdeApi に追加（onBootstrapと対の一度きりリスナー）
readonly onRestoreFileBrowserRoot: (listener: (path: string) => void) => void;
```

`FileBrowserView`は、ダイアログ経由の`chooseRoot()`と復元専用の`restoreRoot(path)`とで、ルート設定以降の処理（キャッシュクリア・子の読み込み・展開・描画）を共有する。

```ts
// renderer/app/file-browser-panel.ts
export class FileBrowserView {
  // ...7.6.3節のコンストラクタ・フィールド...

  async chooseRoot(): Promise<void> {
    const dir = await this.gateway.chooseFolder();
    if (dir) await this.setRoot(dir);
  }

  /** 起動時の自動復元用。フォルダが存在しない・アクセスできない場合は
   * フォルダ未選択のまま起動する（エラーにしない、3.5.1節）。 */
  async restoreRoot(dir: string): Promise<void> {
    try {
      await this.setRoot(dir);
    } catch {
      this.root = null;
      this.render();
    }
  }

  private async setRoot(dir: string): Promise<void> {
    this.root = dir;
    this.expanded.clear();
    this.children.clear();
    await this.loadChildren(dir);
    this.expanded.add(dir);
    this.render();
  }
}
```

`AppShell`（7.6.5節）は起動時に`gateway.onRestoreFileBrowserRoot((path) => void this.fileBrowser.restoreRoot(path))`を一度だけ登録する。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|TECSCDE-DT-EL内部仕様 第7C章（7.7節、前回セッション復元・参照専用追加・消去ボタン・オプションファイル読込・import統一の設計）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章（本ノートの分離元、7.1〜7.5節）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 03 画面構成|TECSCDE-DT外部仕様 第3章（3.5.1節、本節が実装するファイルブラウザの画面規定）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様 第5章（5.3節、ファイル選択ダイアログ経路の撤回）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（プロセス配置の根拠）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様 第11章（11.2節#4、ファイルブラウザ採用の決定記録）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

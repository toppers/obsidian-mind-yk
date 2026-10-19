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
> 複数ファイルを同時選択するOSネイティブの「開く」ダイアログは、ファイルブラウザと役割が重複するため撤回した。コマンドライン引数・ファイル関連付けで複数ファイルが渡る場合は最後を主ファイル、他を追加読み込みファイルとする。通常CDL由来のセルはどのファイルでも編集可能とする（DT外部仕様第5章）。

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

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様5.1・5.3節]]および同第8章8.1節が規定する参照先の自動追跡（`FileService.resolveImports()`）の詳細設計は、[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|第7D章（具体アルゴリズム・tecsgen本体との対応検証）]]・[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章（renderer側オーケストレーション・import_C境界・統合ポイント）]]に分離した（2026-09-22、25KB閾値。旧稿にあった「tecsgen本体の探索順序とは異なる（inferred・未検証）」という警告は、`Importable#find_file`の実ソース検証により第7D章7.5.3節で対応関係を確定し解消済み）。

### 7.6 ファイルブラウザ（サイドパネル）

`FileService`拡張・IPC・`FileBrowserView`・ルートフォルダの永続化（Local AppData）と起動時自動復元を含む全体設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計|第7B章（ファイルブラウザ設計）]]に分離（2026-09-22、25KB閾値）。

### 7.7 読み込み経路の統合

前回セッションの復元・ファイルブラウザからの追加読み込み・消去ボタン・tecsgenオプション形式ファイルの一括読み込み・import自動追跡との統一（第11章11.2節#7〜#11）の設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|第7C章（読み込み経路の統合）]]にまとめた。

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

---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第2章（モジュール構成とプロセス境界）— 9モジュールをmain/renderer/preloadへ配置し、IPCゲートウェイクラス（FileGateway/TecsgenGateway）を設計する。本書の中心章。"
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

Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 2 of 11. **本書の中心章**。

## 2. モジュール構成とプロセス境界

### 2.1 モジュール一覧・依存方向は既存と同一

9モジュール（A〜I）の責務・依存方向は[[TECSCDE内部仕様]]第2章・[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 02 モジュール構成と責務境界|TECSCDE-TS内部仕様第2章]]と**同一であり、本章では再掲しない**。本章が追加するのは、これらのモジュールをElectronの2プロセス（main／renderer）にどう配置するかという、直交する軸である。

### 2.2 プロセスモデル

Electronはセキュリティ上の理由（`contextIsolation: true`を既定とする）から、次の3つのコンテキストに分かれる。

| コンテキスト | 特徴 | 本書での役割 |
|---|---|---|
| **main** | Node.js フルアクセス（`fs`・`child_process`等）。OSごとに1プロセス | OSリソースへの唯一のアクセス点 |
| **preload** | mainとは別プロセスだが、Node/ElectronのAPIに限定的にアクセスできる橋渡し役。`contextBridge.exposeInMainWorld`でrendererに公開するAPIを定義する。**ESM（`.mjs`）で書き`sandbox: false`とする**（[[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定\|決定 2026-09-08]]、第11章11.2節#1） | ゲートウェイの定義点。IPCを直接使う処理と、Node APIを直接ブリッジするだけの処理の両方をここに置く |
| **renderer** | Chromiumのウェブページ相当。既定ではNode.js APIへのアクセスを持たない | UI・モデル・コマンド・描画の実行コンテキスト |

### 2.3 モジュール別プロセス配置

| #   | モジュール            | 配置                                                  | 理由                                                                                                                                                                                    |
| --- | ---------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A   | ファイルI/O          | **main**（`FileService`）                             | `fs`・`dialog`はNode/Electronのmain専用API。`dialog`は`BrowserWindow`に紐づくため、mainプロセスからの操作が自然                                                                                                 |
| B   | CDLパーサ／シリアライザ    | **renderer**                                        | テキスト→モデルの変換は純粋な計算処理であり、OSリソースへのアクセスを必要としない。ファイル内容自体はAから渡されるだけでよい。**2026-09-13追記**: 構文解析をtree-sitter文法へ委ねる改訂（[[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 04 CDLパーサ／シリアライザ設計\|TECSCDE内部仕様第4章]]）を受けても配置は変わらない——ただしrendererは`nodeIntegration: false`（2.4節）のためネイティブバインディングを読み込めず、**rendererに置く限りWASM版（`web-tree-sitter`）に限られる**。11.2節#5 |
| C   | モデル              | **renderer**                                        | [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 03 モデル設計\|TECSCDE-TS内部仕様第3章]]のクラス設計をそのまま踏襲。UIから直接操作されるため                                                                                |
| D   | 編集コマンド／Undo-Redo | **renderer**                                        | 同上。`History`クラスはUI操作に対して同期的に応答する必要がある                                                                                                                                                 |
| E   | 描画（SVGレンダリング）    | **renderer**                                        | DOM/SVGへのアクセスはrendererプロセスでのみ可能                                                                                                                                                       |
| F   | 表示制御（View State） | **renderer**                                        | UI状態そのものであり、rendererに閉じる                                                                                                                                                              |
| G   | UIシェル            | **renderer**                                        | 同上                                                                                                                                                                                    |
| H   | 整合性チェック／診断       | **renderer**                                        | `DiagnosticsCollector`はB（renderer）とI（mainの実行結果をIPC経由で受け取る）の両方から診断を集約する。集約先自体はrendererに置き、mainからの結果はIPC経由の入力として扱う                                                                      |
| I   | tecsgen連携        | **main**（`TecsgenRunner`）＋**renderer**（コマンド文字列組み立て） | サブプロセス起動（`child_process`）はmain専用。ただしコマンド文字列の組み立て自体（[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 09 tecsgen連携設計\|TECSCDE-TS内部仕様第9章]]の`TecsgenCommandBuilder`）は純粋な文字列処理でありrendererに残せる |

**要点**: 9モジュールのうち、mainプロセスに置く必要があるのは**A（ファイルI/O）とI（tecsgenのサブプロセス実行部分のみ）**の2つに限られる。残る7モジュール（B・C・D・E・F・G・H）は[[TECSCDE-TS内部仕様]]の設計をそのままrendererプロセスへ持ち込める。

### 2.4 IPCゲートウェイ設計

main専用の機能（A・I）を、renderer側のクラスから**Promiseを返す通常のメソッド呼び出しであるかのように**使えるようにする。

```
┌─────────────── main process ───────────────┐
│  FileService          TecsgenRunner          │
│  (fs, dialog)          (child_process)        │
└──────────────┬───────────────┬───────────────┘
               │ ipcMain.handle │
┌──────────────┴───────────────┴───────────────┐
│              preload script                    │
│  contextBridge.exposeInMainWorld('tecscde', {  │
│    file: { open, save, saveAs, export,         │
│            resolveImports },                   │
│    tecsgen: { generate, preprocess, version }, │
│    clipboard: { writeText, readText },         │
│  })                                            │
└──────────────┬─────────────────────────────────┘
               │ window.tecscde.*
┌──────────────┴───────────────────────────────┐
│            renderer process                    │
│  FileGateway   TecsgenGateway   （clipboardは  │
│  （Aへの窓口） （Iへの窓口）    直接ブリッジ） │
│         ↓             ↓                        │
│      G (UIシェル) が呼び出す                    │
└────────────────────────────────────────────────┘
```

```ts
// preload.mts（ESM。Node/Electron APIへアクセスできるコンテキスト、sandbox: false）
import { contextBridge, ipcRenderer } from 'electron';
import { createRequire } from 'node:module';

// ESMの`electron`はpreload/renderer向けにcontextBridge/ipcRenderer/webFrame/
// webUtils/nativeImage/crashReporterのみを名前付きエクスポートする。`clipboard`は
// 含まれないため、非サンドボックスpreloadのCJS版から取得する。
const { clipboard } = createRequire(import.meta.url)('electron') as typeof import('electron');

contextBridge.exposeInMainWorld('tecscde', {
  file: {
    open: (): Promise<OpenResult> => ipcRenderer.invoke('file:open'),
    save: (path: string, content: string): Promise<void> => ipcRenderer.invoke('file:save', path, content),
    saveAs: (content: string, suggestedName: string): Promise<string> => ipcRenderer.invoke('file:saveAs', content, suggestedName),
    export: (path: string, data: Buffer | string): Promise<void> => ipcRenderer.invoke('file:export', path, data),
    resolveImports: (editablePath: string, requests: readonly ImportRequest[], options: ImportResolutionOptions): Promise<readonly ResolvedImport[]> =>
      ipcRenderer.invoke('file:resolveImports', editablePath, requests, options),
  },
  tecsgen: {
    generate: (args: readonly string[]): Promise<TecsgenResult> => ipcRenderer.invoke('tecsgen:generate', args),
    preprocess: (headerPath: string, cppCommand?: string): Promise<CppResult> => ipcRenderer.invoke('tecsgen:preprocess', headerPath, cppCommand),
    version(): Promise<string | null> => ipcRenderer.invoke('tecsgen:version'),
  },
  // clipboardはipcMainを介さず、preloadから直接ブリッジできる
  // （非サンドボックスpreloadではElectronのclipboardモジュールを直接利用可能なため）
  clipboard: {
    writeText: (text: string): void => clipboard.writeText(text),
    readText: (): string => clipboard.readText(),
  },
});
```

```ts
// renderer側: main.ts 等が生成するゲートウェイクラス
class FileGateway {
  open(): Promise<OpenResult | null> { return window.tecscde.file.open(); }
  save(path: string, content: string): Promise<void> { return window.tecscde.file.save(path, content); }
  saveAs(content: string, suggestedName: string): Promise<string | null> { return window.tecscde.file.saveAs(content, suggestedName); }
  export(path: string, data: Buffer | string): Promise<void> { return window.tecscde.file.export(path, data); }
  resolveImports(editablePath: string, requests: readonly ImportRequest[], options: ImportResolutionOptions): Promise<readonly ResolvedImport[]> {
    return window.tecscde.file.resolveImports(editablePath, requests, options);
  }
}

class TecsgenGateway {
  generate(args: readonly string[]): Promise<TecsgenResult> { return window.tecscde.tecsgen.generate(args); }
  preprocess(headerPath: string, cppCommand?: string): Promise<CppResult> { return window.tecscde.tecsgen.preprocess(headerPath, cppCommand); }
  version(): Promise<string | null> { return window.tecscde.tecsgen.version(); }
}
```

`FileGateway`・`TecsgenGateway`は、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 07 ファイルI-O設計|TECSCDE-TS内部仕様第7章]]の`FileSaver`・[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 09 tecsgen連携設計|同第9章]]の`TecsgenCommandBuilder`が担っていた役割を、**IPC越しの薄いプロキシとして**引き継ぐ。呼び出し側（モジュールG）から見れば、Promiseを返す通常のクラスメソッドであることに変わりはない——プロセス境界がある事実はゲートウェイクラスの内部に閉じ込め、UIシェルはそれを意識しない。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 02 モジュール構成と責務境界|TECSCDE-TS内部仕様 第2章（モジュール分割・依存方向の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章（FileService/FileGatewayの詳細）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様 第9章（TecsgenRunner/TecsgenGatewayの詳細）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

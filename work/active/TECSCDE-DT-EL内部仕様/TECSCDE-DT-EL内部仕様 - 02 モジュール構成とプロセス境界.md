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
│    cdl, file, tecsgen, clipboard,              │
│    settings, window, log,                      │
│    onBootstrap, onRestoreFileBrowserRoot,      │
│  })   （内訳は下の表。型は TecscdeApi）         │
└──────────────┬─────────────────────────────────┘
               │ window.tecscde.*
┌──────────────┴───────────────────────────────┐
│            renderer process                    │
│  FileGateway   TecsgenGateway   ClipboardGateway │
│  （Aへの窓口） （Iへの窓口）   （mainのclipboard │
│                                  への窓口）      │
│         ↓             ↓                        │
│      G (UIシェル) が呼び出す                    │
└────────────────────────────────────────────────┘
```

preload（`src/preload/index.mts`）が`window.tecscde`として公開するAPIの全体の型は、`src/shared/ipc-types.ts`の`TecscdeApi`が一次情報である（2026-10-22に、擬似コードを全文で持つのをやめた。メソッドの追加・撤回のたびに、ここが古くなっていたため）。名前空間ごとの役割は次のとおり。

| 名前空間 | 役割 | 詳細 |
|---|---|---|
| `cdl` | CDL・cdecl文法のWASMの読み込み（`loadGrammarAssets`） | 第4B章4B.3節、第9B章9B.3節 |
| `file` | ファイルI/O。`save`・`saveAs`・`export`・`chooseFolder`・`listDirectory`・`openPath`・`confirmDiscardChanges`・`saveSession`・`resolveImports`・`parseTecsgenOptionsFile`（OSの「開く」ダイアログによる`open`は、ファイルブラウザへの一本化で撤回した） | 第7章 |
| `tecsgen` | tecsgenの実行。`generate`・`generatedTypes`・`preprocess`・`version` | 第9章・第9C章 |
| `clipboard` | OSクリップボードの読み書き（`writeText`・`readText`）。preloadに公開される`electron`モジュールには`clipboard`が含まれない（ESM／CJSを問わない。実機確認）ため、`file`・`tecsgen`と同じくipcMain経由にしている | 第4章4.1節 |
| `settings` | rendererが読むアプリケーション設定（`get`） | 第3章3.2節 |
| `window` | 未保存かどうかをmainへ知らせる（`setDirty`） | 第7章7.9節 |
| `log` | 診断パネルの内容を、起動ごとのログファイルへ追記する（`append`。mainの`LogService`、rendererの`DiagnosticsLogger`） | 外部仕様9.5節（2026-11-01 採用）。専用の設計節は無い（第9C章9C.5節が版の記録に使う）。9.5節の置き場所（`logsDirectory()`＝設定ファイルと同じフォルダの`logs/`）・書き込み失敗の警告（`LogService.append`が最初の失敗だけ`{ newFailure }`を返し、rendererの`createLogAppender`がストアへ`W-LOG-WRITE-FAILED`を入れる）・30個の保存期間（起動時の`pruneOldLogs`）は実装済み（2026-11-02、実装リポジトリPR #21、同日マージ`cdbb8c1`） |
| `onBootstrap`・`onRestoreFileBrowserRoot` | mainが起動時に一度だけ送る起動ドキュメントとファイルブラウザのルート（イベント） | 第7章7.4節・7.6.6節 |

renderer側のゲートウェイクラス（`FileGateway`・`TecsgenGateway`・`ClipboardGateway`・`LogGateway`・`WindowGateway`・`SettingsGateway`、`src/renderer/gateways/`）は、上の各名前空間を**Promiseを返す通常のメソッド**として薄くラップするだけで、プロセス境界をこのクラスの内部に閉じ込める。メソッドの一覧は`TecscdeApi`と、各ゲートウェイのソースを参照する。

`FileGateway`・`TecsgenGateway`は、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 07 ファイルI-O設計|TECSCDE-TS内部仕様第7章]]の`FileSaver`・[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 09 tecsgen連携設計|同第9章]]の`TecsgenCommandBuilder`が担っていた役割を、**IPC越しの薄いプロキシとして**引き継ぐ。呼び出し側（モジュールG）から見れば、Promiseを返す通常のクラスメソッドであることに変わりはない——プロセス境界がある事実はゲートウェイクラスの内部に閉じ込め、UIシェルはそれを意識しない。

### 2.5 アプリケーションの版（2026-11-01 追加）

外部仕様[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 02 動作環境|2.5.5]]・[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 03 画面構成|3.8]]の設計。

- **情報源の一本化**: `scripts/build-renderer.mjs` の esbuild の `define` で、`package.json` の `version` とコミットの短縮ハッシュ（`git rev-parse --short HEAD`。取れなければ `unknown`）を、画面側のコードに埋め込む。`tool-info-types.ts` の手書きの定数 `TECSCDE_TS_VERSION` をやめ、埋め込まれた値を使う。vitest にも同じ `define` を渡す。main 側は `app.getVersion()`（= `package.json`）をそのまま使う。
- **実行環境の版**: preload に、読み取り専用の `versions`（`process.versions` の Electron・Chromium・Node、`process.platform`）を追加する。preload から渡せるかは、`sandbox` の設定による（実装時に確認）。
- **tecsgen の版**: 起動時の確認（第9C章）の結果のうち、確認できた版と、使われた起動コマンドを、`AppStore` に保持する（いまは診断ログの1行にしか使っていない）。
- **ダイアログ**: `<dialog>`。既存の `celltype-details.ts` と同じ作りにする。「コピー」は `ClipboardGateway` を使う。
- **診断ログの先頭行**: `LogService` のコンストラクタに版（`app.getVersion()`）を渡し、先頭行に入れる。
- **実装単位**: V1 一本化、V2 ダイアログとボタン、V3 診断ログの先頭行（コマンドライン `--version` は今回採らない。余裕があれば別に検討）。**V1〜V3 は 2026-11-01 に実装済み**（実装リポジトリ toppers/tecscde-dt-el の #16・#17・#18）。`TecsgenVersionResult.command` は省略可の項目、`LogService` のコンストラクタは `dirs, appVersion, now` の順で版は必須。進め方とテストは[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 バージョン表示追加案|追加案]]。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 02 モジュール構成と責務境界|TECSCDE-TS内部仕様 第2章（モジュール分割・依存方向の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章（FileService/FileGatewayの詳細）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様 第9章（TecsgenRunner/TecsgenGatewayの詳細）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

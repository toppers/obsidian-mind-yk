---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書（Electron・TypeScriptクラスベース）の目次。main/renderer/preloadのプロセス境界設計が中心。全11章と03B・7B〜7E・9B・11Bの章別ノート。"
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

# TECSCDE-DT-EL 内部仕様（Electron・クラスベース）

> [!info] 文書状態
> **全11章執筆完了（2026-09-05）／実装着手・検証完了（2026-09-16）** — [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]]（デスクトップ版、Electron/Tauri言語非依存）を、**TypeScriptクラスベース設計で、Electronに固有化して**実装するための内部仕様として起こした。2つの先行文書の交点に位置する。
>
> | 軸 | 先行文書 | 本書での扱い |
> |---|---|---|
> | クラス設計（`Cell`/`Command`/`History`等） | [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様\|TECSCDE-TS内部仕様]] | **そのまま踏襲**（第3〜6章・第8章）。モデル・コマンド・描画・表示制御は実行環境に依存しないため変更しない |
> | デスクトップ機能（ネイティブfs・tecsgen実行・OSクリップボード） | [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様\|TECSCDE-DT外部仕様]] | **Electronに固有化**（第7章・第9章）。Tauriとの両立を考慮する必要がなくなったため、Electron固有のAPI（Node.js `fs`・`child_process`・`clipboard`・`dialog`）を直接使う設計に書き換える |
> | **プロセス境界（main/renderer/preload）** | **どちらの先行文書にもない** | **本書が新規に追加する中心的な設計**（第2章）。Electronのセキュリティモデル（`contextIsolation`）は、Node.js APIを直接使えるmainプロセスと、Webページ相当のrendererプロセスを分離するため、9モジュール（A〜I）のどれがどちらのプロセスで動くかを新たに決定する必要がある |
>
> **実装（[[TECSCDE-DT-EL実装]]）の進捗**: 2026-09-06〜09-16 にかけて全モジュール（モデル、コマンド、描画、表示制御、ファイルI/O、診断、tecsgen連携、UIシェル、tree-sitter WASM IPC転送、Electron Forge package/make）の実装と実機動作確認（191テストpass）が完了している。実装過程で判明した相違点・確定事項は下記および第11章11.5節を参照。

## 目次

1. [[TECSCDE-DT-EL内部仕様 - 01 概要]]
2. [[TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界]] — 本書の中心。main/renderer/preloadへのモジュール配置とIPC契約
3. [[TECSCDE-DT-EL内部仕様 - 03 モデル設計]] 基本モデルは[[TECSCDE-TS内部仕様]]を踏襲。複合セルタイプは[[TECSCDE-DT-EL内部仕様 - 03B 複合セルタイプ設計|03B 複合セルタイプ設計]]で定める
4. [[TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計]] — 同上
5. [[TECSCDE-DT-EL内部仕様 - 05 描画・インタラクション設計]] 基本描画を踏襲。複合セルタイプの非展開は03Bで定める
6. [[TECSCDE-DT-EL内部仕様 - 06 表示制御設計]] — 同上
7. [[TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 - 07 ファイルI/O設計]] — Electron固有化。`dialog`/`fs`をmainプロセスに置き、`FileGateway`でIPC経由公開（インポート参照先解決含む）
   - [[TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡]] — 7.5節前半（2026-09-22詳細化）。`FileService.resolveImports()`の具体アルゴリズム、tecsgen本体（`Importable#find_file`）との対応関係の実地検証
   - [[TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合]] — 7.5節後半（2026-09-22詳細化）。renderer側の再帰的解決オーケストレーション・import_Cの第9章への受け渡し境界・診断・既存コードへの統合ポイント
   - [[TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計]] — 7.6節（2026-09-21追加、2026-09-22分離）。階層ツリー表示・ルートフォルダの永続化（Local AppData）と起動時自動復元
   - [[TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合]] — 7.7節（2026-09-22追加）。前回セッション復元・参照専用追加・消去ボタン・tecsgenオプションファイル読込・import自動追跡との統一（第11章11.2節#7〜#11、全項目決定・実装済み。2026-09-22実装コミット`829efc7`・`e0e2c26`・`7c0318d`）
8. [[TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計]] 既存診断を集約。複合セルタイプの未対応構文通知は03Bで定める
9. [[TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計]] — Electron固有化。`child_process`（tecsgen・Cプリプロセッサ実行）をmainプロセスに置き、`TecsgenGateway`でIPC経由公開
   - [[TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計]] — 9.6節が名前を挙げていた`CdeclExtractor`（モジュールB、typedef/struct抽出）自体の設計・実装（2026-09-23、同日中に設計・実装完了）。文法ローダ・型モデル・CST走査アルゴリズム
   - [[TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計 — 実装時の差分]] — 上記の実装時に判明した8件の差分（サテライト、2026-09-23）
10. [[TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧]] — main/renderer/preloadのディレクトリ構成とIPCチャネル一覧
11. [[TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案]]
   - [[TECSCDE-DT-EL内部仕様 - 11B 配布方式の候補（署名・パッケージング）]] — 11.2.1〜11.2.3（コード署名候補・macOS/Linuxパッケージング方式）（サテライト、2026-10-10）

## 実装（TECSCDE-DT-EL実装）との相違点・確定事項

実機（Electron 44）起動検証およびヘッドレス契約テストの過程で判明した仕様との相違点と確定事項（詳細は各章および第11章11.5節参照）。

1. **`PasteCommand` の非同期クリップボード対応（第4章）**:
   - Electron 44 の `clipboard.readText()` は非同期（`Promise<string>`）であるのに対し、`Command.apply()` は純粋同期処理。そのため `PasteCommand` は `ClipboardGateway` を持たず、事前に解決されたテキスト文字列（`string | undefined`）を受け取る設計に変更（[[work/active/tecs/TECSCDE-DT-EL PasteCommand非同期クリップボード決定|決定記録]]）。
2. **`CutCommand` 副作用の UI 層移動（第4章）**:
   - `History` の replay 機構（`past` 再生）と整合させるため、クリップボード書き込み副作用を `apply()` からコマンド発行前の `AppStore.cutSelection` へ移動し、`CutCommand.apply()` は純粋な削除のみを行う。
3. **`HitTester` / `GestureController` の疎結合化（第5章）**:
   - `HitTester` は `SvgRenderer` ではなく `CanvasView`（ズーム比率のみ）を受け取り、`GestureController` は DOM リスナ登録を明示的な `attach(svg)` に分離してヘッドレス検証を可能にした。
4. **パンの HTML スクロールコンテナ実現（第6章）**:
   - パンは SVG 変形ではなく、シェル側のスクロールコンテナ（`pan-scroll.ts`、`panCenter`(mm) ⇔ `scrollLeft/Top`(px)）で実現。
5. **UI シェルの Electron 特化設計（第2章 / 第10章）**:
   - TS版の汎用 `UiComponent` ライフサイクル抽象クラス階層を挟まず、`AppShell` と各専用ビュー（`PaletteView`, `PropertyPanelView` 等）が `AppStore`・DOM/IPC に直接結合する構成を採用。
6. **Preload の ESM 化と `sandbox: false`（第2章 / 第11章）**:
   - Preload を ESM（`.mjs`）で書き `createRequire` で `clipboard` を取得するため、`sandbox: false` を確定（`contextIsolation: true` は維持、[[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定|決定記録]]）。
7. **tree-sitter WASM の Main プロセス経由 IPC ロード（第2章 / 第7章）**:
   - renderer からの `file://` fetch が CORS でブロックされるため、Main プロセスが `fs` で WASM バイナリを読み込み、IPC 経由で renderer へバイト列を渡して初期化。
8. **起動時初期ドキュメントのプッシュ供給（第7章）**:
   - Main プロセスが `did-finish-load` 後に `app:bootstrap` IPC で初期ドキュメントのソーステキスト群を 1 回だけプッシュ供給する方式を採用。

## Related

- [[TECSCDE-DT-EL実装]] — 本書に基づく実装の進捗ノート（2026-09-06着手）
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]] — 本書が実装する外部仕様（デスクトップ版）
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様]] — 姉妹文書（Tauri・Rust）。同じ外部仕様・同じモジュール分割から出発するが、言語・プロセスモデルの違いにより設計が分岐する
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]] — 本書が踏襲するクラス設計の一次情報源（ブラウザ版）
- [[TECSCDE内部仕様]] — さらに元となる関数/インタフェースベースの内部仕様（ブラウザ版）
- [[TECSCDE-JS-TS実装]] — ブラウザ版の実際の実装（本書はこれとは別系統）
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体
- [[North Star]] — 🔴最優先事項としてのTECSCDE JS版実装（本書はデスクトップ・Electron版という別ラインの検討）

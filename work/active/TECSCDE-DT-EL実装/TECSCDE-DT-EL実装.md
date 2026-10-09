---
date: 2026-09-06
description: "TECSCDE-DT-EL内部仕様（Electron・クラスベース）の実装進捗ノート。11.4節の3実装単位＋preload ESM化＋第4章（4.1節Copy/Cut/Paste＋キーボード配線含む）＋第5章（描画）＋第6章（表示制御）＋モジュールG（最小UIシェル＋次段のパレット/プロパティパネル/検索ボックス/ナビゲータ/診断パネル、esbuild+実機起動確認）＋モジュールH（診断集約）＋第9章（9.4 TecsgenResultParser、9.5 Generate操作配線、9.6 import_Cプリプロセス配線）まで完了。Electron Forge導入（package/make、Node 22 LTS実行が前提）、package/make後（asar化後）の実機起動確認（electron-squirrel-startup依存配置バグ修正込み）も完了。2026-09-16、手書きlexer/parserをtree-sitter（`web-tree-sitter`＋WASM）へ移行。2026-09-20、初の実機対話的確認を4ラウンド実施し、PropertyPanelView編集消失・CSP・起動サンプル順・保存インジケータ・既定メニューによるCtrl+C/X/V横取り・clipboard未定義・Generate後の診断視認性の計7件のバグを発見・修正してpush済み。279テストpass。2026-09-23、配布の仕組み（[[work/active/tecs/TECSCDE-DT-EL 配布アーキテクチャ決定|配布アーキテクチャ決定]]: publisher-github・update-electron-app・GitHub Actionsワークフロー・README更新）を実装、ローカルコミット済み（未push・未タグ作成）。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - implementation
---

# TECSCDE-DT-EL実装

## Context

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]]（Electron・クラスベース設計、全11章執筆完了 2026-09-05）に対応する実装。
- 対象ローカルリポジトリ: `E:\Ccur\typescript\TECSCDE-DT-EL`（[[TECSCDE-JS-TS実装]]の`E:\Ccur\typescript\TECSCDE-JS`（旧称`TECSCDE`）、[[TECSCDE-TS実装]]の`E:\Ccur\typescript\TECSCDE-TS`とは別リポジトリ）。2026-09-06に`git init`。
- 対象リモートリポジトリ: `origin`が`https://github.com/toppers/tecscde-dt-el`（TOPPERS組織のフォーク、実際のpush先）、`upstream`が`https://github.com/ykominami/tecscde-dt-el`（非公開、2026-09-11作成、README等の初期化なし、[[TECSCDE-TS実装]]に倣った命名）。ローカル`main`は`origin`へpush済み（2026-09-16確認、`26d8ddc`まで）。

## Notes

日付つきの実装エントリ（2026-09-06〜、モジュールごとの実装記録・テスト状況・実機起動確認）は
[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Progress Log|TECSCDE-DT-EL実装 — Progress Log]] に分離（2026-09-10、25KB閾値）。

**現在の到達点（2026-09-13）**: 11.4節の3実装単位（model+CDL round trip・IPCゲートウェイ契約テスト・第4章 Command/History）＋ preload ESM化（[[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定|決定記録]]、11.2節#1）＋第5章（描画・インタラクション `render/`）＋第6章（表示制御 `view-state/`）＋モジュールG（最小UIシェル `app/`、esbuild バンドル・実機 `electron .` クリーン起動）＋モジュールH（診断集約 `diagnostics/` の `DiagnosticsCollector`/`DiagnosticReport`/`checkIntegrity`、パネルUI配線込み）＋第4章4.1節（`CopyCommand`/`CutCommand`/`PasteCommand`、`cdl/fragment.ts`のCDL断片シリアライズ/パース、2026-09-11）＋モジュールGへのCtrl+C/X/Vキーボード配線（`AppStore`のアプリ内クリップボード、2026-09-11）＋モジュールG次段（パレット／プロパティパネル／検索ボックス／ナビゲータパネル、2026-09-11）＋第9章9.4節`TecsgenResultParser`（2026-09-11）＋第9章9.5節Generate操作配線＋`TecsgenCommandBuilder`新設（2026-09-11）＋第8章8.4節診断パネルUI配線（`DiagnosticsPanelView`、2026-09-12）＋第9章9.6節`import_C`プリプロセス実行とフォールバック配線（`TecsgenRunner.preprocess`／`tecsgen:preprocess` IPCチャネル／`TecscdeApi.tecsgen.preprocess` preload／`TecsgenGateway.preprocess`、2026-09-13）まで完了。**188テスト全pass**、`npm run check`（typecheck:renderer + esbuild + build:main + test + depcruise）green。

## Action Items

2026-09-06〜09-15分は[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Action Items — 2026-09-06〜09-15|Action Items — 2026-09-06〜09-15]]に分離（2026-09-21、25KB閾値）。09-16〜09-21分は[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Action Items — 2026-09-16〜09-21|Action Items — 2026-09-16〜09-21]]に分離（2026-09-21、コア再肥大化）。以下は09-21以降の未分類項目。

- [x] ツールバーのズームUI（−/100%/＋ボタン）の外部仕様3.2.1スライダ規定からの逸脱（[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Action Items — 2026-09-16〜09-21|09-16〜09-21分]]参照）を解消——整数値スライダ（`min=5 max=200 step=1`）を追加（コミット`06f2c25`）した上でユーザーが使用感を比較し、`−`/`＋`ボタンを削除して「100%」ボタンを「Reset Rate」に改称、スライダへ一本化（コミット`43268b4`、いずれも2026-09-21）。設計記録は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|内部仕様11.5節#9]]参照
- [x] [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計|第7B章]]（ファイルブラウザ基本設計）・[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|第7C章]]#7（前回セッション復元）・#9（消去ボタン）を実装（2026-09-22、コミット`829efc7`、238テストpass）
- [x] [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|第7D章]]・[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章]]（§7.5 import自動追跡）を実装——`FileService.resolveImports()`・`resolveAllImports()`（新規`import-resolution.ts`）・`applyOpenResult`統合（2026-09-22、コミット`e0e2c26`、252テストpass）
- [x] [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|第7C章]]#8（参照専用追加）・#10（tecsgen-optsファイル一括読込）・#11（import統一）を実装——`addAsReference`・`loadOptionsFile`・`FileService.parseTecsgenOptionsFile`・ツリーの参照ハイライト（2026-09-22、コミット`7c0318d`、268テストpass）。第7C章全項目（#7〜#11）の実装が完了
- [x] [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|第9B章]]`CdeclExtractor`（`import_C`のtypedef/struct抽出）を設計・実装——`src/renderer/cdecl/{grammar,types,extractor}.ts`新規、`import-resolution.ts`の`resolveImportClosure`へ統合、`tecsgenGateway`を`file-actions.ts`・`main.ts`・`shell.ts`まで橋渡し（2026-09-23、コミット`8e920f0`、279テストpass）。実装中に2件の実バグを発見・修正——①`CdlGrammar.init()`/`CdeclGrammar.init()`の並列実行がweb-tree-sitterのグローバルランタイム初期化を競合させる問題（逐次awaitへ変更）、②実際の文法では`struct_declarator`の`declarator`子にフィールド名が付与されない問題（`namedChildren`から型名検索へ変更）。詳細は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計 — 実装時の差分|実装時の差分]]参照
- [x] 配布実装（[[work/active/tecs/TECSCDE-DT-EL 配布アーキテクチャ決定|配布アーキテクチャ決定]]、2026-09-23）——①`forge.config.js`に`@electron-forge/publisher-github`を追加、origin自身（`toppers/tecscde-dt-el`）をpublish先に指定（`draft: true`で自動公開はしない安全側の既定） ②`.github/workflows/release.yml`新設（`v*`タグトリガー、Node 22固定、`windows-latest`、`npm run check`→`electron-forge publish`、認証は既定`GITHUB_TOKEN`） ③`update-electron-app`導入、`src/main/index.ts`起動時に呼び出し ④README更新（実機起動・279テストの検証済み状態を反映、インストール／自動更新手順を追記）。**実装過程で`.gitignore`の`.github/`一律除外（`.claude/`等と同枠のAIツール除外だった）がワークフローファイルのコミットを妨げると判明し、`.github/copilot-instructions.md`・`hooks/`・`instructions/`のみへnarrow**——このリポジトリでは初めて`.github/workflows/`を使う前提修正だった。`electron-forge package`でasar化後も`update-electron-app`が正しく同梱されること（`dependencies`配置）を確認済み。ローカルコミット済み（未push、未タグ作成——実際のリリース発行は別途判断）
- [x] 自動更新の実機確認（2026-09-24）——`package.json` に `repository`（`https://github.com/toppers/tecscde-dt-el.git`）が欠落していたため `guessRepo()` で例外が発生するリスクを特定・解消（`package.json` への `repository` 追加および `src/main/index.ts` での `updateElectronApp({ repo: "toppers/tecscde-dt-el", logger: console })` 明示指定、コミット `be43cb1`）。`update.electronjs.org` への疎通（404 No updates found で正常待機）、`npm run forge:package` 後の実機バイナリ（`out/tecscde-dt-el-win32-x64/tecscde-dt-el.exe`）起動、および 279 テスト全 pass（`npm run check` green）を確認。
- [ ] リリース発行後の自動更新実動テスト（通知ダイアログ表示と更新適用）——初回リリースタグ（例: `v0.1.0`）発行後、次バージョン（`v0.1.1`等）公開時に実機アプリを起動し、`makeUserNotifier` による通知ダイアログ表示および `quitAndInstall()` によるインプレース更新が正常完了するかを検証する（ユーザー承諾済み、リリース作業時に自動組み込み）。

## Related
- [[work/active/tecs/TECSCDE-DT-EL 複合セルタイプ対応案|TECSCDE-DT-EL 複合セルタイプ対応案]] 複合セルタイプ対応の方針（2026-10-03採用。表示・編集範囲は外部仕様で決める）

- [[work/active/tecs/TECSCDE-DT-EL 配布アーキテクチャ決定|TECSCDE-DT-EL 配布アーキテクチャ決定]] — 配布専用ミラーリポジトリ＋update-electron-app＋GitHub Actionsの決定記録（2026-09-23、実装は未着手）
- [[work/active/tecs/Electronアプリのコード署名|Electronアプリのコード署名]] — コード署名の仕組みと設定箇所の参考ノート（11.2節#2、現状は未署名）
- [[work/active/tecs/Electronアプリの配布・自動更新ツール|Electronアプリの配布・自動更新ツール]] — パッケージング・自動更新ツール比較（Electron Forge採用の背景）
- [[work/active/tecs/Electron Forgeの使い方|Electron Forgeの使い方]] — Forgeの一般的な使い方と、本実装で実際に採った構成の差分
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]] — 本実装が対応する内部仕様（全11章）
- [[work/active/tecs/TECSCDE-DT-EL ズーム・パン対話的確認チェックリスト|TECSCDE-DT-EL ズーム・パン対話的確認チェックリスト]] — SVG幾何・ズーム/パンの対話的目視確認用チェックリスト（ズーム項目は2026-09-21確認・修正済み）
- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 07 表示機能|TECSCDE外部仕様7章（表示機能）]] — Ctrl+ホイールのポインタ固定点ズーム・「左上基準でずれる」旧版バグの禁止を規定する一次情報源
- [[TECSCDE-TS実装]] — model/cdl/diagnosticsの移植元
- [[TECSCDE-JS-TS実装]] — 現行の関数ベース・ブラウザ版実装（比較対象）
- [[work/active/TECSCDE共通ロジック/TECSCDE共通ロジック|TECSCDE共通ロジック]] — 本実装と[[TECSCDE-JS-TS実装]]が共有するロジックの棚卸しと共有方法の未決事項
- [[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定|TECSCDE-DT-EL preload ESM・sandbox決定]] — 実機起動確認で判明したpreloadのESM/CJS不整合への対応（`sandbox: false`確定）
- [[work/active/tecs/TECSCDE-DT-EL PasteCommand非同期クリップボード決定|TECSCDE-DT-EL PasteCommand非同期クリップボード決定]] — 第4章4.1節実装で判明した`ClipboardGateway.readText()`の非同期化と`Command.apply()`の同期性の不整合への対応
- [[TECSCDE-DT-TA実装]] — 姉妹実装（Tauri・Rust）。2026-09-07リポジトリ初期化、本ノートを進め方の先例にしている
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]] — 本実装が実現する外部仕様（デスクトップ版）
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]] — 第5・6章のクラス表現の正典
- [[perf/competencies/ソフトウェアアーキテクチャ|ソフトウェアアーキテクチャ]] — クラス階層・main/renderer/preloadのプロセス境界・依存方向の機械的強制
- [[North Star]] — 本ラインが🔴最優先（DT-EL版の内部仕様・実装への移行）。[[TECSCDE-JS-TS実装]]（関数ベース）は現行実装として維持しつつ、クラスベース設計の検証は本実装で前進させる

## 2026-09-16以降の詳細ログ

tree-sitter移行・`TecsgenCommandBuilder`の`-I`誤り訂正・未コミット作業の整理（いずれも2026-09-16）は
[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Progress Log — 2026-09-16〜|TECSCDE-DT-EL実装 — Progress Log — 2026-09-16〜]]
に分離（2026-09-20、25KB閾値）。

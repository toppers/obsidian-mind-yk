---
date: 2026-09-06
description: "TECSCDE-DT-EL内部仕様（Electron・クラスベース）の実装進捗ノート。11.4節の3実装単位＋preload ESM化＋第4章（4.1節Copy/Cut/Paste＋キーボード配線含む）＋第5章（描画）＋第6章（表示制御）＋モジュールG（最小UIシェル＋次段のパレット/プロパティパネル/検索ボックス/ナビゲータ/診断パネル、esbuild+実機起動確認）＋モジュールH（診断集約）＋第9章（9.4 TecsgenResultParser、9.5 Generate操作配線、9.6 import_Cプリプロセス配線）まで完了、188テストpass。Electron Forge導入（package/make、Node 22 LTS実行が前提）も完了。"
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
- 対象ローカルリポジトリ: `E:\Ccur\typescript\TECSCDE-DT-EL`（[[TECSCDE-JS-TS実装]]の`E:\Ccur\typescript\TECSCDE`、[[TECSCDE-TS実装]]の`E:\Ccur\typescript\TECSCDE-TS`とは別リポジトリ）。2026-09-06に`git init`。
- 対象リモートリポジトリ: https://github.com/ykominami/tecscde-dt-el（非公開、2026-09-11作成、README等の初期化なし、[[TECSCDE-TS実装]]に倣った命名）。ローカル`main`をpush済み（`5c04939`まで）。

## Notes

日付つきの実装エントリ（2026-09-06〜、モジュールごとの実装記録・テスト状況・実機起動確認）は
[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Progress Log|TECSCDE-DT-EL実装 — Progress Log]] に分離（2026-09-10、25KB閾値）。

**現在の到達点（2026-09-13）**: 11.4節の3実装単位（model+CDL round trip・IPCゲートウェイ契約テスト・第4章 Command/History）＋ preload ESM化（[[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定|決定記録]]、11.2節#1）＋第5章（描画・インタラクション `render/`）＋第6章（表示制御 `view-state/`）＋モジュールG（最小UIシェル `app/`、esbuild バンドル・実機 `electron .` クリーン起動）＋モジュールH（診断集約 `diagnostics/` の `DiagnosticsCollector`/`DiagnosticReport`/`checkIntegrity`、パネルUI配線込み）＋第4章4.1節（`CopyCommand`/`CutCommand`/`PasteCommand`、`cdl/fragment.ts`のCDL断片シリアライズ/パース、2026-09-11）＋モジュールGへのCtrl+C/X/Vキーボード配線（`AppStore`のアプリ内クリップボード、2026-09-11）＋モジュールG次段（パレット／プロパティパネル／検索ボックス／ナビゲータパネル、2026-09-11）＋第9章9.4節`TecsgenResultParser`（2026-09-11）＋第9章9.5節Generate操作配線＋`TecsgenCommandBuilder`新設（2026-09-11）＋第8章8.4節診断パネルUI配線（`DiagnosticsPanelView`、2026-09-12）＋第9章9.6節`import_C`プリプロセス実行とフォールバック配線（`TecsgenRunner.preprocess`／`tecsgen:preprocess` IPCチャネル／`TecscdeApi.tecsgen.preprocess` preload／`TecsgenGateway.preprocess`、2026-09-13）まで完了。**188テスト全pass**、`npm run check`（typecheck:renderer + esbuild + build:main + test + depcruise）green。

## Action Items

- [x] モデル＋CDLパーサ/シリアライザのround trip（[[TECSCDE-TS実装]]から移植）
- [x] IPCゲートウェイの疎通確認（契約テストとして、実機起動なしで実施）
- [x] 第4章: `Command`抽象クラス・`History`クラス・主要コマンド群（セル/結合/ポート）（2026-09-07、コミット`0b753e7`）
- [x] 実際に`electron .`を起動して確認する（2026-09-08、Electron 44で起動成功・4プロセス構成を確認。renderer未ビルドとpreloadのESM/CJS不整合は下記2項目へ）
- [x] preloadのESM/CJS不整合を解消する（2026-09-08、ESM `.mjs` + `sandbox: false`を採用。[[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定|決定記録]]、11.2節#1確定）
- [x] 第4章4.1節: `CopyCommand`/`CutCommand`/`PasteCommand`とOSクリップボード連携（2026-09-11、コミット`0e79b3e`）。`serializeCellsAsCdl`／`tryParseCdlFragment`（`cdl/fragment.ts`）を新設し、`cell`ブロックのみ（位置・結合は含まない）を断片化。実装中に判明した設計上の齟齬: 実装済み`ClipboardGateway.readText()`は`Promise<string>`（Electron 44のclipboardモジュール自体が非同期化）だが`Command.apply()`は同期のため、`PasteCommand`はOSクリップボードの読み取り済みテキストを渡される形に変更（読み取り自体は将来のAppStore側の責務、[[work/active/tecs/TECSCDE-DT-EL PasteCommand非同期クリップボード決定|決定記録]]）。132テスト全pass、`npm run check`green。UI配線（キーボードショートカット・アプリ内クリップボード状態の保持）は未着手で、下記モジュールG次段と合流する。
- [x] 第5章: 描画（SVG）・インタラクション — クラス一式（`src/renderer/render/` 8ファイル）＋ヘッドレステスト20件（2026-09-09）。SVG描画クラスは型チェックのみ、実挙動検証はモジュールG待ち
- [x] 第6章: 表示制御（`ViewState`／`DisplayFilters`／ナビゲータ／検索） — `src/renderer/view-state/` 5ファイル＋ヘッドレステスト23件（2026-09-09）。第5章の暫定`CanvasView`は`ViewState.toCanvasView()`の射影先として残置（モジュールG実装時に配線）
- [x] [[TECSCDE-TS実装]]第6章へ本実装を写す（2026-09-11、第5章・モジュールHと合わせて実施。詳細は[[TECSCDE-TS実装]]側のNotesを参照）
- [x] UIシェル（モジュールG） — 最小スコープで実装（2026-09-10、esbuild バンドル＋実機 `electron .` 起動確認＋happy-dom 配線テスト18件）
- [x] `ViewState`のズーム/パンの実DOM配線（`pan-scroll.ts` の `panCenter` ⇔ scrollLeft/Top、`shell.ts` の scroll/wheel ハンドラ）。※対話的な目視（ズーム固定点・スクロール連動の見た目）は次回 `electron .` で
- [x] `SvgRenderer`／`GestureController`の実DOM起動確認（`electron .` で描画ツリー生成を確認。ドラッグ・結合作成の対話的目視は次回）
- [x] モジュールGへのキーボードショートカット配線（Ctrl+C/X/V、2026-09-11、コミット`e4e7484`）。`AppStore`に`copySelection`/`cutSelection`/`pasteClipboard`とアプリ内クリップボード（`Cell`スナップショット、外部仕様6.7.2の優先順位）を追加。配線中に発見したバグ: `CutCommand.apply()`がOSクリップボードへの書き込みを副作用として持っていたが、`History.current`は`past`を毎回`initial`から再生する（4.3節）ため、`current`を読むたび（=ほぼ毎回のrender）に書き込みが再実行されてしまう構造だった。書き込みを`AppStore.cutSelection`側（dispatch前に1回）へ移し、`CutCommand.apply()`は`DeleteCommand`と同じ純粋な削除のみに修正。137テスト全pass
- [x] モジュールG次段: パレット／プロパティパネル／検索ボックス／ナビゲータパネル（2026-09-11、コミット`67ad15f`）。4つとも専用クラス（`app/palette.ts`・`property-panel.ts`・`search-box.ts`・`navigator-panel.ts`）としてAppShellから薄く配線。旧ツールバーの`<select>`＋チェックボックスはPaletteへ置き換え。regionフィールドは読み取り専用（RegionTreeがROOTのみのため）。配線中に発見したバグ: PaletteViewの初期セルタイプ自動選択が自身のDOM構築完了前に`store.notify()`を誘発し、再入したrender()と元の呼び出しの両方がセルタイプ一覧を追加して二重表示になっていた（`return`で即座に抜ける形に修正）。ついでにshell.ts内の無関係な既存破損（2026-09-10のスキャフォールド由来、文字列リテラル内のNULバイト1個——grepがバイナリ扱いしていた原因）も発見・除去。150テスト全pass、`electron .`起動確認（エラーなし）。ナビゲータのクリック→パン変換のピクセル演算はhappy-domがレイアウトを持たないため自動テスト対象外（第5章のSVG幾何確認と同じ方針）
- [x] [[TECSCDE-TS実装]]第5章へ本実装を移す（2026-09-11。第4章`commands/`が第5章`gesture-controller.ts`の直接依存のため合わせて移植、モジュールGはElectron専用AppShellとTS内部仕様の`UiComponent`設計が異なるため今回は見送り）
- [x] 第9章9.4節: `TecsgenResultParser`（tecsgen実行結果→`Diagnostic[]`変換、2026-09-11、コミット`9933003`）。DT-EL側で先行実装——外部仕様9.1.1・9.3.1の固定書式（`<file>:<line>:<col>: error|warning: <message>`、位置情報なしは`error|warning: <message>`）を解析し、メッセージ先頭のG-code/S-codeを`Diagnostic.code`へ分離。書式に一致しない行（tecsgenの通常出力）は診断化せず読み飛ばす。実行ファイル自体が無い場合は`E-TECSGEN-NOT-FOUND`1件のみ返す。160テスト全pass。スコープは9.4のみ——9.1〜9.3（`TecsgenRunner`/IPC/`TecsgenGateway`）は既存実装済み、9.5（モジュールGからの「実行」トリガー配線）と`TecsgenCommandBuilder`（コマンド文字列組み立て、いずれのリポジトリにも未実装）は次段
- [x] 第9章9.5節: モジュールGからtecsgen「実行(Generate)」操作を配線（2026-09-11、コミット`5c04939`）。前提だった`TecsgenCommandBuilder`（`tecsgen/command-builder.ts`、外部仕様8.4.2の`-I <base_dir> -I <import_path…> -D <macro…> <参照専用ファイル…> <編集対象ファイル>`）も新設。**（2026-09-14 追記）** 当時準拠した外部仕様8.4.2の例は誤りだったと判明（[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携#8.4.2 JS 版の規定]]参照、`-I`はbase_dir用ではなく`base_dir`に対応するCLIオプションは存在しない）。[[TECSCDE-TS実装]]側の`TecsgenCommandBuilder`は同日中に訂正済みだが、本リポジトリ（`tecsgen/command-builder.ts`）は未確認・未修正のまま残っている——次回このコードに触る際に要対応。実装中に判明した構造的な欠落: 参照専用ファイルの実パスは`applyOpenResult`が`baseName()`で切り詰めていたため`TecscdeDocument.referenceFiles`にはbasenameしか残らず、`execFile`に渡せる実パスがどこにも保持されていなかった。`AppStore`に`referenceFilePaths`（`loadDocument`経由）を追加し解消。tecsgenはディスク上のファイルを読むため、dirty状態なら生成前に自動保存（`file-actions.save()`再利用）。二重起動防止は`AppStore.isGenerating`でツールバーボタンを無効化。外部仕様8.4.2の「実行に加えてコマンドの提示・コピーも残す」は`tecsgenCommandLine()`＋2つ目のツールバーボタンでOSクリップボードへコピーする形で実現。183テスト全pass、`electron .`起動確認（エラーなし）
- [x] リモートリポジトリの作成（2026-09-11、https://github.com/ykominami/tecscde-dt-el、非公開、`gh repo create`で作成しローカル`main`をpush）
- [x] 第8章8.4節: 診断パネルのUI配線（2026-09-12）。`AppStore.getReport()`はステータスバーに件数を出すのみでUIから一覧を見る手段が無いままだった（`/om-wrap-up`で発見）。`DiagnosticsPanelView`（`app/diagnostics-panel.ts`）を新設し、ステータスバーの件数表示を`<button>`化してトグル、一覧パネルを表示。`relatedCellId`/`relatedJoinId`を持つ診断は第6章6.4節の検索ジャンプ機構と同じ操作（選択＋パン）を再利用し専用ハイライトは新設せず（8.4節どおり）、`location`のみの診断は`file:line:column`の提示に留める。185テスト全pass、`npm run check`green、`electron .`起動確認（エラーなし）
- [x] 第9章9.6節: `import_C`プリプロセス実行とフォールバック配線（2026-09-13）。外部仕様・内部仕様の改訂に追随し、Cプリプロセッサ実行（`gcc -E -DTECSGEN` または `__tool_info__("tecsgen")` の `cpp` オプション）をMainプロセスに委譲する `TecsgenRunner.preprocess`／`tecsgen:preprocess` IPCチャネル／preloadの `TecscdeApi.tecsgen.preprocess`／`TecsgenGateway.preprocess` を配線。プリプロセッサ未検出（`executableFound: false`）や異常終了（`exitCode !== 0`）時にもクラッシュさせず `W-CPP-FALLBACK` 警告を安全にキューイング可能とする基盤を構築。新規3テスト追加で全188テストpass、`npm run check`green
- [x] Electron Forgeの導入（2026-09-12、11.2節#2「配布・自動更新・コード署名」のうち配布ツールの選定を一部解消。公開(publish)・自動更新・コード署名・macOS/Linux Makerは範囲外のまま未決）。`@electron-forge/cli`・`@electron-forge/maker-squirrel`・`electron-squirrel-startup`を追加、`forge.config.js`のprePackageフックで既存`npm run build`（tsc+esbuild）をそのまま再利用、`main/index.ts`にSquirrel早期終了ガード（`createRequire`経由、preloadと同型パターン）を追加。`npm run forge:package`/`forge:make`を新設（既存の`start`/`build`/`test`/`check`は変更なし）。導入中に3件の環境要因を発見・解消:
  1. **`@electron/rebuild@3.x`（`@electron-forge/core`の依存）がgit参照の`@electron/node-gyp`フォークに依存**しており、このリポジトリのサンドボックス環境はgitプロトコルでの依存取得を禁止しているためインストールが失敗（`EALLOWGIT`）。`@electron/rebuild@4.x`はレジストリ配布の`node-gyp`のみに依存するため、`package.json`の`overrides`で`"@electron/rebuild": "^4.0.0"`に固定して解消。
  2. **`electron-winstaller@5.4.4`の`script/select-7z-arch.js`に上流バグ**（`os.arch`が関数呼び出し`()`忘れのまま文字列結合されており`vendor/7z.exe`/`7z.dll`を生成できない）があり、Squirrel.exe（`CreateZipFromDirectory`）が7z.exeを見つけられず`System.ComponentModel.Win32Exception`で`make`が失敗。`scripts/fix-electron-winstaller-7z.mjs`（`os.arch()`で正しくコピーし直す）を新設し、`postinstall`スクリプトとして配線——`npm install`のたびに自己修復する。
  3. **`@electron/packager`がこのリポジトリの既定Node（v26.8.1、mise管理）で無期限にハングする**（Forge経由・素の`packager()`直接呼び出し、Windows/Linuxターゲットいずれでも再現——Node自身の「unsettled top-level await」検出が働きexit code 13で強制終了。プラットフォーム非依存の再現のためrcedit等のWindows固有処理が原因ではない）。同じ環境の`mise`管理下にあるNode 22.23.2 LTSで実行したところ正常終了（`electron-forge make`が`out/make/squirrel.windows/x64/tecscde-dt-el-0.1.0 Setup.exe`を生成、実行時間約38秒）。**`npm run forge:package`/`forge:make`は現状Node 22 LTS実行が前提**——既定のNode 26では`@electron/packager`側のNode 26未対応（と見られる）バグでハングする。開発用の`npm start`（`electron .`）自体はNode 26のままで問題なし（Electron本体の実行であり`@electron/packager`を経由しないため）。
- [ ] **package/make後（asar化後）の実機起動確認は未実施**。`electron-forge make`がSetup.exeを生成することは確認したが、実際にインストール/`out/.../tecscde-dt-el.exe`を起動してレンダラ・preload（ESM `.mjs`）・`contextBridge`が動作するかは未検証。preloadのESM/`sandbox: false`設定（[[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定|決定記録]]）はasar化でファイルパス解決が変わる可能性があり、開発時の`electron .`起動確認とは別に確認が必要（[[work/active/tecs/Electron Forgeの使い方|Electron Forgeの使い方]]参照）

## Related

- [[work/active/tecs/Electronアプリのコード署名|Electronアプリのコード署名]] — コード署名の仕組みと設定箇所の参考ノート（11.2節#2、現状は未署名）
- [[work/active/tecs/Electronアプリの配布・自動更新ツール|Electronアプリの配布・自動更新ツール]] — パッケージング・自動更新ツール比較（Electron Forge採用の背景）
- [[work/active/tecs/Electron Forgeの使い方|Electron Forgeの使い方]] — Forgeの一般的な使い方と、本実装で実際に採った構成の差分
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]] — 本実装が対応する内部仕様（全11章）
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
- [[North Star]] — 🔴最優先事項としてのTECSCDE JS版実装（本実装は代替設計の検証であり、最優先ラインそのものではない）

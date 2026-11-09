---
date: 2026-09-06
description: "TECSCDE-DT-EL内部仕様（Electron・クラスベース）の実装進捗ノート。実装単位・Forge配布・tree-sitter移行・実機確認・配布アーキテクチャの進捗と、発見したバグを記録する。"
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

日付つきの実装エントリ（2026-09-06〜、モジュールごとの実装記録・テスト状況・実機起動確認）は[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Progress Log|TECSCDE-DT-EL実装 — Progress Log]] に分離（2026-09-10、25KB閾値）。

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
- [x] ウィンドウを閉じるときの未保存確認を実装する（2026-10-22実装、実機で確認済み、出典は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|7.9]]）——実機で、未保存の変更があっても確認なしに終了することを確認した。`CloseGuard`（main）の追加、`window:setDirty`のIPCとpreload公開、`AppShell`の`bindBeforeUnload`の廃止とストア購読への置き換え、テスト。
- [ ] CDLパーサの実装を読んで気づいた点（2026-10-21、出典は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 04B CDLパーサ設計|4B]]の4B.10節。**読解のみで動作は未確認**）——実装の修正か仕様側の整理かは未決:
  - [x] ①（**解消、2026-10-22**: `require`を拾う処理を追加。名前つきは通常の呼び口、名前なしは隠れた呼び口として警告）`isRequire`が常に`false`で、`hiddenRequirePortCount`が常に0（`cdl/cst.ts`の`collectPort`と`collectCelltype`が`require`を拾わない）。`W-REQUIRE-PORT-HIDDEN`が出ない可能性。まず`require`を含むCDLで確かめる
  - [x] ②（**解消、2026-10-22**: 関数`compositeUnsupported`を削除。コード定数はテスト用に残す）`W-COMPOSITE-UNSUPPORTED`／`compositeUnsupported()`は`cdl/messages.ts`に定義だけ残り、呼び出しが`src`に無い。仕様（DT外部仕様4.7・9章、DT-EL第8章・3B.5）は警告にしないと定めて**決着済み**なので、コードを削除する
  - [x] ③（**解消、2026-10-22**: `visitNested`に統合）`cdl/cst.ts`の`build`のトップレベル`switch`と`visitNested`の`switch`の重複（`signature`の修飾規則もずれる）。統合を検討
  - [x] ④（**解消、2026-10-22**: `W_CODES`に集約）`W-C-TYPE-UNRESOLVED`・`W-PORT-SIGNATURE-UNRESOLVED`・`W-REGION-MISMATCH`が`messages.ts`の`W_CODES`に無く`document-builder.ts`に直書き
  - [x] ⑤（**解消、2026-10-22**）`CdlDocumentLoader.loadSources`のドキュメントコメントが「編集対象ファイルのcellのみeditable=true」のまま古い（現行は呼び出し側が`editable`を決め、通常CDLは全て編集可能）
  - [x] ⑥（**解消、2026-10-22**: 主要なファイルにDT-EL内部仕様04Bへの参照を追加）各ソースの先頭コメントがTS版の章番号を指す（DT-ELの章との対応は4Bに記載）
- [ ] tecsgen起動失敗の診断で外部仕様と食い違う点（2026-10-21、出典は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|9.7]]。**読解のみ、動作は未確認**）:
  - [x] ①`ENOENT`以外の起動失敗（権限なし・タイムアウト・出力過多など）を、`TecsgenResult.launchFailure`で種類別に表し、Generate経路・Plugin型の取り込み経路ともエラー／警告にする（2026-10-22、9.7節。非0終了でエラー行が無い場合の`E-TECSGEN-FAILED`も追加）
  - [x] ②Generateの`timeout`30秒・既定`maxBuffer`がPlugin型の取り込み（120秒・16MiB）より小さい。大量の進捗出力で失敗しないかを確認する——2026-10-22に決定: 上限は変更しない（Generate は30秒・既定 `maxBuffer` のまま）。実測はしない。超過した場合は `E-TECSGEN-TIMEOUT`／`E-TECSGEN-OUTPUT-OVERFLOW` として提示されるため、実際に問題が出てから見直す。
  - [x] ③`TECSGEN_COMMAND`の文言は直し、外部仕様2.4節・8.4.2節に規定を追加した。`E-TECSGEN-*`・`W-PLUGIN-TYPE-LOAD`・`W-TECSGEN-VERSION-*`は外部仕様9.4節に一覧を載せた（2026-10-22）
- [ ] `-k`の扱い（2026-10-21、出典は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|第9章冒頭の注記]]。**読解のみ、動作は未確認**）: ①（**解消、2026-10-22**: オプションファイルに`-k`が無ければ`-k utf8`を足す。`-k`があればその値を尊重する）`.tecsgen-opts`経由のPlugin型の取り込みで`-k utf8`が付かない（`TecsgenRunner.generatedTypes`がオプションファイルの原文を渡す）。`-k`がファイルに無い場合のtecsgenの既定は`euc`で、UTF-8のCDLを正しく読めるか確かめる。付けるなら、ファイルに`-k`があればそれを尊重するかを決める ②DT-TA内部仕様第9章には`-k`の記述が無い（DT-ELで見つかった欠落と同じものが起きないか）
- [ ] 入力の文字コードの残課題（2026-10-21。外部仕様を実装に合わせて改訂し、「UTF-8に限る」との食い違いは解消。出典は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|7.8]]。**読解のみ、動作は未確認**）:
  - [ ] ①レガシー符号のファイルを保存するとUTF-8に変わる点を利用者に提示するか（現状は無通知で、外部仕様もそれを認めた）
  - [x] ②`__location_information__`形式は、検出してエラーにする代わりに「読み込んで無視する」へ外部仕様・内部仕様・実装を統一（2026-10-22、`blankLocationInformation`）。第8章の発生源`input`は診断を生成しないままで正しい

## Related
- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — 外部仕様と内部仕様・実装の差分一覧|外部仕様と内部仕様・実装の差分一覧]]（2026-10-21、食い違い・未実装・不整合の一覧）
- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — 未実装・未結線項目の監査 — 2026-10-26|未実装・未結線項目の監査]]（2026-10-26、親仕様を含む28件、コード基準）
- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — 三者監査 69件の実装要否一覧 — 2026-11-09|三者監査 69件の実装要否一覧]]（2026-11-09、要実装66件・不要3件。契約補足は内部仕様・外部仕様の「監査対応」ノート）
- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — V0.2.0 実装計画 — 2026-11-09|V0.2.0 実装計画]]（2026-11-09、段0〜5・7、tecsgen相当機能はV0.2.1へ）
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
- [x] [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 06B 表示フィルタUI設計|第6B章]]（表示フィルタ、外部仕様7.5.2）の1〜7番を実装（2026-10-23〜24、PR #4、コミット`da603e0`・`50909a4`・`5fd550d`・`3a87b29`）。`DisplayFilters`を非表示リージョンの集合へ作り替え、色分けの帯・表示制御バー・リージョン木・凡例・結合スタブ・検索連携を追加。`HitTester`が非表示セルを掴める不具合も修正。518テストpass
- [x] 整列操作（上端・左端、外部仕様7.3.2）を結線（2026-10-24、PR #5、コミット`6974663`、524テストpass）。差分一覧のF1
- [ ] 第6B章の目視確認——リージョン木のポップオーバー、凡例、結合スタブ、検索連携、整列（`tests/testa/test-region/regions-join-test.cde`で確認できる）。あわせて暫定値（帯2mm・スタブ4mm・横線2mm・パレット）を決める
- [x] 差分一覧のF2（結合経路の重なり回避、PR #6、コミット`bf022a2`）・F3（セル名強調、PR #7、コミット`ec996d0`）を実装し、F4（スペース+ドラッグのパン、PR #8）とともにマージ済み（2026-10-24）。いずれも`origin/main`
- [x] 差分一覧のF5（Escでの検索解除、PR #10）・F6（選択時の所属リージョン表示、2026-10-26）を実装。F2〜F6はすべて解消。残りはF3のセル名が長いときの扱い（切り詰め・縮小）の未決と、目視確認
- [x] PR #4・#5・#6・#7・#8のマージ（2026-10-24）
- [[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定|TECSCDE-DT-EL preload ESM・sandbox決定]] — 実機起動確認で判明したpreloadのESM/CJS不整合への対応（`sandbox: false`確定）
- [[work/active/tecs/TECSCDE-DT-EL PasteCommand非同期クリップボード決定|TECSCDE-DT-EL PasteCommand非同期クリップボード決定]] — 第4章4.1節実装で判明した`ClipboardGateway.readText()`の非同期化と`Command.apply()`の同期性の不整合への対応
- [[TECSCDE-DT-TA実装]] — 姉妹実装（Tauri・Rust）。2026-09-07リポジトリ初期化、本ノートを進め方の先例にしている
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]] — 本実装が実現する外部仕様（デスクトップ版）
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]] — 第5・6章のクラス表現の正典
- [[perf/competencies/ソフトウェアアーキテクチャ|ソフトウェアアーキテクチャ]] — クラス階層・main/renderer/preloadのプロセス境界・依存方向の機械的強制
- [[North Star]] — 本ラインが🔴最優先（DT-EL版の内部仕様・実装への移行）。[[TECSCDE-JS-TS実装]]（関数ベース）は現行実装として維持しつつ、クラスベース設計の検証は本実装で前進させる

## 2026-09-16以降の詳細ログ

tree-sitter移行・`TecsgenCommandBuilder`の`-I`誤り訂正・未コミット作業の整理（いずれも2026-09-16）は[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Progress Log — 2026-09-16〜|TECSCDE-DT-EL実装 — Progress Log — 2026-09-16〜]]に分離（2026-09-20、25KB閾値）。

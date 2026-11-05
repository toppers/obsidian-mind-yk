---
date: 2026-09-16
description: "TECSCDE-DT-EL実装 の日付つき進捗ログ（2026-09-16〜）。[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Progress Log|TECSCDE-DT-EL実装 — Progress Log]] が25KBを超えたため verbatim 分離。物理順を保持。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - implementation
---

Event-log satellite of [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]（2026-09-20、25KB閾値でProgress Logからさらに分離）。日付つきの実装エントリを元の物理順のまま保持する。要約とAction Itemsはコア側。

## 2026-09-16 tree-sitter移行

- [x] 手書き`lexer.ts`／`parser.ts`を`CdlGrammar`＋CST走査`CdlDocumentBuilder`へ置換し、`web-tree-sitter@0.25.10`と3種のWASMを同梱
- [x] Electronではrendererから`file://`をfetchせず、mainがasar透過の`fs`でWASMを読み、preload IPC経由でバイト列を渡す構成にした
- [x] `import`／`import_C`原文保持、CDL終端`;`、tecsgen文法による直列化結果の再解析を実装
- [x] ビルド成功、21ファイル・190テストpass、dependency-cruiser 82モジュール／287依存で違反0件

## 2026-09-16 `TecsgenCommandBuilder`の`-I`誤り訂正

- [x] `src/renderer/tecsgen/command-builder.ts`が[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携#8.4.2 JS 版の規定|外部仕様8.4.2]]の旧誤り（`-I <base_dir>`）を引き継いだまま未修正だった件を解消。`base_dir`はコマンドラインへ一切出さない（`buildArgs`から除去）よう修正し、外部仕様の例どおり`import_path`用の`-I`・`define_macro`用の`-D`に加えて未対応だった`cpp`用の`-c`も新設。呼び出し元（`tecsgen-actions.ts`の`generate`/`tecsgenCommandLine`）は`TecsgenCommandInput`の形をそのまま渡しているため変更不要。テスト（`tests/renderer/tecsgen-command-builder.test.ts`・`tecsgen-actions.test.ts`）を訂正後の仕様に合わせて更新（baseDirがCLIに出ないことを明示的にアサート）。`npm run check`（build＋191テストpass＋depcruise違反0件）green

## 2026-09-16 未コミットだった作業のコミット・push

`git status`確認で、以前完了と記録していた2件の作業が実際にはコミットされていなかったと判明——vaultの記録と作業ツリーの実態が食い違う4件目の事例（[[brain/Patterns - 検証と調査 Archive#実装前にリポジトリの実態を確認する（2026-09-06、2件目の発生）]]参照、ただし今回はvault遅れ型: 記録は完了扱いだが実際は未コミット）。

- [x] 第9章9.6節`import_C`プリプロセス実行とフォールバック配線（2026-09-13作業分、コミット`afb6b32`）
- [x] Electron Forge導入（2026-09-12作業分、コミット`26d8ddc`）。同コミットに、ユーザーの明示指示によるサンプル起動元の一時的な変更（`celltypes.cdl`→`main.cde`重複、より適切なCDLファイル用意までの暫定措置）を含む
- [x] `.gitignore`にAIコーディングツールのローカル設定・状態（`.claude/`・`.cursor/`・`.github/`・`.kiro/`・`CLAUDE.md`・`*.code-workspace`）を追加——いずれもTECS実装のソースではなくローカルテレメトリ
- [x] `origin`（`github.com/toppers/tecscde-dt-el`）へpush済み。当ノートが従来「対象リモートリポジトリ」としていた`ykominami/tecscde-dt-el`は`upstream`として別途設定されている（Context節を訂正）

## 2026-09-20 保存・Undo/Redo・結合作成の実機確認、保存インジケータ修正

[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|コア]]の実機確認（CSP・ブートストラップ順修正）に続き、同日中にユーザーが保存・Undo/Redo・結合作成も対話的に確認。

- **Undo/Redo**: 移動→Undo→Redo、ボタンの有効/無効切替まで含めて問題なし。
- **結合作成**: サンプルの`main.cde`は全ポート接続済みのため、「セル新規作成」モードで`tController`セルを新規作成し、その`cLog`（呼び口）から`cLogger1.eLog`（受け口）へドラッグして結合線を確認、シグニチャ不一致時の静かなキャンセルも確認。問題なし。
- **保存**: ファイル自体は正しく書き込まれる（mtime更新を確認）が、未保存状態のインジケータが`#status-file`末尾の「•」1文字のみで非常に気づきにくく、保存できたかの確信が持てないという指摘。バグではなくUI視認性の問題と判定。
  - **修正**（コミット`f83ce0f`）: 未保存時は`#status-file`を太字・オレンジ色にし、テキストも「ファイル名 ● 未保存の変更」に変更。`shell.dom.test.ts`に回帰テストを追加（`dirty`クラスとテキストの付与・解除を検証）。193テスト全pass。
- **発見した設計リスク（テストfixtureとライブサンプルの兼用）**: 上記の対話的テスト中、ユーザーの「保存」操作が実際に`public/samples/main.cde`を上書きした。ところがこのファイルは`tests/renderer/shell.dom.test.ts`ほか複数のテストファイルが`readFileSync`で直接読み込む**テストfixtureでもある**ため、一時的にテストスイート全体（28件）が壊れた（`git checkout -- public/samples/main.cde`で復旧、コード側の不具合ではなくfixture汚染）。根本对応（fixtureをテスト専用の別ディレクトリ/インライン文字列に分離する等）は未着手——次に本格的に触る際の宿題として記録。

## 2026-09-20 tecsgen実行・Cut/Copy/Paste・診断パネルの実機確認、3件の実バグ修正

保存・Undo/Redo・結合作成の確認に続き、同日中にtecsgen実行・Cut/Copy/Paste・検索・診断パネルも対話的に確認。**検索は問題なし**。残り3項目で実バグを発見・修正（コミット`86ec0ff`）。

- **Ctrl+C/X/Vが完全に無反応**: このリポジトリはどこにも`Menu.setApplicationMenu()`を呼んでおらず、Electronの自動生成デフォルトメニュー（Edit: Cut/Copy/Paste/Undo/Redo、標準アクセラレータCtrl/Cmd+X/C/V/Z付き）がrenderer側の`keydown`リスナへ届く前にキーを横取りしていた（デバッグログで`"Control"`キーは届くが`"c"/"x"/"v"`本体が一切届かないことを確認して特定）。`Menu.setApplicationMenu(null)`で既定メニュー自体を除去して解消（メニューバーが消えることは意図した変更——独自ショートカットは全てDOM側で処理済みのため）。
- **「コマンドをコピー」ボタンが無反応**（`window.tecscde.clipboard`が`undefined`）: `preload/index.mts`は「非サンドボックスpreloadなら`createRequire(import.meta.url)("electron")`経由でclipboardを直接取得できる」という前提で書かれていたが、実機確認でこの前提が誤りだったと判明（`typeof clipboard`が`undefined`）。**この誤った前提は`tests/preload/index.test.ts`が`createRequire`自体をモックすることで覆い隠されていた**——モックされた契約テストが実環境の境界の壊れを検出できなかった典型例（[[brain/Patterns - 検証と調査]]参照）。file/tecsgenと同じくipcMain経由（`clipboard:writeText`/`clipboard:readText`）に変更し、`ipc.test.ts`・`preload/index.test.ts`（createRequireモックは削除）を実態に合わせて更新。
- **「実行」(Generate)クリック後、診断が実際には正しく計算されているのに画面から認識できない**: デバッグログで`store.setTecsgenDiagnostics()`まで正しく到達し`E-TECSGEN-NOT-FOUND`診断1件が生成されていることを確認——ステータスバー中央の小さなボタンにテキストは出ているが、クリックした結果だと人間には認識できないとの指摘。`DiagnosticsPanelView.open()`を新設し、Generate完了後に診断があれば一覧パネルを自動的に開く形に変更。ボタン自体も太字・枠付き・背景色ありのバッジ表示に変更（保存インジケータ修正と同じ形）。診断メッセージも「tecsgen実行ファイルが見つかりません」という説明的な文言から「実行ファイル 'tecsgen' が見つかりません」という具体的な文言に変更（ユーザー指摘）。
- **194テスト全pass**、`npm run check`green（depcruise違反0件）。今回もログ取得に手間取った——OSレベルのstdoutリダイレクト（Bash `>`、PowerShell `Start-Process -RedirectStandardOutput`）がElectron（GUIサブシステムアプリ）に対して間欠的に効かず、最終的にrendererプロセスから`fs.appendFileSync`で直接ファイルへ書く方式に切り替えて解決した。

## 2026-09-22 ファイルブラウザ（第7B章）＋前回セッション復元・消去ボタン（第7C章#7/#9）実装、import自動追跡（第7章7.5節）の詳細設計

前回セッションで未コミットのまま存在していた第7B章（ファイルブラウザ基本設計：`chooseFolder`/`listDirectory`/`FileBrowserView`/ルートフォルダ永続化/未保存確認）を検証（vitest 225件pass）の上、第7C章7.7節の#7（前回セッション復元）・#9（消去ボタン）を実装。`AppSettings.lastSession`の追加と`saveAppSettings`のread-modify-write化（`fileBrowserRoot`と`lastSession`が互いを消さないよう修正）、起動時ドキュメント供給の優先順位を`pendingOpenPath` > `lastSession` > `samples`へ拡張、ツールバー「消去」ボタン（`newDocument`、references集合は維持）を追加。238テストpass、`npm run check`green。実機確認（再起動での復元・消去ボタン動作）もOK。コミット`829efc7`。

調査の結果、#8（参照専用追加）・#10（tecsgen-optsファイル一括読込）・#11（import統一）は、設計が前提とする`FileService.resolveImports()`（第7章7.5節）が未実装のため見送り。同日、この§7.5自体の詳細設計を実施——`ParsedCdl.imports`（`cst.ts`）が既にimport/import_C文を解析済みであることを確認した上で、`resolveImports()`の具体アルゴリズム（`searchDirs`×`importPaths`の探索）、tecsgen本体の実ソース（`Importable#find_file`）検証によるアルゴリズム対応関係の確定（旧「inferred・未検証」フラグを解消）、renderer側の再帰的解決オーケストレーション（`resolveAllImports`、循環・重複抑止）、`import_C`の第9章9.6節への受け渡し境界（`CdeclExtractor`自体は未実装と明記）、既存コードへの統合ポイント（`applyOpenResult`への変更）を[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|第7D章]]・[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章]]としてまとめた。7C章の記述は変更せず、実装前提を満たす形。

## 2026-09-22 import自動追跡（第7章§7.5、第7D/7E章）の実装

同日中に設計（第7D/7E章）を完了した直後、`E:\Ccur\typescript\TECSCDE-DT-EL`へ実装。`FileService.resolveImports()`（main）は編集対象ファイル自身のディレクトリ→`baseDir`→`extraSearchDirs`（renderer側が解決の進行に応じて蓄積）の順に`importPaths`を試す。`kind:"manual"`は絶対パスを直接確認し探索を経由しない（第7C章#8向けの地ならし）。UTF-8妥当性は`TextDecoder`の`fatal`オプションで検出——設計時点で「実装時に確定」としていた点をここで解決。`readPaths()`は返すパスを`resolve()`で正規化するよう修正（renderer側の重複排除が文字列比較で正しく機能するために必要）。

renderer側`resolveAllImports()`（新規`import-resolution.ts`）はモジュールBの既存出力（`ParsedCdl.imports`）を使い推移的に解決、正規化済み絶対パスで循環・重複を抑止（`editablePath`自身で種付けして自己import循環も防ぐ）。`import_C`は解決するが`references`には含めない（typedef/struct抽出を担う`CdeclExtractor`は第9章9.6節設計のみで未実装のため）。`applyOpenResult`を非同期化し、自動発見した参照を既存の`result.references`と重複排除して合流。

テスト作成中に実装側の実バグを1件発見・修正: `resolveAllImports`が各呼び出しへ渡す`extraSearchDirs`を配列参照のまま渡していたため、後続ラウンドでの`push`が過去に渡した呼び出し引数のスナップショットまで書き換えてしまっていた（`toHaveBeenCalledWith`の検証で発覚）。呼び出しごとに`[...extraSearchDirs]`でコピーするよう修正。252テストpass、`npm run check`green。コミット`e0e2c26`。

## 2026-09-22 第7C章#8/#10/#11（参照専用追加・tecsgen-opts一括読込・import統一）の実装

§7.5実装の直後、同日中に第7C章の残り3項目を実装。設計の擬似コード（いずれも「実装時に確定」と明記）を具体化する過程で2つの決定を追加: ①**参照追加は既存の編集対象を再構築する**——新しい参照ファイルのセルタイプを既存の`cell`（celltype未解決）へ反映するにはeditable＋全referencesを合わせた再パースが必要で、これはUndo/Redo履歴をリセットする（`openFromPath`が別ファイルを開く際に既に持つのと同じトレードオフとして、ユーザー確認済みで採用。未保存の内容自体は`CdlSerializer.serialize()`で引き継ぐため失われない）。②**`AppStore`に`referenceSources`（パス→生テキストのキャッシュ）を追加**——再構築のたびに既存参照をディスクから再取得するのは冗長・TOCTOU的に危ういため。

`addAsReference`（#8）はCtrl+クリックで、`loadOptionsFile`（#10）は`.tecsgen-opts`ファイルのクリックで発火する。07C章7.7.4節の擬似コードは`addAsReference`を`openFromPath`より先に呼ぶ順序だったが、`addAsReference`が既存の編集対象を前提とする実装とは矛盾するため（前の編集対象に参照が誤って付く）、**先にeditableを確定してから参照追加する順序に修正**した。`FileService.parseTecsgenOptionsFile`はテスト作成中に実バグを発見・修正: CDLファイルパスは`.tecsgen-opts`ファイル自身のディレクトリを基点に解決する必要があり（当初は素通しで、mainプロセスの起動ディレクトリ基点になってしまっていた）、`resolve(optsDir, f)`で修正。#11(a)（ツリー上の参照ハイライト）は`FileBrowserView`に`.reference`クラスを追加。268テストpass、`npm run check`green。コミット`7c0318d`。第7C章（#7〜#11）全項目の実装が完了。

## Related

- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]] — コア（要約・Action Items・Related）
- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Progress Log|TECSCDE-DT-EL実装 — Progress Log]] — 前段（2026-09-06〜09-13）
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]] — 対応する内部仕様（全11章）

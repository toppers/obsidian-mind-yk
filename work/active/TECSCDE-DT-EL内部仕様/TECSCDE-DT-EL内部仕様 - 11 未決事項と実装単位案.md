---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様 第11章 — 外部仕様由来とElectron固有の未決事項、実装単位案、実装との相違点。配布方式の候補は11Bへ分離。"
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

Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 11 of 11（本書の最終章）。

## 11. 未決事項と実装単位案

### 11.1 未決事項（外部仕様由来、既存内部仕様と共通）

複合セルタイプの表現方法は**2026-10-14に決定済み**。外側を通常セルとして表示し、内部は展開せず、図上で複合セルタイプを新規定義・編集しない。未対応構文の存在のみをプロパティ欄に表示する（[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 04 コンポーネント図の表現|TECSCDE-DT外部仕様4.7節]]）。OSクリップボード連携の詳細仕様（本書は往復のCDL断片化までを規定し、それ以上の高度な連携は範囲外）と図全体の自動レイアウトは引き続き未決。

### 11.2 Electron固有の未決事項

| # | 事項 | 現状 |
|---|---|---|
| 1 | ~~`sandbox: true`の採否~~ → **決定済み（2026-09-08）: `sandbox: false`** | preloadをESM（`.mjs`）で書く方針を採ったため`sandbox: false`（Electronのサンドボックス化preloadはESM importを使えない）。`contextIsolation: true`・`nodeIntegration: false`は維持。経緯・トレードオフ: [[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定\|preload ESM・sandbox決定]]。第2章2.4節のコードも`.mjs` + `createRequire`によるclipboard取得に更新済み |
| 2 | ~~配布ツールの選定~~ → **決定済み（2026-09-12パッケージング／2026-09-23自動更新）**: パッケージング(package/make)はElectron Forge（`@electron-forge/maker-squirrel`）。自動更新(publish)は`update-electron-app` + GitHub Actions（Node 22固定でpublish）で自動化する構成に確定。origin（`toppers/tecscde-dt-el`）が当初非公開で`update.electronjs.org`が使えないと判明し、いったん配布専用の公開ミラーリポジトリ案を採ったが、同日中にユーザーがoriginをpublicへ変更したため撤回——**originへ直接publishする**構成で確定した。**コード署名は引き続き未決。macOS向けMakerは11.2.2節、Linux向けMakerは11.2.3節で方式を選定済み（いずれも未実装）**。決定の経緯・却下した代替案は[[work/active/tecs/TECSCDE-DT-EL 配布アーキテクチャ決定|TECSCDE-DT-EL 配布アーキテクチャ決定]]参照。パッケージング導入時に見つかった3件の環境要因（gitフェッチ禁止によるoverrides、electron-winstallerの上流バグ、`@electron/packager`のNode 26非対応）は[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]Action Items参照。コード署名の背景知識・設定箇所は[[work/active/tecs/Electronアプリのコード署名|Electronアプリのコード署名]]、選定時に比較したパッケージング・自動更新ツールの一覧は[[work/active/tecs/Electronアプリの配布・自動更新ツール|Electronアプリの配布・自動更新ツール]]参照 |
| 3 | `tecsgen`・Cプリプロセッサの検出方法 | 第9章9.1節の`TecsgenRunner`は`PATH`頼みの起動（`execFile('tecsgen', ...)`）としたが、複数バージョンの共存やパス設定不備への対応（設定画面での明示的なパス指定等）は未決 |
| 5 | tree-sitterバインディングの選択 | **2026-09-13追加**（[[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 04 CDLパーサ／シリアライザ設計\|TECSCDE内部仕様第4章]]の改訂に伴う本書固有の選択）。ブラウザ版と異なりElectronはネイティブバインディング（`node-tree-sitter`）を選べるが、**モジュールBはrendererに置かれ`nodeIntegration: false`・`contextIsolation: true`（第2章2.4節）のためrendererからは読み込めない**。したがって選択肢は①rendererで`web-tree-sitter`（WASM）を使う（プロセス配置を変えずに済む・ブラウザ版と同一コード）②CDL解析をmainへ移し`node-tree-sitter`を使う（速いがBの配置を第2章2.2節から変更することになり、解析結果をIPCで渡す設計が増える）。**①を既定とする**——**2026-09-21、大規模CDLでの実測により決着**（[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]の`tests/perf/cdl-parse.bench.test.ts`、`RUN_CDL_BENCH=1`で実行）: 150〜6000セル（100〜4000結合）で計測したところ、6000セル・4000結合という現実のtecsgen CDL図では想定しづらい規模でも`CdlDocumentLoader.loadSources()`（パース＋CST走査＋モデル構築のフルパイプライン）の中央値は約75ms、スケーリングもほぼ線形で崖（急激な劣化点）は観測されなかった。②へ切り替える性能上の根拠は無いと判断し、①のまま確定する |
| 4 | ~~ファイルブラウザの再検討~~ → **決定済み（2026-09-21）: 採用。** [[TECSCDE-DT外部仕様]]第3章3.5.1節・第10章10.4節を改訂し、階層ツリー表示のファイルブラウザを採用した。訂正: 本表は以前「mainプロセスに`fs.readdir`（`FileService`の拡張）が既にある」と記載していたが誤りだった——2026-09-21時点の[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装\|TECSCDE-DT-EL実装]]の`FileService`にディレクトリ列挙機能は存在せず（`openDialog`/`openPath`/`openPaths`/`save`/`saveAsDialog`/`exportFile`のみ）、新規実装が必要。設計は第7章7.6節に追加した |
| 6 | ~~`TecsgenCommandBuilder`に`-k`（CDLファイルの文字コード指定）を追加するか~~ → **決定済み（2026-09-24）: 追加した。** [[work/active/tecsgen/tecsgen外部仕様 - 05 コマンドラインインターフェース\|tecsgen外部仕様第5章]]の`-k, --kcode`（既定`euc`）に対し、CDLファイルはUTF-8前提（[[TECSCDE外部仕様]]5.1.2節）のため`buildArgs`の先頭で常に`-k utf8`を付与するよう`command-builder.ts`を変更（コミット`6425b25`、テスト更新込みで279テスト全pass）。実際に文字化け・構文エラーが発生するかどうかは未確認のまま(inferred)だが、外部仕様が定める前提と一致させる安全側の対応として実施 |
| 7 | 起動時、固定のsamples/コマンドライン引数ではなく**前回終了時に開いていたファイルを復元する** | **決定済み（2026-09-22）**: `AppSettings`に`lastSession`（editablePath・referencePaths）を追加し都度保存、起動時は`pendingOpenPath` > `lastSession` > `samples`の優先順位で復元する。設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合\|第7C章7.7.1節]]参照 |
| 8 | ファイルブラウザで選択したファイルを、**既存の編集対象を置き換えるのではなく現在読み込み済みの全CDLファイル群に追加する** | **決定済み（2026-09-22、ユーザー確認）**: 解釈(a)「新ファイルをreferencesへ追加し既存editableは変えない」を採用。UI操作はCtrl+クリック（inferred・未検証）、実現方式は`import`自動追跡と同一の`resolveImports()`パイプラインを`kind: 'manual'`で流用（#11の統一と一体）。重複判定（既読み込み済みなら無視）は当初案のまま確定。設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合\|第7C章7.7.2節]]参照 |
| 9 | ツールバーに**「消去」ボタンを追加**（現在の図をクリアし、CDLファイルを何も読み込んでいない状態にする） | **決定済み（2026-09-22、ユーザー確認）**: [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作\|TECSCDE-DT外部仕様5.2節「新規作成」]]の別名として設計。未保存確認は第7B章7.6.4節の`confirmDiscardChanges()`を再利用。設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合\|第7C章7.7.3節]]参照 |
| 10 | ファイルブラウザで**tecsgenのコマンドラインオプション形式を記したテキストファイルを選択した場合、`-I`/`--import-path`の値をCDLのimport探索パスとして使い、列挙されたCDL-fileを読み込む** | **決定済み（2026-09-22、DT-EL固有拡張として設計）**: 新拡張子`.tecsgen-opts`（仮称・未確定）を定義し、複数CDL-fileのうち最後の1つを編集対象（8.1.2節の規則を踏襲）、残りを#8の`addAsReference`で参照専用追加。`-I`/`--import-path`は`ImportResolutionOptions.importPaths`へ橋渡し。外部仕様への昇格は未定のまま。設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合\|第7C章7.7.4節]]参照 |
| 11 | CDLの`import`構文で自動追跡されたファイルを、**ファイルブラウザで選択されたファイルと同等に扱う** | **決定済み（2026-09-22）**: (b)「発見経路によらず同一データ構造で管理」は#8の実現方式（`resolveImports()`共有）により自動的に満たされる。(c)「編集可否の統一」は対象外のまま据え置く（[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携\|TECSCDE-DT外部仕様8.1節]]の規定を変更しない、ユーザー確認済み）。(a)「ツリー上の参照ファイル表示」は`FileBrowserView.render()`に強調クラスを追加して解決。設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合\|第7C章7.7.5節]]参照 |

11.2.1〜11.2.3（Windowsのコード署名候補・macOS／Linuxのパッケージング方式）は、25KB閾値のため [[TECSCDE-DT-EL内部仕様 - 11B 配布方式の候補（署名・パッケージング）]] へ分離した（2026-10-10、本文は逐語移動）。

### 11.3 Tauriではなくelectronを選ぶことの含意（参考）

本書はElectronに固有化したことで、[[TECSCDE-DT外部仕様]]が言語非依存を保つために避けていた前提を置けるようになった。1点だけ、Tauriとの比較で明らかになった留意点を記す——**ElectronはWebViewを自前でバンドルする（Chromium同梱）ため、TauriのようなOSごとのWebView実装差異（第2章2.4節、[[TECSCDE-DT外部仕様]]第2章2.4節）は生じない**。これはElectron選択の利点だが、その代わりアプリケーションの配布サイズが大きくなる（Chromium同梱のため）というトレードオフを伴う。本書はこのトレードオフの評価自体は行わない（配布方式は11.2節#2のとおり範囲外）。

### 11.4 最初の実装単位の提案

[[TECSCDE-TS内部仕様]]11.3節の提案（モデル＋CDLパーサ／シリアライザのround trip）を土台としつつ、本書固有の検証観点を1つ追加する。

1. **モデル＋CDLパーサのround trip**（[[TECSCDE-TS内部仕様]]11.3節と同一）——外部との唯一の契約点を最初に固める。
2. **IPCゲートウェイの疎通確認を、UIの実装より先に行う。** `FileGateway.open()`→`FileService.openDialog()`→IPC→レンダラでの受信、という一往復が、preloadの`contextBridge`設定を含めて正しく動作することを最初に確認する。これは本書固有の新しいリスク（`contextIsolation`・`sandbox`設定の誤りはUI実装が進んだ後に発覚すると手戻りが大きい）に対する検証観点であり、[[TECSCDE-TS内部仕様]]にはなかった項目である。
3. 次点として`History`のUndo/Redoをヘッドレスでテストする単位（[[TECSCDE-TS内部仕様]]11.3節と同一の優先順位）。

### 11.5 実装（TECSCDE-DT-EL実装）との相違点・設計更新

実機（Electron 44）起動検証およびヘッドレス契約テストの過程で判明し、実装（`E:\Ccur\typescript\TECSCDE-DT-EL`）側で解決・更新された設計差分を記録する。

| # | 項目 | 本書の当初記述 / 想定 | 実装（[[TECSCDE-DT-EL実装]]）での実際 | 理由・背景 |
|---|---|---|---|---|
| 1 | `PasteCommand` のクリップボード受渡し | `ClipboardGateway.readText()` を同期取得してコマンド内で読む | 事前に解決済みの `string \| undefined` を引数で受け取る | Electron 44 の `clipboard.readText()` は非同期（`Promise`）だが、`Command.apply()` は純粋同期のため。[[work/active/tecs/TECSCDE-DT-EL PasteCommand非同期クリップボード決定\|決定記録]] |
| 2 | `CutCommand` の副作用 | `apply()` 内で OS クリップボードへ書き込み | 副作用を `AppStore.cutSelection` へ移し、`apply()` は純粋なモデル削除のみ | `History.current` の replay 計算（`past` の毎回再生）により、レンダリング毎にクリップボード書き込みが再発するのを防止するため |
| 3 | `HitTester` / `GestureController` の結線 | `HitTester` は `SvgRenderer` を受け取り、`GestureController` はコンストラクタで DOM リスナ登録 | `HitTester` は `CanvasView`（ズーム換算のみ）を受け取り、`GestureController` の DOM 結線は `attach(svg)` に分離 | 描画インスタンスとの循環依存を排除し、状態機械をヘッドレスで単体テスト可能にするため |
| 4 | パン（Pan）の実現方式 | SVG レベルの変形（`viewBox` / `transform`） | HTML シェルのスクロールコンテナ（`pan-scroll.ts`、`panCenter` ⇔ `scrollLeft/Top`） | 実 DOM スクロールとの自然な統合。`CanvasView` は `panCenter` を読まない |
| 5 | UI シェル（モジュールG）の設計 | TS版の `UiComponent` ライフサイクル抽象クラス階層を踏襲 | `AppShell` と各専用ビュー（`PaletteView` 等）が `AppStore`・DOM/IPC に直接結合 | Electron 特有の IPC/プロセス境界および DOM 構造に特化したシンプルな設計を採用 |
| 6 | Preload の形式と Sandbox | `sandbox: true`（または未決） | ESM（`.mjs`）＋ `sandbox: false`（`contextIsolation: true`・`nodeIntegration: false` は維持） | Electron のサンドボックス化 preload が ESM を解釈できないため、`createRequire` で `clipboard` を取得する構成に確定。[[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定\|決定記録]] |
| 7 | tree-sitter WASM のロード | renderer からの直接読み込み | Main プロセスが `fs` で読み、Preload/IPC 経由で renderer へバイト列を渡して初期化 | renderer からの `file://` fetch が CORS でブロックされる制約を回避するため |
| 8 | 起動時初期ドキュメントの供給 | renderer 起動後に IPC でオープン要求 | Main が `did-finish-load` 後に `app:bootstrap` IPC でソース群をプッシュ供給 | renderer 起動時の CORS/非同期ロード制約を回避し、確実なブートストラップを行うため |
| 9 | 倍率コントロールのUI形式 → **解消済み（2026-09-21）** | 本書は独自の再設計を行わず、[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 03 画面構成#3.2.1 座標系と用紙\|外部仕様3.2.1]]の「5%〜200%・既定100%・整数値の**スライダ**」を継承する前提 | ツールバーに`−`／`100%`（`zoomReset`）／`＋`の3ボタンのみで、スライダは未実装だった状態から、`<input type="range" min="5" max="200" step="1">`（外部仕様3.2.1準拠の整数値スライダ）を追加（コミット`06f2c25`）。ユーザーがスライダとボタン組の使用感を比較した結果、`−`／`＋`ボタンを削除しスライダへ一本化（コミット`43268b4`）。曖昧だった「100%」ボタンのラベル（現在倍率のライブ表示だと誤解される原因になっていた）は「Reset Rate」に改称し、スライダの左に残置（既定倍率へのリセット機能は維持、外部仕様7.1.2のCtrl+0ショートカットと同等）。ズーム変更（ホイール／キーボード／リセット）に応じて`refreshToolbarState()`がスライダの表示値を同期する | 記録なし（2026-09-21、対話的確認で発見・同日中に解消）。外部仕様7.1.2が規定するCtrl+0キーボードショートカット（既定倍率へのリセット）の視覚的な代替としてボタン化したと推測されるが、当初ボタン方式を採った判断が明文化された記録は見つからないまま（inferred、未検証）——ただし逸脱自体は解消済み |

## Related

- [[work/active/tecs/TECSCDE-DT-EL 配布アーキテクチャ決定|TECSCDE-DT-EL 配布アーキテクチャ決定]]（2026-09-23、11.2節#2の自動更新部分を解消した決定記録）
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 11 未決事項と実装単位案|TECSCDE-TS内部仕様 第11章（対応する既存設計、外部仕様由来の未決事項の一次情報源）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 10 制約・制限|TECSCDE-DT外部仕様 第10章（ファイルブラウザ採用の一次情報源、2026-09-21改訂）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章（7.6節、ファイルブラウザの設計）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|TECSCDE-DT-EL内部仕様 第7C章（7.7節、#7〜#11の設計本体）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様 第9章（11.2節#6、`-k`欠落の詳細記録）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
date: 2026-05-10
description: "Living document of goals, focus areas, and aspirations — read at session start, updated when direction shifts"
tags:
  - brain
  - north-star
aliases:
  - Goals
  - Focus
---

# North Star — yasuo kominami

A living document of goals, aspirations, and current focus areas. Both you and Claude write to this. Claude reads it at the start of meaningful work sessions and references it when making suggestions.

## Current Focus

_What am I working toward right now?_

### TOPPERSプロジェクトの[[TECS開発]]（TECS WG関連）

#### TECSCDE JS版の内部仕様・実装への移行

- [[TECSCDE外部仕様]]は全11章完成（2026-08-13）。第6章分割後も原文141,227 bytesとの完全一致、heading link、孤立ノート、oversized flagを検証済み。
- [[TECSCDE内部仕様]]は全12章執筆完了（2026-08-29）。2026-08-30、`E:\Ccur\typescript\TECSCDE` にてTypeScript実装に着手し、モデル・CDLパーサ/シリアライザ・編集コマンド/Undo-Redo・SVG描画・ファイルI/O・UIシェルを実装、ブラウザ上での起動・サンプル読込・セル編集・Undo/Redoの動作を確認済み。実装過程で5章のUndo/Redo設計を`Command{apply, invert()}`からreplayベースの`History`に簡素化。実装アーキテクチャ案は[[TECSCDE-実装アーキテクチャ案]]。
- 外部仕様の追加整理やVault整備は、内部仕様・実装を直接前進させる場合だけ優先します。
#### [[TECSCDE-DT外部仕様]]
#### 🔴 最優先: TECSCDE-DT-EL版の内部仕様・実装への移行

- リポジトリ: `E:\Ccur\typescript\TECSCDE-DT-EL`（[[TECSCDE-JS-TS実装]]の`E:\Ccur\typescript\TECSCDE`とは別リポジトリ。2026-09-06に`git init`、リモート https://github.com/ykominami/tecscde-dt-el は非公開・2026-09-11作成、初期化なし）。対応する内部仕様は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]]（Electron・クラスベース、全11章 2026-09-05）。
- 進捗: 第11章11.4節の実装単位#1〜#3（モデル+CDL round trip・IPCゲートウェイ疎通の契約テスト・第4章 Command/History）が完了。replayベースの`History`で外部仕様6.6.1の現行版2 Undo/Redo不具合を構造的に排除（2026-09-07、コミット`0b753e7`）。2026-09-08、Electron 44で実機`electron .`起動を確認（4プロセス構成で起動成功）。起動確認で判明したpreloadのESM/CJS不整合は、preloadをESM（`.mjs`）化＋`sandbox: false`で解消（[[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定|決定記録]]、内部仕様11.2節#1を確定）。2026-09-09、第5章（描画・インタラクション、`render/` 8ファイル）と第6章（表示制御、`view-state/` 5ファイル）をクラスベースで実装、90テストpass。2026-09-10、モジュールG（最小UIシェル）を実装し実機`electron .`でクリーン起動・samples描画を確認。2026-09-11、**モジュールA（FileI/O main）・第4章4.1節Copy/Cut/Paste（CDL断片シリアライズ＋非同期OSクリップボード対応、[[work/active/tecs/TECSCDE-DT-EL PasteCommand非同期クリップボード決定|決定記録]]）・モジュールGキーボード配線・モジュールG次段（パレット／プロパティパネル／検索ボックス／ナビゲータパネル）・第9章9.4節`TecsgenResultParser`・9.5節Generate操作配線（`TecsgenCommandBuilder`込み）を実装、183テストpass**。同日、第5・6章・モジュールG・Hを[[TECSCDE-TS実装]]へ移植（`commands/`も併せて移植、モジュールGは設計差異のため見送り）。2026-09-12、第8章8.4節の診断パネルUI配線（`DiagnosticsPanelView`、ステータスバーの件数表示をトグルボタン化し一覧＋ジャンプ機構を追加）を実装、185テストpass。同日、Electron Forgeを導入（11.2節#2のパッケージング選定を一部解消）——導入中に環境固有の問題3件（gitフェッチ禁止・`electron-winstaller`上流バグ・`@electron/packager`のNode 26非対応）を発見・解消し、`out/make/squirrel.windows/x64/`にSetup.exe生成を確認（Node 22 LTS実行が前提）。詳細: [[TECSCDE-DT-EL実装]]（Action Items、asar化後の実機preload動作確認のみ未消化、2026-09-12）。
- 次のステップ: SVG幾何/ズーム・パンの対話的目視確認（happy-domでは検証不能、`electron .`での手動確認のみ残る）。package/make後（asar化後）の実機起動でpreload/contextBridgeが動作するかも未検証（開発時の`electron .`起動確認とは別項目）。DT-EL実装が一巡した後の次の一手（DT-TA版への展開か、DT-EL残課題の継続か）は未決——次回セッション着手時に判断。
- JS版との関係: 本ラインが🔴最優先。[[TECSCDE-JS-TS実装]]（関数ベース）は現行実装として維持しつつ、クラスベース設計の検証はDT-EL版で前進させる。

#### TECSCDE-DT-TA版の内部仕様・実装への移行
- [[TECSCDE-DT-TA内部仕様]]
- [[TECSCDE-DT-TA実装]]
#### TECSCDE-TS版の内部仕様・実装への移行

- リポジトリ: `E:\Ccur\typescript\TECSCDE-TS`（[[TECSCDE-JS-TS実装]]の`E:\Ccur\typescript\TECSCDE`とは別リポジトリ。リモート https://github.com/ykominami/tecscde-ts は非公開・2026-09-05作成、初期化なし）。対応する内部仕様は[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]]（[[TECSCDE内部仕様]]のクラスベースTypeScript代替設計、全11章 2026-09-05）。本書の設計自体の採否は未決（[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 11 未決事項と実装単位案|11.2節]]）。
- 進捗（as of 2026-09-14）: モデル＋CDL＋診断型に加え、**第4章commands・第5章render・第6章view-state・モジュールH diagnostics を[[TECSCDE-DT-EL実装]]から逆移植済み**（2026-09-11、`531801d`）。2026-09-13〜14に**CDLパーサをtree-sitterへ移行**（`5a1c189`）し、**第7章モジュールA（ファイルI/O）を実装**（`8d779ba`）。120テストpass。この model/cdl/diagnostics は[[TECSCDE-DT-EL実装]]が`src/renderer/`へそのままコピーした一次情報源でもある。詳細: [[TECSCDE-TS実装]]。
- 次のステップ: **モジュールG（UIシェル）と`app/`シェル**——ブラウザで動く入口がまだ無く、モジュールAのDOM依存部分（`FileIOStrategy`の実体・エクスポート）が未検証のまま。DT-ELのUIシェルはElectron専用のため逆移植できず、TS内部仕様第2章の`UiComponent`設計で別途実装する必要がある。
- **保留**: モジュールI（tecsgen連携）が並行セッションとの二重実装になっており、一方をブランチ`feature/tecsgen-link-module-i`へ退避中。統合と外部仕様8.4.2の訂正は後日（[[TECSCDE-TS モジュールI 二重実装の保留]]）。
- 位置づけ: 🔴最優先そのものではなく、DT-EL版のクラス階層の一次情報源として、また[[TECSCDE内部仕様]]の代替設計の検証として前進させる。
#### CDLParser(tree-sitter利用)
- [[CDLParser(tree-sitter利用-JS版)]]
- 2026-09-13、**このパーサの採用を決定し、[[TECSCDE外部仕様]]（2.2・5.1.2・5.3.2・8.1.2・8.2.2・8.3.2・9.1.2・10章）と[[TECSCDE-DT外部仕様]]（8.1節・5章・10章・目次比較表）へ反映済み**。中心は「`import_C` 常に非対応」の撤回と構文エラー検出の新設、および「`import` を追跡しない」理由の訂正（パーサ能力→ファイルアクセス能力）——後者によりDT版では参照先の自動追跡が可能になった。経緯: [[work/active/CDLParser(tree-sitter利用)/TECSCDE外部仕様 tree-sitter反映案|TECSCDE外部仕様 tree-sitter反映案]]、決定: [[Key Decisions]]。同日、**内部仕様4書（[[TECSCDE内部仕様]]第4章を全面改訂＋第2/11/12章、TS版・DT-EL版・DT-TA版）と[[TECSCDE-実装アーキテクチャ案]]・[[work/active/TECSCDE共通ロジック/TECSCDE共通ロジック|TECSCDE共通ロジック]]も追随改訂済み**。同日、**[[TECSCDE-JS-TS実装]]の実装移行も完了**（コミット`353853a`、32テストpass・実機ブラウザでdev/build両方確認）。この移行で**旧実装の出力が有効なCDLでなかった**ことが判明し（サブセットではなく別方言で、保存した`.cde`はtecsgenに入力できなかった＝外部仕様2.2違反）、あわせて修正した。教訓は[[Patterns - 検証と調査#自前パーサと自前シリアライザのround-tripは、方言が外界の仕様から外れていても永久に緑になる（2026-09-13）|Patterns]]。未決だった`.wasm`配布方法（→`public/`配下）とWASMロード待ちの外部仕様反映要否（→実測約120msで不要）も決着。**残るは[[TECSCDE-TS実装]]・[[TECSCDE-DT-EL実装]]の2件の移行**と、構文エラー文言のG-code対応付けの粒度。
- [[CDLParser(tree-sitter利用-TS版)]]
#### [[tecsgen]]

- [[tecsgen|外部仕様]]と[[tecsgen-plugins|プラグイン仕様]]は、SVN trunk r3301の全85ファイルまで追随済み。[[work/active/tecsgen-plugins/PluginCoverageAudit|カバレッジ監査]]で既知対象を確認済みです。
- [[tecsgen内部仕様|内部仕様]]は、CType・MultiPluginディスパッチの統合（2026-08-15）に続き、4章クラス階層図の`MultiPlugin`欠落を修正し、9章に「既知の問題」節を新設して実装上の既知リスク3件（TransparentRPCSignaturePlugin参照切れ・FMPのRPC死コード・CppIfGenの二重無効化コード）を記録しました（2026-08-21）。2026-08-22、残っていた5・6・8・10〜12章をすべてソース照合し、set_require_joinの役割誤認（未結合エラー検出ではなくrequire節の自動結合生成）や存在しない変数`$KCODE_CDL`など複数の実質的な誤りを訂正。**2026-08-23、最後まで未検証だった1-3章も再照合**：1章の対象バージョン記載（1.9.0→実測1.9.1）、2章のファイル配置誤り3件（`tecs_lang.rb`の役割誤認・`namespacepath.rb`の配置先・`componentobj/generate.rb`の記載漏れ）、3章の処理フロー図の誤り（`set_require_join`の所属フェーズと役割・`check_join`のシグニチャ一致誤記・`optimize_and_generate`の条件付け誤り・`generate_post`の欠落）を訂正し、**全12章の個別検証パスが完了**しました。
- 実装着手・動作確認は完了（2026-08-30）。`MoveJoinBarCommand`実装完了・コミット済み（2026-09-01）。次のステップは`ChangePortEdgeCommand`のUI配線です。詳細: [[TECSCDE-JS-TS実装]]。
- ソース更新または実装上の必要がない限り、新規プラグイン仕様の探索は最優先にしません。

### 個人開発環境整備
#### NotebookLM管理システム
- NotebookLMソース管理システム([[notebooklmclix]])
#### 関連ドキュメント管理システム
- ドキュメント管理システム([[bookinfor]] — 書籍・Kindle・ドキュメント・APIキー管理 Railsアプリ)
- bookmark管理システム([[bookmarkr]] — Google Chromeのブックマーク・OneTab機能拡張)
- 
- bookmark管理拡張機能([[bmx]] — Google Chrome用機能拡張)
- Calibre用documentメタデータ抽出システム([[calibrex]] — calibre DBから)
- Gist管理システム([[gistx]])
- Githubリポジトリ管理システム([[ghrepo]])
- gitリポジトリ管理システム([[gitreporemote]])
- ICONファイル管理システム([[cpiconfiles]])
- ファイル管理システム([[filelist]])
- Google Drive用ファイルアップロードプログラム([[gupload]])
#### HTMLドキュメント解析システム([[htmlparser]])
- Amazon注文履歴モジュール(amazonorderscraper)
- Amazonカートモジュール(amazonsavedcartscraper)
- Fanza同人バスケットモジュール(fanzadoujinbasketscraper)
- Fanza同人購入履歴モジュール(fanzadoujinpurchasedscraper)
- Amazon-Kindle Unlimitedリストモジュール(kuscraper)
- Udemyマイラーニングモジュール(udemyscraper)
#### LLM対話システム
- janllm
#### Util関連
- TOMLファイル操作(tomlx)
- TkinterベースTUIプログラム(tkinterx_)
- (xmlkindle)
#### Python共通ライブラリ
- Pythonライブラリ([[yklibpy]])
- Pythonライブラリ([[yklibpyz]])
#### Ruby共通ライブラリ
- Rubyライブラリ(ykutils)
- Rubyライブラリ([[ykxutils]])
#### AI向けVCS
- [[entire]]
### AIツールチェーンコスト最適化
- トークン削減（RTK — Rust Token Killer）
- コンテキスト圧縮（headroom MCP — compress/retrieve/status）
- セッション横断記憶（agentmemory — Docker + iii-engine + Node.js）
- Claude Code コスト運用（モデル選択・CLAUDE.md設計・作業プロセス最適化）
### obsidian-pluginの活用
#### Cobsidian-tagfolder + tag-wrangler を導入した目的のタグ整理をいつかやる

## Goals

### Short-term (This Quarter)

- [x] [[TECSCDE外部仕様]]を入力として、JavaScript版内部仕様の章構成と主要コンポーネントの責務境界を決める（2026-08-21完了）
- [x] 内部仕様の最初の1単位を作成し、対応する実装・テストの入口まで定義する（2026-08-30、実装着手・動作確認済み）
- [x] tecsgen内部仕様を継続し、CType・MultiPlugin・既知の参照切れを優先して整理する（2026-08-21完了）
- [ ] 週1回以上の執筆セッションをstandupの最優先タスクとして維持する

### Medium-term (This Half)

- TECSCDE JavaScript版（フレームワーク非依存）の内部仕様を完成させ、検証可能な縦切りの実装を1本成立させる
- tecsgen内部仕様へ外部仕様・プラグイン仕様の知見を統合する
- 個人開発システム群のうち2つ（候補: [[notebooklmclix]]・[[ghrepo]]）を「日常運用中」の状態にする

### Long-term (This Year+)

- コンポーネントモデルリファレンスマニュアルをTECS WGで公開状態に持っていく
- TECS向けLSPサーバを実用レベルにする
- vault + wiki + QMD のナレッジ基盤を、維持作業ほぼゼロで回る状態にする

## Aspirations

_What kind of engineer/person am I becoming?_
- TECS WGの主要ドキュメント整備者としての貢献を、公開された仕様書群という形に残す
- 自作ツールチェーン（RTK・スキル・フック構成）を他者が再利用できる形で公開する
## Anti-goals

_What am I explicitly NOT optimizing for?_

- 準備・方法論収集が執筆を押し出すこと — 執筆タスクが1本終わるまで新ツール導入・環境整備をしない（Shifts Log 6/22・6/29・7/20・7/27 で**4回検出**）
  - **ハードゲート（2026-07-27 設定・1週間の試行）→ ✅ 2026-07-29 クリア**: TECSCDE外部仕様 第2章（動作環境）が埋まるまで `/om-vault-audit` と新規ツール導入を行わない、という条件を設定。**2026-07-29 に第2章を執筆して解除**。`/om-vault-audit` を起動した時点でゲート抵触を指摘 → その場で第2章に着手する判断が取られ、監査より執筆を先に通した。ゲートが機能した初めての事例（07-27 深夜は指摘後に抵触作業を実行していた）。
  - **1週間後（2026-08-03）の判定 → 判定前に条件充足・継続**: 第2章が 07-29 に埋まったためゲートは保たれた。TECSCDE外部仕様は最優先のまま継続する。**第3章（画面構成）も同日 07-29 に完成**し、次のゲート条件とした**第4章（コンポーネント図の表現）は 07-31、第5章（ファイル操作）は 08-01 に完成**した。判定日を待たずに条件を2章分先行して満たしている。
  - **降格検討の根拠は失効した（2026-08-01）**: 「06-03 の着手から8週間で1章」という実績を根拠に降格を検討する条件を置いていたが、実績は**07-23 からの10日間で第1〜5章**に変わった。ゲートは4回検出しても止まらなかった再発ループを実際に断っており、目標が実際の意図を反映していないという仮説は否定されたと判断する。以後は降格判定ではなく、**執筆の継続そのものを既定**とする。**第6章（編集操作）は 2026-08-06 に完成**——現行版の未実装2機能（クリップボード操作・グループ操作）を新規要件として規定し、アンドゥのオフバイワン不具合と Redo 恒久無効化という2件の不具合を発見した。次のゲート条件は第7章（表示機能）。
- メモリ/タスクシステムの多重化 — 正は brain/ 一本（2026-07-06 の beads 廃止決定を維持する）
- 「いつかやる」項目を Current Focus に置き続けること — 動かさない項目はここ（Anti-goals の下の判断基準）で切る

## Shifts Log

Record when focus changes, with date and reason.

| Date | Shift | Reason |
|------|-------|--------|
|      | Created North Star | Initial setup |

- [[North Star — Shifts Log — Segment 1|Segment 1]] — 表ヘッダーから物理順前半
- [[North Star — Shifts Log — Segment 2|Segment 2]] — 物理順中盤
- [[North Star — Shifts Log — Segment 3|Segment 3]] — 物理順後半

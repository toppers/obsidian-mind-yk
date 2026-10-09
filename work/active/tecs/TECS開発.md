---
date: 2026-04-26
description: "TOPPERSプロジェクト TECS WG — tecsgen・TECSCDE・ツール群・仕様書・mkspec の開発進捗概要"
project: TECS
quarter: Q2-2026
status: active
tags:
  - work-note
---

# TECS 開発

TECS WG の開発作業全体の進捗管理ノート。

## Context

- TECS (TOPPERS Embedded Component System) のコンポーネント記述言語・ツールチェーン開発
- tecsgen（コンポーネント記述コンパイラ）、TECSCDE（設計環境）、関連ツール群を並行開発
- 参照資料: [[reference/03-Resources/my-topic/CLAUDE|TECS Wiki]]
- tecsgenの最新コード  E:\Crepo\ykominami-svn-2\tecsgen\trunk

**状態凡例:** `-` 未着手 / `進行中` / `完了` / `保留`

> [!success] 共通ブロッカー解決済み（2026-05-19）
> ~~コードベースからのドキュメント生成方法（NotebookLM 等）が未決定。~~
> **決定**: NotebookLM は採用せず。RST ソースは llm-wiki（Claude Code 直接 ingest）で知識ベース化し、仕様書執筆は Claude Code がコードベースを直接読んで行う。tecs-docs の ASP3+TECS RST 32件を llm-wiki TECS トピックに取り込み済み（raw 48件、記事 13件）。

## tecsgen

コンポーネント記述言語のコンパイラ。Ruby 実装。

| 作業 | 状態 | メモ |
|------|------|------|
| 外部仕様作成 | 進行中 | [[tecsgen外部仕様]] ドラフト作成済み |
| プラグイン仕様書 | 進行中 | 名前付き5カテゴリ＋HRP2系＋無印HRP＋FMP＋HRMP＋カバレッジ監査4候補、すべて完了（2026-08-15）。詳細: [[work/active/tecs/TECS開発 — Progress Log#tecsgen プラグイン仕様書 詳細|Progress Log]] |
| 内部仕様作成 | 進行中 | [[tecsgen内部仕様]] ドラフト着手（2026-05-19）、87日ぶりに再開・加筆（2026-08-15）。`ctypes.rb`（未記載だった`CType`モジュール）と`MultiPlugin`ディスパッチ機構（`pluginModule.rb`の`load_plugin`実装＋ポストコード生成優先順位）をプラグイン仕様書シリーズの知見から追加。2026-08-21、4章クラス階層図の`MultiPlugin`欠落（`Plugin`ではなく`Node`直下）を修正し、9章に既知の問題3件（TransparentRPCSignaturePlugin参照切れ・FMPのRPC死コード・CppIfGenの二重無効化コード）を追加——プラグイン境界知見の内部構造への統合が一区切り。2026-08-22、未検証章の検証を開始：5章（字句解析・構文解析）をソース照合の上で全面改訂（字句解析は`bnf.y.rb`内蔵、`tecs_lang.rb`は文字コード解決のみ、Cパーサは`Import_C`経由のtypedef/struct限定パーサと訂正）。続けて6章（意味解析）も改訂——`set_require_join`は未結合エラー検出ではなく`require`節の自動結合生成であり、非optional呼び口の未結合検出は実際には`check_join`が担うと訂正。8章（コード生成）も一部訂正——`CFile`はテンポラリ書き出しではなく文字コード変換専用ラッパー、テンプレート出力可否は`-f`ではなく`--generate-all-template`系オプション、`INITIALIZE_TECS()`はセルタイプ別ファイルでなく`global_tecsgen.h`定義と修正。10章（ファイル入出力）も全面改訂——`Import.new`は「キューに積む」のではなく即座に同期パース、ファイル探索は`$import_path`単純走査でなく二段探索、`TECSIO`は`bnf.y.rb`内蔵と訂正。11章（エラー・警告処理）も全面改訂——コード生成前のエラーゲート（エラーがあれば生成フェーズに進入しない）と`finalize`での最終コミット抑制を追加、エラーコードプレフィックスをG/P/Wの3種から実測10種以上に訂正。12章（グローバル変数一覧）で架空の変数`$KCODE_CDL`等を削除し訂正——これで4-12章の個別検証パスが一巡。2026-08-23、残っていた1-3章を再照合：1章はバージョン記載が`1.9.0`から実測`1.9.1`にずれていたと判明し訂正、2章はファイル配置の誤り3件（`tecs_lang.rb`の「字句解析器」誤記述、`namespacepath.rb`の配置先誤り、`componentobj/generate.rb`の記載漏れ）を訂正、3章は処理フロー図の実質的な誤り（`set_require_join`の所属フェーズ誤り〔`semantics_analisys_2`ではなく`semantics_analisys_1`最終ステップ〕と役割誤記、`check_join`のシグニチャ一致誤記、`optimize_and_generate`全体を`$unopt`条件としていた誤り、`generate_post`の欠落）を訂正——全12章の個別検証パスが一巡した |
| リファクタリング | - | |
| 新機能追加 | - | |
| テスト仕様・テストプログラム作成 | 進行中 | |
| ユーザ向けドキュメント作成 | 進行中 | |

## tecsgen-python3

tecsgen（Ruby実装）のPython3移植版。構文解析は Ruby 版の racc の表を移植して使う（2026-09-27 に tree-sitter から変更 → [[tecsgen-python3 構文解析方式決定]]）。P2 まで実装・検証済み。詳細: [[tecsgen-python3]]

| 作業 | 状態 | メモ |
|------|------|------|
| 外部仕様作成 | - | [[tecsgen-python3外部仕様]] 未着手（2026-09-21プレースホルダ作成） |
| 内部仕様作成 | - | [[tecsgen-python3内部仕様]] 未着手（2026-09-21プレースホルダ作成） |
| 実装 | - | Python3版最新コード `E:/Ccur/python3/tecsgen-python3`。tecsgen-python3実装ノート未作成 |

## TECSCDE

TECS コンポーネント設計環境（Component Diagram Editor）。

| 作業                           | 状態   | メモ                                                                                                                                      |                |
| ---------------------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| 外部仕様・内部仕様                    | 本文完成 | [[TECSCDE外部仕様]] 全11章完成（2026-08-13）。詳細: [[work/active/tecs/TECS開発 — Progress Log#TECSCDE 外部仕様・内部仕様 詳細                                    | Progress Log]] |
| JS版（フレームワーク非依存）外部仕様          | 完了   | [[TECSCDE外部仕様]]の第2章が「本仕様が対象とするのはJS版（フレームワーク非依存）である」と明記しており、外部仕様全11章自体がこの対象。上の行と同一文書のため独立した進捗ではなかったと判明（2026-08-21、[[TECSCDE内部仕様]]執筆時に発覚） |                |
| JS版（フレームワーク非依存）内部仕様          | 完了   | [[TECSCDE内部仕様]] 全12章執筆完了（2026-08-29）。9モジュールの責務・依存方向・境界設計判断に加え各モジュール詳細設計・インタフェース一覧・実装単位案を規定                                                 |                |
| JS版（フレームワーク非依存）実装アーキテクチャ     | 完了   | [[TECSCDE-実装アーキテクチャ案]]（9モジュール→`src/`配置案、依存方向の機械的強制方針）                                                                                    |                |
| JS版（フレームワーク非依存）実装             | 着手・動作確認済み | 2026-08-30、`E:\Ccur\typescript\TECSCDE` にてモデル・CDLパーサ/シリアライザ・編集コマンド/Undo-Redo・SVG描画・ファイルI/O・UIシェルを実装。ブラウザ上での起動・サンプル読込・セル編集・Undo/Redoの動作を確認済み。`MoveJoinBarCommand`実装完了・コミット済み（2026-09-01）。次は`ChangePortEdgeCommand`のUI配線。詳細: [[TECSCDE-JS-TS実装]] |                |
| JS版（クラスベース）内部仕様（代替設計）        | 全11章執筆完了・採否未決 | 2026-09-05、[[TECSCDE内部仕様]]（関数/インタフェースベース）とは別系統で、クラスベースOOP設計を全11章執筆完了。モジュール分割・依存方向は既存と同一、モデル層（呼び口=結合1本まで等を型階層で表現）・編集コマンド/Undo-Redo（`History`クラスがreplay計算をカプセル化）・描画/表示制御/ファイルI-O/整合性チェック/tecsgen連携/インタフェース一覧まで完了。対応する実装は未着手で、本書自体の採否（現行実装を置き換えるか等）も未決定（第11章11.2節）。詳細: [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様\|TECSCDE-TS内部仕様]] |                |
| デスクトップ版（Electron/Tauri両対応）外部仕様 | 全11章執筆完了 | 2026-09-05、[[TECSCDE外部仕様]]（ブラウザ単体版）を踏まえ、言語非依存（TypeScript/Electron・Rust/Tauriのどちらでも同一挙動）のデスクトップ版外部仕様を新規執筆。両フレームワークで実現可能な機能（ネイティブファイルI/O・tecsgenのサブプロセス直接実行・OSクリップボード連携）を積極採用し、ブラウザ由来の制約の大半を解消。詳細: [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様\|TECSCDE-DT外部仕様]] |                |
| デスクトップ版（Electron・クラスベース）内部仕様 | 全11章執筆完了 | 2026-09-05、[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様\|TECSCDE-DT外部仕様]]を[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様\|TECSCDE-TS内部仕様]]のクラス設計を踏襲しつつElectronに固有化。中心はmain/renderer/preloadのプロセス境界設計（`FileService`/`TecsgenRunner`をmainに、モデル・コマンド・描画をrendererに配置し、IPCゲートウェイクラスで橋渡し）。詳細: [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様\|TECSCDE-DT-EL内部仕様]] |                |
| デスクトップ版（Electron・クラスベース）実装 | 実装進行中（モジュールG/Hまで） | 2026-09-06、`E:\Ccur\typescript\TECSCDE-DT-EL`にてモデル/CDL/diagnosticsを[[TECSCDE-TS実装]]から移植、main/preload/rendererゲートウェイを新規実装。第4章（`Command`/`History`）・第5章（描画）・第6章（表示制御）・モジュールG（最小UIシェル、esbuild＋実機 `electron .` クリーン起動確認）・モジュールH（診断集約）まで実装、117テストpass（2026-09-10）。`dependency-cruiser`でプロセス境界を機械的強制。preloadのESM化＋`sandbox: false`を確定（[[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定\|決定記録]]）。詳細: [[TECSCDE-DT-EL実装]] |                |
| デスクトップ版（Tauri・Rust）内部仕様 | 全11章執筆完了 | 2026-09-05、[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様\|TECSCDE-DT外部仕様]]をRustで実装するための内部仕様。姉妹文書[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様\|TECSCDE-DT-EL内部仕様]]（Electron・TS）とモジュール分割は同一だが、Rustに`class`がないためstruct+impl+traitのイディオマティックな設計に置き換え、プロセス境界もbackend/frontendの2層（preload相当なし、クリップボードも含め全ネイティブ操作がinvoke経由に統一）に単純化。フロントエンドも`web-sys`によるRust/WASMで統一。詳細: [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様\|TECSCDE-DT-TA内部仕様]] |                |
| デスクトップ版（Tauri・Rust）実装 | リポジトリ初期化のみ | 2026-09-07、`E:\Ccur\typescript\TECSCDE-DT-TA`にて`git init`（初期化のみ、README＋Rust用`.gitignore`、初回コミット`5c568f6`）。中身の実装は未着手。EL版と違い対応するRust実装が存在しないため、model/CDL層も`tecscde-ts`内部仕様からの新規移植になる。詳細: [[TECSCDE-DT-TA実装]] |                |
| 実装ライン間の共通ロジック整理 | 棚卸し中・共有方法未決 | 2026-09-08、[[TECSCDE-JS-TS実装]]（関数ベース）と[[TECSCDE-DT-EL実装]]（クラスベース）が共有するロジックを3層（挙動仕様＝実装中立／純粋計算＝コード共有候補／クラス階層＝クラスベース実装のみ）に分類。1層目は既存内部仕様で共有済み、2層目の物理的な共有方法（verbatimコピー継続／共有パッケージ切り出し／仕様のみ共有）は未決。詳細: [[work/active/TECSCDE共通ロジック/TECSCDE共通ロジック\|TECSCDE共通ロジック]] |                |
| JS版（フレームワーク依存）外部仕様           | -    |                                                                                                                                         |                |
| JS版（フレームワーク依存）内部仕様           | -    |                                                                                                                                         |                |
| JS版（フレームワーク依存）実装             | -    |                                                                                                                                         |                |
| JS版（フレームワーク依存）テスト仕様・テストプログラム | -    |                                                                                                                                         |                |

## ツール群

| ツール | 作業 | 状態 | メモ |
|--------|------|------|------|
| tecsmerge | 実装・仕様 | 進行中 | |
| RubyScriptAnalyzer | 実装・仕様 | 進行中 | |
| TECS向け LSP サーバ | 実装・仕様 | 進行中 | |
| CDLParser (tree-sitter) | 実装・確認 | 進行中 | [[CDLParser(tree-sitter利用-JS版)]] / [[CDLParser(tree-sitter利用-TS版)]] |

## ドキュメント

llm-wiki に TECS RST ドキュメントを ingest 済み（2026-05-19）。仕様書執筆は Claude Code + llm-wiki の組み合わせで進める。

| ドキュメント | 状態 | メモ |
|------------|------|------|
| TECS仕様書 | 進行中 | 2026-09-13、llm-wikiに`tecs-spec-base`（SVN trunk/base直下`tecs_spec.md`、TeX→Markdown直接変換）を新規ingest。既存`tecs-0-md`とは同一バージョン(V1.3.0.1)で逐語一致を確認（変換パイプラインの段数差のみ、tecs-0-mdはノイズ多め）、`tecs-0`とは版が異なり逐語重複なしと判明。公開状況（tecs-0は公開済み、tecs-spec-baseは非公開）も記録。詳細: [[reference/Note/0-TECS/TECS-MEMO/wiki-raw\|wiki-raw]] |
| ツール仕様書 | 進行中 | |

## mkspec（テスト管理）

| 作業 | 状態 | メモ |
|------|------|------|
| テスト管理システム整備 | 進行中 | |

## llm-wiki Ingest 候補

[[tecs-docs]] の RST ファイルのingest候補リスト（90件超）。`E:\Crepo\github-toppers\tecs-docs\docs\` 配下。
- asp3（13件）、atk2+tecs（9件）、mruby-on-ev3rt+tecs（14件）、tecs（35件）、tinet+tecs・tlsf+tecs（各index）
- 元リスト: `reference/Inbox/llm-wiki-ingest-candidate-list.txt`（絶対パス版）、`llm-wiki-ingest-2-candidate-list.txt`（相対パス版）

## Action Items

- [ ] llm-wiki TECS トピックをベースに仕様書ドラフトを開始する

完了済み45件の履歴: [[work/active/tecs/TECS開発 — Progress Log#Action Items 履歴（完了分）|Progress Log]]

## Open Questions

## Related

- [[work/active/tecs/TECS開発 — Progress Log|TECS開発 — Progress Log]] — 詳細な進捗ナラティブ・Action Items 完了分の全履歴
- [[North Star]]
- [[reference/03-Resources/my-topic/CLAUDE|TECS Wiki]]
- [[perf/competencies/技術文書化|技術文書化]] — 仕様書作成の competency 証拠
- [[perf/competencies/ソフトウェアアーキテクチャ|ソフトウェアアーキテクチャ]] — CDL・tecsgen 設計判断の competency 証拠

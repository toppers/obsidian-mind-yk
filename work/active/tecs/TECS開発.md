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

## TECSCDE

TECS コンポーネント設計環境（Component Diagram Editor）。

| 作業 | 状態 | メモ |
|------|------|------|
| 外部仕様・内部仕様 | 本文完成 | [[TECSCDE外部仕様]] 全11章完成（2026-08-13）。詳細: [[work/active/tecs/TECS開発 — Progress Log#TECSCDE 外部仕様・内部仕様 詳細|Progress Log]] |
| JS版（フレームワーク非依存）外部仕様 | 完了 | [[TECSCDE外部仕様]]の第2章が「本仕様が対象とするのはJS版（フレームワーク非依存）である」と明記しており、外部仕様全11章自体がこの対象。上の行と同一文書のため独立した進捗ではなかったと判明（2026-08-21、[[TECSCDE内部仕様]]執筆時に発覚） |
| JS版（フレームワーク非依存）内部仕様 | 進行中 | [[TECSCDE内部仕様]] 第1〜2章（概要・モジュール構成と責務境界）着手（2026-08-21）。9モジュールの責務・依存方向・境界設計判断を定義。第3章以降は未着手 |
| JS版（フレームワーク依存）外部仕様 | - | |
| JS版（フレームワーク依存）内部仕様 | - | |
| JS版（フレームワーク依存）実装 | - | |
| JS版（フレームワーク依存）テスト仕様・テストプログラム | - | |

## ツール群

| ツール | 作業 | 状態 | メモ |
|--------|------|------|------|
| tecsmerge | 実装・仕様 | 進行中 | |
| RubyScriptAnalyzer | 実装・仕様 | 進行中 | |
| TECS向け LSP サーバ | 実装・仕様 | 進行中 | |

## ドキュメント

llm-wiki に TECS RST ドキュメントを ingest 済み（2026-05-19）。仕様書執筆は Claude Code + llm-wiki の組み合わせで進める。

| ドキュメント | 状態 | メモ |
|------------|------|------|
| TECS仕様書 | 進行中 | |
| ツール仕様書 | 進行中 | |

## mkspec（テスト管理）

| 作業 | 状態 | メモ |
|------|------|------|
| テスト管理システム整備 | 進行中 | |

## llm-wiki Ingest 候補

tecs-docs RST ファイルのingest候補リスト（90件超）。`E:\Crepo\github-toppers\tecs-docs\docs\` 配下。
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

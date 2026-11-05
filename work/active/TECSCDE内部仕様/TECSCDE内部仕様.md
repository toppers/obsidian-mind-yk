---
date: 2026-08-30
description: "TECSCDE（JS版・フレームワーク非依存）内部仕様書の目次。全12章（2026-08-29完成）を章別ノートに分割。実装はTECSCDE-JS-TS実装を参照。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - index
---

# TECSCDE 内部仕様

> [!info] 文書状態
> **改訂（2026-09-13）**: [[TECSCDE外部仕様]]2.2節がCDL解析系のみを外部依存の例外として認める形へ改訂されたことを受け、**第4章（CDLパーサ／シリアライザ設計）を全面改訂**した。手書きの再帰下降パーサ（`cdl/lexer.ts`・`cdl/parser.ts`）を廃し、tecsgen自身の構文定義から移植したtree-sitter文法2種（`tree-sitter-cdl`・`tree-sitter-tecs-cdecl`）を`web-tree-sitter`（WASM）で読み込む構成へ改めている。あわせて第2章（モジュールBの責務・非同期初期化の設計判断）・第11章（ディレクトリ構成・Bのインタフェース・ランタイム依存と`.wasm`配布の未決）・第12章（未決事項3件と往復検証の基準）を追随させた。**実装はまだ追随しておらず**、3リポジトリの`lexer.ts`・`parser.ts`は手書きのまま（移行メモは4.7節）。経緯: [[work/active/CDLParser(tree-sitter利用)/TECSCDE外部仕様 tree-sitter反映案|TECSCDE外部仕様 tree-sitter反映案]]。
>
> **全12章執筆完了（2026-08-29）／実装着手・動作確認済み（2026-08-30）** — [[TECSCDE外部仕様]]（JS版・フレームワーク非依存、全11章、2026-08-13完成）を通読したうえで、モジュール構成と責務境界（2章）を定義し（2026-08-21）、続けて3〜12章（各モジュールの詳細設計・モジュール間インタフェース一覧・未決事項と実装単位案）を執筆した。新規の一次資料調査は行わず、外部仕様の該当箇所を根拠として設計判断を導出した。2026-08-30、`E:\Ccur\typescript\TECSCDE` にてTypeScript実装に着手し、モデル・CDLパーサ/シリアライザ・編集コマンド/Undo-Redo・SVG描画・ファイルI/O・UIシェルの一式を実装、ブラウザ上での起動・サンプル読込・セル編集・Undo/Redoの動作を確認した。実装過程で5章のUndo/Redo設計を`Command{apply, invert()}`からreplayベースの`History`に簡素化（5.1〜5.3を実装反映済みに更新）。`MoveJoinBarCommand`実装完了・コミット済み（2026-09-01）。次のステップは`ChangePortEdgeCommand`のUI配線、および[[North Star]]が定める後続の実装単位への着手。実装の詳細な進捗・既知の差分は[[TECSCDE-JS-TS実装]]を参照。

全12章、[[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 01 概要|章別ノート]]に分割済み（2026-08-30、25KB閾値）。

## 目次

- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 01 概要|1. 概要]] — 目的、対象範囲（外部仕様全11章との対応）、対象読者、関連文書
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 02 モジュール構成と責務境界|2. モジュール構成と責務境界]] — 9モジュールの責務、依存方向、境界設計判断
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 03 モデル設計|3. モデル設計]] — Cell/Port/Join/Region/Signature の型定義と不変条件
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 04 CDLパーサ／シリアライザ設計|4. CDLパーサ／シリアライザ設計]] — 対象文法サブセット、`__tool_info__` スキーマの要素単位検証
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 05 編集コマンドとUndo-Redo設計|5. 編集コマンドとUndo/Redo設計]] — コマンドパターン、現行版2件の不具合の解消方針。実装時にinvert()方式からreplayベースのHistoryへ簡素化（2026-08-30）
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 06 描画・インタラクション設計|6. 描画・インタラクション設計]] — SVG更新戦略、ヒットテスト、ドラッグ状態機械
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 07 表示制御設計|7. 表示制御設計]] — ズーム/パン/グリッド/ナビゲータ/検索/表示フィルタ
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 08 ファイルI-O設計|8. ファイルI/O設計]] — File System Access API分岐、ドラッグ&ドロップ、エクスポート
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 09 整合性チェックとメッセージ設計|9. 整合性チェックとメッセージ設計]] — 診断収集パイプライン、メッセージ一覧
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 10 tecsgen連携設計|10. tecsgen連携設計]] — コマンド文字列組み立て、非実行の境界
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 11 モジュール間インタフェース一覧|11. モジュール間インタフェース一覧]] — 2章の依存図を具体的な契約まで落とした参照補遺
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 12 未決事項と実装単位案|12. 未決事項と実装単位案]] — 複合セルタイプ等の未決事項、最初の実装単位の候補

## Related

- [[TECSCDE外部仕様]] — 本内部仕様が実装する外部仕様（全11章）
- [[TECSCDE-実装アーキテクチャ案]] — 本内部仕様を踏まえたTypeScript実装のパッケージ構成・型設計・テスト戦略案
- [[TECSCDE-JS-TS実装]] — アーキテクチャ案に沿った実装の進捗ノート（動作確認・既知の差分）
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]] — 本書（関数/インタフェースベース）に対する、クラスベース内部設計の代替案（2026-09-05着手）
- [[tecsgen内部仕様]] — 内部仕様書の記述形式の先例（同じ「章別ノート分割」パターンを2026-08-16に先行採用）
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体
- [[North Star]] — 🔴最優先事項としてのTECSCDE JS版内部仕様・実装への移行
- [[perf/competencies/ソフトウェアアーキテクチャ|ソフトウェアアーキテクチャ]] — モジュール分割・依存方向設計の competency 証拠

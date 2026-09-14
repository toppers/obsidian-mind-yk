---
date: 2026-09-08
description: "TECSCDE-JS-TS実装（関数ベース）とTECSCDE-DT-EL実装（クラスベース・Electron）の両方が必要とする共通ロジックの棚卸しと、物理的な共有方法の未決事項を追跡するノート。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - implementation
---

# TECSCDE共通ロジック

## Context

- [[TECSCDE-JS-TS実装]]（関数/interfaceベース、ブラウザ、`E:\Ccur\typescript\TECSCDE`）と [[TECSCDE-DT-EL実装]]（クラスベース、Electron、`E:\Ccur\typescript\TECSCDE-DT-EL`）は**別リポジトリ・別パラダイム**だが、同じエディタを実装するため多くのロジックを共有する。
- きっかけ: [[TECSCDE-DT-EL実装]]の Action Item「第5・6章（描画・表示制御）は [[TECSCDE-TS実装]] にも未実装、両方で同時に必要」。実装を始める前に**何が共通で・その正典（single source）はどこにあり・どう共有するか**を先に決めておくためのノート（[[reference/Note/daily/2026-09-08|2026-09-08 日次ノート]]の目標より）。
- 対象は JS-TS実装 と DT-EL実装 の2つ。クラス階層そのものを共有する [[TECSCDE-TS実装]]（クラスベース・ブラウザ）と [[TECSCDE-DT-EL実装]] の関係は別軸（下記「3層目」参照）。

## 共通ロジックの3層

### 1層目: 挙動仕様（実装方式に非依存・最重要）

両実装が守るべき**振る舞い**。正典は既存の実装中立な内部仕様。

| 領域                                       | 正典                                                                          | JS-TS実装                                                        | DT-EL実装                                                                                                                                                             |
| ---------------------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SVGツリー構造・差分更新戦略（図全体の再描画をしない）             | [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 06 描画・インタラクション設計\|TECSCDE内部仕様 第6章]] | 実装済み（`svgRenderer.ts`）                                         | 実装済み（`render/svg-renderer.ts`、2026-09-09。モジュールG（2026-09-10）で実機 `electron .` 起動・描画ツリー生成を確認。対話的目視は次回）                                                                 |
| ヒットテスト優先順位（ポート＞セル＞結合バー）・結合バー探索の半径限定      | 同上 6.2節                                                                     | 実装済み（`hit-test.ts`）                                            | 実装済み（`render/hit-tester.ts`、2026-09-09。ヘッドレステスト8件）                                                                                                                  |
| ドラッグ状態機械の4状態（通常／呼び口上／結合中／結合先有効）・結合プレビュー線 | 同上 6.3節・外部仕様3.7                                                             | 実装済み（`gesture.ts`）                                             | 実装済み（`render/gesture-controller.ts`、2026-09-09。ヘッドレステスト12件）                                                                                                         |
| ズーム・パン・グリッド・表示フィルタ・検索の表示状態（`.cde`に保存しない） | [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 07 表示制御設計\|TECSCDE内部仕様 第7章]]        | 一部実装（`viewState.ts` — scale/grid/filter/signature名のみ、pan/検索なし） | 実装済み（`view-state/` 5ファイル、2026-09-09）。モジュールG（2026-09-10）で `panCenter` ⇔ scrollLeft/Top を `app/pan-scroll.ts`＋`app/shell.ts` に配線（スクロールコンテナ方式）。ズーム固定点・スクロール連動の対話的目視は次回 |
| Undo/Redo の挙動（replay方式、現行版2不具合を解消）       | [[work/active/tecs/TECSCDE Undo-Redo設計決定\|Undo-Redo設計決定]]                   | 実装済み                                                           | 実装済み（[[TECSCDE-DT-EL実装]] 第4章、2026-09-07）                                                                                                                            |

→ **この層は既に共有されている**（同じ内部仕様を両実装が参照する）。DT-EL側の第5・6章実装は、JS-TS実装の挙動を移植先の言語構造へ写す作業になる。

### 2層目: 純粋計算ロジック（パラダイム非依存・コード共有の候補）

関数として書けるためクラス化の有無に関わらず**同一コードを共有しうる**部分。現状は各リポジトリに別々のコピーが存在（または存在予定）。

- 座標・整列: `ALIGN = 1.0mm` グリッドスナップ、モデル座標⇔画面座標の変換（zoom/pan考慮）
- 結合バー自動経路計算（`autoRouteBars` 相当、JS-TS実装 `geometry.ts` / DT-EL実装 `commands/support.ts`）
- ヒットテストの数理（点と矩形・線分の距離、半径内判定）
- CDL パーサ/シリアライザ — **2026-09-13に性質が変わった**。構文解析が tecsgen の構文定義から移植した tree-sitter 文法（`tree-sitter-cdl`／`tree-sitter-tecs-cdecl`）へ移り、**文法定義そのものが言語非依存の共有物になる**（[[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 04 CDLパーサ／シリアライザ設計|TECSCDE内部仕様 第4章]]）。共有すべき自前コードは CST 走査（モデル構築）・`__tool_info__` 検証・シリアライザに縮み、最も移植コストの高かった字句解析・構文解析は**共有方法を決めるまでもなく外部パッケージとして共有される**。Rust版（[[TECSCDE-DT-TA実装]]）は公式 `tree-sitter` クレートを直接使える点で他3実装と条件が異なる（DT-TA内部仕様11.2節#6）
- モデル不変条件の検査（呼び口＝結合1本まで、シグニチャ一致 等）
- 整合性チェックのメッセージカタログ（警告文言）

→ **共有方法は未決（TBC）**。下記「共有方法の決定」参照。

### 3層目: クラス階層（クラスベース実装のみ）

`SvgRenderer`／`ElementRenderer`・`CellRenderer`／`JoinRenderer`・`HitTester`・`GestureController`・`ViewState`・`DisplayFilters` のクラス設計。正典は [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 05 描画・インタラクション設計|TECSCDE-TS内部仕様 第5章]]・[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 06 表示制御設計|第6章]]。

- **[[TECSCDE-TS実装]]・[[TECSCDE-DT-EL実装]] の2つが共有**（DT-EL内部仕様 第5・6章が「TECSCDE-TS内部仕様と完全に同一、変更なし」と規定）。
- **[[TECSCDE-JS-TS実装]] は対象外**（関数/interfaceベースの別実装）。ただし挙動（1層目）は同一。
- model/CDL/diagnostics も同様: クラスベース版は [[TECSCDE-TS実装]] が一次情報源で DT-EL が `src/renderer/` 配下へ verbatim コピー。JS-TS実装 は関数ベースの独自実装。

## 共有方法の決定（未決 / TBC）

2層目（純粋計算ロジック）を2リポジトリ間でどう物理的に共有するかは**未決**（このノート作成時点で方針の指示なし — inferred）。選択肢:

| 案 | 内容 | トレードオフ |
|----|------|-------------|
| A. verbatim コピー（現状） | 各リポジトリに同じコードを複製。内部仕様が「同一」を保証 | 追加インフラ不要。ただし片方の修正が他方へ伝播せず、drift のリスク（[[Patterns]]・[[Gotchas]]に既出の「ノート未更新のまま実装が進む」と同型の危険） |
| B. 共有パッケージ | `@tecscde/core-logic` を npm workspace / git subtree で切り出し、両リポジトリが依存 | drift を構造的に排除。ただし JS-TS実装 と DT-EL実装 のリポジトリ統合または subtree 運用が必要 |
| C. 仕様のみ共有 | 2層目もコード共有せず、内部仕様（1層目）だけを正典に各自再実装 | 現状の延長。3実装が並存する限り再実装コストが線形に増える |

- Rust版（[[TECSCDE-DT-TA実装]]）は言語が異なるため2層目のコード共有対象外。3案いずれでも DT-TA は内部仕様からの新規移植になる。
- 推奨（inferred）: 実装ラインが3〜4本に増えた今、2層目は案Bの検討に値する。少なくとも「どのファイルが2層目か」を各リポジトリで明示し、コピー元を1つに固定する（案Aの規律版）ところから。

## Action Items

- [ ] 共有方法（案A規律版／B／C）をユーザーと決める
- [ ] 2層目に該当するファイルを JS-TS実装・DT-EL実装 の両リポジトリで洗い出し、対応表を本ノートに追記
- [x] DT-EL実装 第5章の着手時、1層目（挙動）は [[work/active/TECSCDE内部仕様/TECSCDE内部仕様|TECSCDE内部仕様]] 第6章、クラス表現は [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]] 第5章を正典として参照する（2026-09-09、[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]第5章）
- [x] DT-EL実装 第6章（表示制御）実装完了（2026-09-09、[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]）。1層目＝[[work/active/TECSCDE内部仕様/TECSCDE内部仕様|TECSCDE内部仕様]] 第7章、クラス表現＝[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]] 第6章を正典に。第5章の暫定 `CanvasView` は `ViewState.toCanvasView()` の射影先として残置（モジュールG実装時に配線）
- [x] [[work/active/TECSCDE-TS実装/TECSCDE-TS実装|TECSCDE-TS実装]] 第6章へ DT-EL の `ViewState`/`DisplayFilters` を写す（2026-09-11、第4・5章・モジュールHと合わせて移植完了）
- [x] DT-EL実装 モジュールG（最小UIシェル）で `SvgRenderer`/`GestureController`/`ViewState` を実DOMに配線・実機起動確認（2026-09-10、[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]）。`src/renderer/app/` 5ファイル＋happy-dom テスト18件。パレット等の次段UIは別途
- [x] [[work/active/TECSCDE-TS実装/TECSCDE-TS実装|TECSCDE-TS実装]] 第5・6章と DT-EL実装 第5・6章は「完全に同一」規定。第5・6章・第4章4.1節（Copy/Cut/Paste/CDL断片）・第9章（TecsgenResultParser/TecsgenCommandBuilder）の共通ロジック同期完了（2026-09-13、120テストpass）

## Related

- [[TECSCDE-JS-TS実装]] — 関数ベース実装（1層目の挙動の実装済み参照元）
- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]] — クラスベース・Electron実装（第5・6章が本ノートの直接のきっかけ）
- [[work/active/TECSCDE-TS実装/TECSCDE-TS実装|TECSCDE-TS実装]] — クラスベース・ブラウザ実装（3層目のクラス階層を DT-EL と共有）
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様|TECSCDE内部仕様]] — 1層目（挙動）の正典
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]] — 3層目（クラス表現）の正典
- [[work/active/tecs/TECSCDE Undo-Redo設計決定|TECSCDE Undo-Redo設計決定]] — 1層目のうち Undo/Redo の設計決定
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体
- [[perf/competencies/ソフトウェアアーキテクチャ|ソフトウェアアーキテクチャ]] — 3層分類と共有方法のトレードオフ整理
- [[North Star]] — 🔴最優先の [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]] を含むTECS開発ライン


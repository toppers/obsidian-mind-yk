---
date: 2026-09-05
description: "TECSCDE クラスベースTypeScript設計（TECSCDE-TS内部仕様）の実装進捗ノート。現行の関数ベース実装（TECSCDE-JS-TS実装）とは別系統。モデル＋CDL（tree-sitter化完了）・第4章commands（Copy/Cut/Paste含む）・第5章render・第6章view-state・第7章io・モジュールH diagnostics（TecsgenResultParser含む）・モジュールI tecsgen（TecsgenCommandBuilder）まで実装完了（2026-09-13、120テストpass）。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - implementation
---

# TECSCDE-TS実装

## Context
- [[TECSCDE-TS内部仕様]]（クラスベース設計、全11章執筆完了 2026-09-05）に対応する実装。現行実装[[TECSCDE-JS-TS実装]]（関数/interfaceベース）とは別系統で、本書の設計自体の採否は未決（[[TECSCDE-TS内部仕様 - 11 未決事項と実装単位案]]11.2節）。
- 対象ローカルリポジトリ: `E:\Ccur\typescript\TECSCDE-TS`（[[TECSCDE-JS-TS実装]]の`E:\Ccur\typescript\TECSCDE`とは別リポジトリ）
- 対象リモートリポジトリ: https://github.com/ykominami/tecscde-ts（非公開、2026-09-05作成、README等の初期化なし）

## Notes
- **2026-09-06確認、single-source-status訂正**: 本ノートは2026-09-05時点で「着手前」と記載していたが、実際には`E:\Ccur\typescript\TECSCDE-TS`に`initial commit`（`741815e`、2026-09-06 08:31）としてモデル（C: `src/model/`）＋CDLパーサ/シリアライザ（B: `src/cdl/`）＋診断型（Hの型のみ: `src/diagnostics/types.ts`）が実装済みで、`tests/model.invariants.test.ts`・`tests/cdl.roundtrip.test.ts`の8件が全てpassすることを確認した（作成者・作成セッション不明——[[TECSCDE-JS-TS実装]]の`MoveJoinBarCommand`と同型の「気づいたら実装済みだった」ケース）。[[TECSCDE-TS内部仕様 - 11 未決事項と実装単位案]]11.3節が提案した最初の実装単位（モデル＋CDLパーサ/シリアライザのround trip）はこれで完了。
- 11.2節の採否判断（クラス化で不変条件の保証が本当に強くなっているか）は、`model.invariants.test.ts`の「クラス化後はmoveTo()自体がalignRound()を強制するため...壊れた値を作れないことを確認する」テストにより、少なくとも1件（呼び口=結合1本の不変条件）は検証済み。
- この実装は[[TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]（Electron版）が`src/renderer/model`・`src/renderer/cdl`として**そのままコピーして再利用**した一次情報源でもある（2026-09-06、[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]]第3・5・6・8章が「完全に同一」と規定していたことの実務上の裏付け）。
- **2026-09-11、逆方向の移植（DT-EL→TS）を実施**: DT-EL側が先行実装した第4章`commands/`・第5章`render/`・第6章`view-state/`・モジュールH `diagnostics/`（`collector.ts`・`integrity.ts`）をそのままコピー。付随して、DT-EL側で拡張されていた`model/join.ts`（`withBars()`追加）と`cdl/messages.ts`（`unresolvedReferenceFile`追加）も同期。第4章は元の依頼範囲外だったが、第5章`gesture-controller.ts`が`AddCellCommand`等の具象コマンドを直接importしており前提として必須のため合わせて移植（ユーザー確認済み）。テストも`tests/renderer/*.test.ts`から6ファイルを`tests/*.test.ts`へ移し、import深さを`../../src/renderer/`→`../src/`に調整。`tsc --noEmit`green、`vitest run`75件全pass。**モジュールG（UIシェル）は今回スキップ**——DT-EL実装のUIシェルはElectron専用`AppShell`（DOM/IPC直結、`gateways/`・`shared/ipc-types.js`に依存）で、TS内部仕様[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 02 モジュール構成と責務境界|第2章]]が定義する`UiComponent`ライフサイクル抽象（`Toolbar`/`PropertyPanel`/`StatusBar`/`Palette`のサブクラス）とは設計が異なり、「完全に同一」の対象にならないため（ユーザー確認済み）。コミット`531801d`（2026-09-11）。
- **2026-09-13、tree-sitter文法移行・第7章モジュールA実装・共通ロジック同期を実施**:
  - `5a1c189`: 手書きパーサを `web-tree-sitter` による CDL 文法（`cst.ts` / `grammar.ts`）へ移行。
  - `8d779ba`: 第7章モジュールA（ファイルI/O: `FileOpener` / `FileSaver` / `Exporter` / `DirtyTracker`）を実装（89テストpass）。
  - **共通ロジック同期（2026-09-13）**:
    - 第4章4.1節 / CDL断片: `src/cdl/fragment.ts`（`serializeCellsAsCdl`、`tryParseCdlFragment`）、`src/commands/clipboard-commands.ts`（`CopyCommand` / `CutCommand` / `PasteCommand` / `pasteFromAppClipboard` / `pasteFromCdlFragment`）。tree-sitter文法の末尾 `;` 要求に合わせて `cell` 定義ブロック終端を `};` に整合。
    - 第9章9.4節: `src/diagnostics/tecsgen-result-parser.ts`（`TecsgenResultParser`、`TECSGEN_CODES`）。
    - 第9章9.5節: `src/tecsgen/command-builder.ts`（`TecsgenCommandBuilder`）。
    - テスト4ファイル（`tests/cdl-fragment.test.ts`、`tests/clipboard-commands.test.ts`、`tests/tecsgen-result-parser.test.ts`、`tests/tecsgen-command-builder.test.ts`）を追加。**全120テストpass**、`tsc --noEmit` green。

## Action Items
- [x] モデル（C）＋CDLパーサ/シリアライザ（B）のround trip実装に着手する（[[TECSCDE-TS内部仕様 - 11 未決事項と実装単位案]]11.3節）——2026-09-06確認、8テストpass
- [x] 不変条件（型階層・`static create()`で保証されるもの）を独立したテストで検証する——`model.invariants.test.ts`で確認済み
- [x] `History`クラスのUndo/Redoをヘッドレスでテストする単位に着手する——2026-09-11、[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]から`src/commands/`を移植して完了
- [x] 第5章`render/`・第6章`view-state/`・モジュールH `diagnostics/`（collector・integrity）を[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]から移植（2026-09-11、75テストpass）
- [x] 手書きパーサからtree-sitter CDL文法への移行（2026-09-13、コミット`5a1c189`）
- [x] 第7章モジュールA（ファイルI/O）の実装（2026-09-13、コミット`8d779ba`）
- [x] [[work/active/TECSCDE共通ロジック/TECSCDE共通ロジック|共通ロジック]]（Copy/Cut/Paste・CDL断片・TecsgenResultParser・TecsgenCommandBuilder）を同期（2026-09-13、120テストpass）
- [ ] モジュールG（UIシェル）をTS独自の`UiComponent`ライフサイクル設計で実装する（DT-ELのElectron専用`AppShell`は移植不可、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 02 モジュール構成と責務境界|第2章]]の設計に従い別途実装）
- [x] 2026-09-11の移植分をコミットする——コミット`531801d`

## Related
- [[TECSCDE-TS内部仕様]] — 本実装が対応するクラスベース内部仕様（全11章）
- [[TECSCDE-JS-TS実装]] — 現行の関数ベース実装（比較対象）
- [[TECSCDE内部仕様]] — 現行実装が準拠する既存内部仕様
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体
- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]] — 本実装のmodel/cdl/diagnosticsをそのまま流用したElectron版実装
- [[work/active/TECSCDE共通ロジック/TECSCDE共通ロジック|TECSCDE共通ロジック]] — 実装ライン間の共通ロジック棚卸し（本実装は3層目のクラス階層をDT-EL実装と共有）
- [[North Star]] — 🔴最優先事項としてのTECSCDE JS版実装（本実装は代替設計の検証であり、最優先ラインそのものではない）


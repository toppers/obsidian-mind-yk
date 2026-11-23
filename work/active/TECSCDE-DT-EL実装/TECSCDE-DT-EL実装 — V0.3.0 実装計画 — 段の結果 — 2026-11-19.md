---
date: 2026-11-19
description: "TECSCDE-DT-EL V0.3.0 実装計画の段0〜段3の実施結果（現行コード確認、変更ファイル、検証結果、実機確認、v0.3.0 タグ・push 完了）。"
project: TECS
quarter: Q4-2026
status: tracking
tags:
  - work-note
  - tecs
  - tecscde
---

[[TECSCDE-DT-EL実装 — V0.3.0 実装計画 — 2026-11-19|V0.3.0 実装計画]]の段ごとの結果。

## 段0 の結果（2026-11-19）

実装リポジトリ（`E:\Ccur\typescript\TECSCDE-DT-EL`）で現行コードを確認した。

- **「情報」ダイアログ**: `src/renderer/app/information-dialog.ts` の `renderVersion()` が `tecsgen:` と `実行コマンド:` を出力しており、設定欄には `TECSPATH` の読み取り専用 `<input>` のみがあり `TECSGEN_COMMAND` の環境変数値を表示するフィールドは無かった。
- **5B. 色に依存しない状態表示**: `src/renderer/index.html` の `#status-legend` が `#canvas-area` 内に `position: absolute; left: 8px; top: 8px; z-index: 5;` で配置されており、キャンバス左上に描画されたセルを覆い隠す構造になっていた。
- **ユーザー確定（2026-11-19）**:
  - ラベル表記は `"環境変数TECSPATH:"` で確定。
  - `"tecsgenのコマンドラインオプション:"` の値は従来の `"実行コマンド:"` と同じ（実際に使う tecsgen コマンド列）とする。
  - `#status-legend` はキャンバス上端の専用バー（`#toolbar` の直下・`#main` の直上）へ移設する。
  - V0.3.0 は段1＋保存の設計強化（段2）＋描画と画面 UI の整備（段3）に絞り、残りを V0.3.1 / V0.4.0 へ分割する。

**段0 は完了（2026-11-19）。**

## 段1 の結果（2026-11-19、実機確認完了 2026-11-20）

ユーザー追加分 2 件をテスト先行（Red → Green）で実装した。

| 対象 | 変更ファイル | 内容 |
| --- | --- | --- |
| 環境変数 `TECSGEN_COMMAND` の受け渡し | `src/shared/ipc-types.ts`, `src/main/tool-settings.ts` | `ToolSettings` に `tecsgenCommandEnv?: string` を追加し、`ToolSettingsService` が `this.environment.TECSGEN_COMMAND ?? ""` を返すようにした |
| 「情報」ダイアログ改修 | `src/renderer/app/information-dialog.ts` | ① `renderVersion()` の `実行コマンド:` を `tecsgenのコマンドラインオプション:` に変更（`tecsgen:` は tecsgen のバージョンを表示）。② `TECSPATH` のラベルを `環境変数TECSPATH:` に変更。③ `環境変数TECSGEN_COMMAND:` の読み取り専用 `<input>`（`#information-tecsgen-command`）を新設し、次の行に環境変数 `TECSGEN_COMMAND` の値を表示するようにした |
| 5B. 状態凡例のセル被り解消 | `src/renderer/index.html` | `#status-legend` を `#canvas-area` のオーバーレイ（`position: absolute`）から外し、`#toolbar` 直下・`#main` 直上の独立した固定バー（`flex: none`）へ移設した |
| テスト | `tests/renderer/v030-stage1.dom.test.ts`, `tests/main/v030-stage1-tool-settings.test.ts`, `tests/renderer/information-dialog.dom.test.ts` | 情報ダイアログの4項目・`ToolSettingsService` の `tecsgenCommandEnv`・`#status-legend` の配置と CSS を検証するテストを追加し、既存テストの旧ラベル期待値2件を更新 |

- **検証**: `tsc` 3設定・`build-renderer.mjs`・`build:main`・`depcruise`・`vitest`（126 ファイル・1298 件）すべて pass。
- **実機確認（2026-11-20、ユーザー確認）**: 問題なし。**段1 は完了。**

## 段2 の結果（2026-11-20、実機確認完了 2026-11-20）

保存の設計強化（4-2・4-5・4-6・4-7）をテスト先行（Red → Green）で実装した。

| 相違# | 変更ファイル                                                            | 内容                                                                                                                                                                                           |
| --- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 4-2 | `src/renderer/app/file-actions.ts`                                | 主ファイル未確定（`!store.filePath`）のときも、変更済みの参照 CDL（`referenceTickets`）があればそれぞれの元のパスへ保存する。主ソースに未保存変更が無い場合は `saveAs` ダイアログを出さずに完了し、主ソースにも未保存変更がある場合は参照 CDL 保存後に続けて `saveAs` を呼ぶ（キャンセルしても参照 CDL は保存済み） |
| 4-5 | `src/renderer/cdl/serializer.ts`                                  | `CdlSerializer.serialize()` のセル選別から `doc.sourceTemplates.size <= 1` を外し、主ファイル所有または `locale` 未設定のセルだけを選別するように変更。また `joinList` もドキュメント全体ではなく選別セル所有（`editableCellIds`）の結合のみを出力するように統一           |
| 4-6 | `src/renderer/cdl/serializer.ts`, `src/renderer/cdl/tool-info.ts` | `buildCellList` / `buildJoinList` を新設し、元のテンプレート内 `__tool_info__("tecscde")` に含まれていたセル・ポート・結合・バー階層内部の未知キーを `serialize` / `serializeSource` の両方で保持して書き戻すようにした（バーは本数一致時のみ引き継ぐ）                  |
| 4-7 | `src/renderer/cdl/tool-info.ts`                                   | `isValidBarLayout`・`isValidJoinBars` を追加し、`parseTecscde` の `join_list` 検証で空配列・非オブジェクト・不正な `dir`・非有限数・隣接バーの端点不整合を `W-LAYOUT-DISCARDED` で破棄して自動生成へフォールバックするようにした                               |
| テスト | `tests/renderer/v030-stage2-save.test.ts`                         | 4-2（2件）・4-5（2件）・4-6（1件）・4-7（2件）の計 7 テストを追加                                                                                                                                                   |

- **検証**: `tsc` 3設定・`build-renderer.mjs`・`depcruise`・`vitest`（127 ファイル・1305 件）すべて pass。
- **実機確認（2026-11-20、ユーザー確認）**: 問題なし。**段2 は完了。**

## 段3 の結果（2026-11-20、実機確認完了 2026-11-20）

描画と画面 UI の整備（3-1・3-11・2-1・2-7・2-8・2-9・2-18・2-19）を実装した。

| 相違# | 変更ファイル | 内容 |
| --- | --- | --- |
| 3-1 | `src/renderer/render/region-outlines.ts` | リージョンごとの外接1矩形をやめ、各セル矩形（マージン込み）の和集合を座標圧縮格子で求め、外部と接する外周線分のみ（同一直線の隣接辺は結合）を出力するように変更 |
| 3-11 | `src/renderer/render/cell-renderer.ts` | ポート三角記号を底辺 `3 mm`・高さ `2.598 mm` に `MM_TO_PX * zoom` を掛けるズーム追従寸法に変更し、呼び口（`cport`＝外向き）・受け口（`eport`＝内向き）を向きで区別するように変更 |
| 2-18 | `src/renderer/app/navigator-panel.ts` | ナビゲータ SVG 内に可視セル矩形（`.navigator-cell`）と可視結合の折れ線（`.navigator-join`）の縮小表示を追加 |
| 2-1・2-9 | `src/renderer/index.html`, `src/renderer/app/shell.ts` | 廃止済みの「表示」メニュー（`#panel-visibility`）と `PanelVisibilityView` 配線を削除し、ツールバー・プロパティ・ステータスを常時表示とした |
| 2-8 | `src/renderer/index.html`, `src/renderer/app/shell.ts` | ツールバーに `#toolbar-mode`（「選択」「セル新規作成」）ボタンを追加し、セルタイプ一覧ダイアログを閉じていてもモード切替でき、ストアと同期するようにした |
| 2-7 | `src/shared/ipc-types.ts`, `src/main/app-settings.ts`, `src/main/tool-settings.ts`, `src/renderer/app/store.ts`, `src/renderer/app/file-actions.ts`, `src/renderer/index.html`, `src/renderer/app/shell.ts` | 用紙のアプリケーション既定（`defaultPaperSize` / `defaultPaperOrientation`）の永続化と起動時復元、ツールバーの「既定に設定」ボタン、`newDocument()` での既定用紙適用を実装 |
| 2-19 | `src/renderer/app/diagnostics-panel.ts`, `src/renderer/index.html` | 診断一覧を「種別・該当箇所・メッセージ・操作」の 4 列表（`table.diag-table`）に変更し、ジャンプ可能行に「ジャンプ」ボタンを配置（行クリックと 10 件高さ上限を維持） |
| テスト | `tests/renderer/v030-stage3a-render.test.ts`, `tests/renderer/v030-stage3b-ui.dom.test.ts`, `tests/renderer/stage1-diagnostics.dom.test.ts`, `tests/renderer/shell.dom.test.ts` | 段3A（5件）・段3B（4件）のテストを追加し、旧仕様テスト（4列表化・表示メニュー廃止）を更新 |

- **検証**:
  - `tsc`（`tsconfig.renderer.json`・`tsconfig.renderer-tests.json`・`tsconfig.main.json`）: いずれも終了コード 0
  - `node scripts/build-renderer.mjs`・`build:main`: 終了コード 0
  - `npm run depcruise`: 違反なし（164 modules, 608 dependencies）
  - `vitest run --maxWorkers=2`: **129 ファイル・1312 件成功**（5 件スキップ）、終了コード 0
- **実機確認（2026-11-20、ユーザー確認）**: リージョン矩形の和集合表示を含め確認完了・問題なし。**段3 は完了。**

## 仕様書反映・リリース完了（2026-11-20）

- 関連仕様書（[[TECSCDE-DT外部仕様 - 03 画面構成|外部 03]]・[[TECSCDE-DT-EL内部仕様 - 05B 色に依存しない状態表示|内部 05B]]・[[TECSCDE-DT-EL内部仕様 - 09C tecsgen版の確認|内部 09C]]）を V0.3.0 実装内容へ更新済み。
- コミット・タグ・push（`origin`: `toppers/tecscde-dt-el`）:
  - `e5b7f3a`: `feat(log): separate diagnosis/error/debug logs and update samples`（先行変更を別コミットとして分離）
  - `c9cd246`: `feat: implement V0.3.0 (info dialog, 5B legend bar, save hardening, region union & UI)`
  - `03b1faf`: `chore: bump version to 0.3.0`（`package.json`・`package-lock.json`、最終検証全 pass 後にコミット）
  - タグ `v0.3.0`（annotated tag）を `03b1faf` に作成し、`origin` へ `main` と `v0.3.0` を push 済み。

## Related

- [[TECSCDE-DT-EL実装 — V0.3.0 実装計画 — 2026-11-19|V0.3.0 実装計画]]
- [[TECSCDE-DT-EL実装]]

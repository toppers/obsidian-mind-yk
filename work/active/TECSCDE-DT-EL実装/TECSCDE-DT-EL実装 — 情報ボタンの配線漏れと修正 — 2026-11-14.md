---
date: 2026-11-14
description: "v0.2.2 までの「情報」ボタンが、仕様の「情報」ダイアログ(tecsgen設定・Cプリプロセッサ設定・CDL一覧作成)でなく旧バージョン情報に繋がっていた不具合と、その修正の記録。"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
---

# TECSCDE-DT-EL — 「情報」ボタンの配線漏れと修正（2026-11-14）

[[TECSCDE-DT-EL実装]]の Related。V0.2.1 の実施記録（[[TECSCDE-DT-EL実装 — V0.2.1 実装計画 — 2026-11-12]]）に残す不具合と修正。仕様は変えていない（実装を仕様に合わせた）。

## 現象

ツールバーの「情報」ボタンを押すと、バージョン情報だけの旧ダイアログが開いた。仕様（[[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成|内部仕様 02B 2B.2]]、[[TECSCDE-DT外部仕様 - 03 画面構成|外部仕様 3.8]]）が定める「情報」ダイアログ — バージョン情報に加えて、tecsgen 設定、C プリプロセッサ設定（09E）、Plugin 型の取り込み方式、CDL ファイル一覧の作成 — には、ボタンから届かなかった。確認した版は `v0.2.2`（実装リポジトリ `E:\Ccur\typescript\TECSCDE-DT-EL`）。

## 原因（実装のコード読解、2026-11-14）

| 項目 | 内容 |
|---|---|
| ボタン | `src/renderer/index.html` の `<button data-action="about">情報</button>` |
| 振り分け | `src/renderer/app/shell.ts` の `runAction` の `case "about":` が、旧ダイアログ `AboutDialogView`（`about-dialog.ts`、90 行）を開いていた |
| 届かなかった実体 | `InformationDialog`（`information-dialog.ts`、611 行。DOM は `createElement("dialog")` で動的に作り、`#information-dialog`）。`case "information":` はあるが、その動作を出すボタンが無かった |

- **混入の経緯は推定（inferred）:** V0.2.0 の段1（設定基盤）で `InformationDialog` を足したときに、ボタンの付け替えが漏れた。コミット履歴は確認していない。
- **検証が見逃した理由は未確認（TBC）:** 段1 の実機 Electron 検証（23 項目）は通っていた。検証が `information` の動作を直接呼んでいた可能性があるが、検証スクリプトの中身は読んでいない。

## 修正

実装リポジトリ `main` の `badc54d`（`fix: open the information dialog from the toolbar's "情報" button`、2026-11-14）。

- `src/renderer/app/shell.ts`: `case "about"` を、設定の入口（`settings`）があるときは `InformationDialog` を開くようにした。ないとき（テスト用）は、従来の `AboutDialogView` にもどる。
- `tests/renderer/information-button.dom.test.ts`（新規、2 件）: 実物の `index.html` を使い、「情報」という文字のボタンを押して確かめる。
- **テスト先行:** 修正前は 1 件目が失敗（RED）、修正後は通過（GREEN）。
- **`npm run check`:** 型検査とビルド、全テスト（118 ファイル通過・1 スキップ、1,198 件通過・5 スキップ）、依存境界（違反なし）が通った。途中で、テストの型エラー（`NodeListOf` のスプレッド展開）が 1 件出て、`Array.from` に直した。

## 同種の取りこぼしの点検

`runAction` の `case`（25 件）と `index.html` のボタン（23 件）を突き合わせた（`runAction("…")` の呼び出しはコード中に 0 件。キー割り当てなど別の入口は見ていない）。**ボタンのない動作は、`information`（修正済み）と `openFolder` の 2 件。** `openFolder` は、V0.2.0 で「フォルダを開く」が「ファイル」ボタン（`openFileBrowser`）に変わった後の旧入口が残っている可能性がある（推定、意図的かは未確認）。

## 未了

- **実機（Electron）での確認:** DOM テストで、実物の `index.html` と `AppShell` を組んで確かめた範囲。実機で「情報」を押し、設定欄が出ることを確認する。
- **実装リポジトリの push と、`v0.2.3` としての出し直し:** `v0.2.2` に含まれていた不具合。公開済みのタグは付け替えない（[[TECSCDE-DT-EL実装 — V0.2.0 実装計画 — 2026-11-09|V0.2.0 実装計画]]の進め方）。
- **ツールチップ:** ボタンの `title` は「バージョン情報を表示する」のまま（`index.html` の 1 行）。実態に合わせるか未決。
- **`openFolder`:** 旧入口として消すか、残すか。
- **再発防止（案）:** ボタンから各ダイアログへ届くことを確かめるテストを、ダイアログごとに持つ（今回の新規テストと同じ形）。

## Related

- [[TECSCDE-DT-EL実装]] — 実装のハブ
- [[TECSCDE-DT-EL実装 — V0.2.1 実装計画 — 2026-11-12]] — V0.2.1 の計画
- [[TECSCDE-DT-EL内部仕様 - 09E V0.2.1 Cプリプロセッサ設定と失敗詳細]] — 「情報」ダイアログの C プリプロセッサ設定

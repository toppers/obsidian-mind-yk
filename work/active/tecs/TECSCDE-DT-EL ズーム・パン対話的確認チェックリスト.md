---
date: 2026-09-21
description: "TECSCDE-DT-EL実装でSVG幾何・ズーム/パンの対話的目視確認がまだ未実施のため、実機electron .でユーザーが確認する手順をチェックリスト化したもの"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
---

# TECSCDE-DT-EL ズーム・パン対話的確認チェックリスト

## Context

[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]の第5・6章（`render/`・`view-state/`）は2026-09-09にヘッドレステスト（happy-dom）で配線済みだが、**SVG幾何・ズーム/パンのスクロール連動の実挙動は一度も対話的に目視確認されていない**（2026-09-10のスモークテストで「起動と描画ツリー生成までは確認、対話的な目視は未実施」と明記されたまま）。09-20の4ラウンド対話確認は保存・Undo/Redo・結合作成・tecsgen実行・Cut/Copy/Paste・検索・診断パネルを対象としており、ズーム/パンは対象外だった。

happy-domはレイアウトを持たないため、この種の「見た目が正しいか」はheadlessテストで構造的に検証できない——2026-09-20に発見したCSP/座標変換バグと同じ理由（[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装#2026-09-16以降の詳細ログ]]参照）。実際の操作・目視はユーザー自身が行う必要がある。

## 実行方法

```
cd E:\Ccur\typescript\TECSCDE-DT-EL
npm start
```

## 確認項目

### ズーム
- [x] マウスホイール（またはズームボタン）でズームイン/アウトした際、**カーソル位置（ズームの固定点）が画面上で動かないか**——`pan-scroll.ts`の`panCenter`計算が正しければ、ズーム前後でカーソル下の同じセルが同じ画面座標に留まるはず。**2026-09-21確認**: Ctrl+ホイールでのズームは左上を固定点として動作するバグを発見。原因は用紙がビューポートより小さい時に`scrollForPanCenter`が常にスクロール位置を0にクランプし、`#canvas-scroll`にCSS中央寄せが無かったこと（`zoomAt`のポインタ固定点計算自体は正しかった）。コミット`566de2e`で修正済み——[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 07 表示機能|外部仕様7.1.2]]が現行版の既知バグとして名指しで禁止する挙動の再発だった。詳細は[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]のAction Items参照。
- [x] ズーム倍率のライブ表示は正しく更新されているか。**2026-09-21確認**: ツールバーの「−」「100%」「＋」の「100%」は現在倍率のライブ表示ではなく`zoomReset`ボタンの固定ラベルだったため一見バグに見えたが、実際のライブ表示（画面下部ステータスバー`#status-zoom`）はデバッグログで正しい更新を確認済み（バグではなくUI表記の誤解）。副産物としてElectronのネイティブCtrl+ホイール光学ズームを`setVisualZoomLevelLimits(1, 1)`で無効化（コミット`affd8f3`、予防的対応）。
- [ ] ズームの上限・下限（`ZOOM_MAX`/`ZOOM_MIN`、`view-state.ts`）に達したときに不自然な挙動（飛び・ガタつき）がないか。
- [ ] ズーム後にセルをドラッグして選択・移動が正しい座標で行われるか（ズーム後の座標変換ズレがないか）。

### パン
- [ ] スクロールバー操作・トラックパッド2本指スクロールで図がスムーズにパンするか。
- [ ] パン中にセルの見た目の位置とヒットテスト（クリック判定）がずれないか（`HitTester`は`CanvasView`のズーム換算のみを持つ設計のため、パン位置とのズレが起きやすい箇所）。
- [ ] ナビゲータパネルのクリック→パン変換（`computeNavigator`）で、クリックした位置が画面中央付近に来るか。

### 複合
- [ ] ズームした状態でパンし、さらにセルをドラッグ移動——3つの座標変換が重なった状態で破綻しないか。

## 発見した問題があれば

[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]のAction Itemsへ、09-20のバグ報告と同じ形式（症状→原因→修正→コミット→テスト件数）で追記する。

## Related

- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]] — 本チェックリストの対象実装
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]] — 第5・6章（描画・表示制御）の設計
- [[reference/Note/daily/2026-09-21|2026-09-21日次ノート]] — チェックリスト作成の経緯

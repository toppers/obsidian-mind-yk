---
date: 2026-10-22
description: "TECSCDE-DT-EL内部仕様書 第7章7.10節（エクスポート: SVG・PNG・PDF）の設計のたたき台 — renderer で SVG を組み立て、PNG は canvas、PDF は main の非表示ウィンドウで生成する案と、未決事項"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - draft
---

Domain note [[TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計]]（7.10節）。**たたき台**。2026-10-22に表示設定の引き継ぎ・枠線とファイル名・入口・PDF の対応を決定した（末尾「決定済み」）。ソースの確認は読解のみ（`render/svg-renderer.ts`、`render/view.ts`、`model/paper.ts`、`index.html`、`main/file-service.ts`）で、動作は確かめていない。未決は末尾の「未決事項」に集めた。

## 7.10 エクスポート（SVG・PNG・PDF）

### 7.10.1 位置づけ

- 外部仕様: [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|DT外部仕様5.6節]]（SVG・PNG は対応、PDF は「対応してよい」）と、親仕様5.6.2（出力範囲選択、出力先選択、用紙の縦向き）。PDF は2026-10-22に「対応」と決め、5.6節の PDF の行を改めた（7.10.9）。
- 現状: 書き込みの下回り（`FileService.exportFile`、IPC `file:export`）だけがあり、生成処理・UI・保存先ダイアログは無い（[[TECSCDE-DT-EL実装 — 外部仕様と内部仕様・実装の差分一覧|差分一覧]]#6）。

### 7.10.2 全体構成

| 段階 | 担当 | 内容 |
|---|---|---|
| 1. 設定 | renderer | 形式（SVG／PNG／PDF）・出力範囲・PNG倍率を選ぶ（7.10.3） |
| 2. 保存先 | main | 形式別のフィルタつき保存ダイアログ（`file:chooseExportPath`、新設）。取り消したら以降をしない |
| 3. SVG 生成 | renderer | 画面と別の、切り離した`<svg>`に描いて文字列にする（7.10.4）。3形式すべての元になる |
| 4. 形式変換 | SVG: なし／PNG: renderer の canvas／PDF: main の非表示ウィンドウ | 7.10.5・7.10.6 |
| 5. 書き込み | main | 既存の`file:export`（`writeAtomic`）。PDF は専用の`file:exportPdf`（7.10.6） |

保存先を先に決めるのは、PNG のラスタライズや PDF の生成が重いので、取り消しのときに無駄な処理をしないため。出力先に既存ファイルがあるときの上書き確認は、OS の保存ダイアログに任せる（現行版は確認なしで`File.unlink`していた）。書き込みは`writeAtomic`なので、失敗しても既存のファイルは失われない。

### 7.10.3 設定（renderer）

ツールバーに「エクスポート」ボタンを置き、押すと小さなオプションダイアログ（DOM）を出す。

| 項目 | 値 | 既定 |
|---|---|---|
| 形式 | SVG／PNG／PDF | SVG |
| 出力範囲 | 用紙に合わせる／図の内容に合わせる | 用紙に合わせる |
| PNG倍率 | 1×／2×／4×（96dpi 基準） | 2× |

出力先は次の保存ダイアログで選ぶ。既定のファイル名は、編集中のファイル名の拡張子を`.svg`／`.png`／`.pdf`に置き換えたもの（未保存なら`untitled`）。

### 7.10.4 SVG の生成（renderer、`export/svg-exporter.ts`新設）

```ts
interface ExportOptions {
  readonly range: 'paper' | 'content';
  readonly showSignatureNames: boolean;       // 画面の設定をそのまま引き継ぐ（決定①）
  readonly hiddenRegionIds: ReadonlySet<RegionId>;   // 同上
}

class SvgExporter {
  /** 画面の SVG とは別の、切り離した <svg> に描いて、単独で開ける SVG 文字列を返す。 */
  static build(doc: TecscdeDocument, options: ExportOptions, title: string): ExportedSvg;
}
interface ExportedSvg { readonly svg: string; readonly widthMm: number; readonly heightMm: number; }
```

1. 切り離した`<svg>`を作り、既存の`SvgRenderer`で描く。表示状態は`CanvasView { zoom: 1, gridVisible: false, showSignatureNames, hiddenRegionIds }`、選択は`SelectionState.empty()`、結合のプレビューなし。これで画面のズーム・選択・グリッドが混ざらず、座標は 96dpi の px（1mm = `MM_TO_PX`）で固定される。
2. **範囲**: `paper`は`doc.paper.contentSize()`（余白10mmを除いた領域）に余白10mmを足した用紙全体。`content`は表示中のセルと結合（バーを含む）のモデル座標から外接矩形を求め、周囲に5mmの余白を足す。外接矩形は`getBBox()`ではなくモデルから計算する（切り離した要素ではレイアウトが無く`getBBox()`が0になるため）。
3. **単位**: ルートに`width="{W}mm" height="{H}mm" viewBox="0 0 {W·MM_TO_PX} {H·MM_TO_PX}"`を付ける。印刷・PDF で実寸になり、画像として開いても比率が保たれる。
4. **スタイル**: 画面の見た目は`index.html`のCSS（`.cell-rect`など）に依存しており、`<svg>`だけを書き出すと白黒の既定に戻る。そこで、`<svg>`内に`<style>`を埋め込む。CSS の元を 1 か所にするため、SVG 関連のルール（`.cell-rect`・`.cell-label`・`.celltype-label`・`.port-symbol*`・`.join-line`・`.signature-label`）を`render/svg-styles.ts`の定数に移し、`index.html`にはアプリ起動時に注入する（`.grid-line`・`.selection-outline`・`.join-preview`・`.rubber-band`はエクスポートに含めない。`.export-frame`・`.export-filename`を加える）。`var(--accent)`を使うルールは含めないので、変数の解決は要らない。
5. **文字列化**: `XMLSerializer`で文字列にする。セル名などCDL由来の文字列は、シリアライザがエスケープする。`<title>`にファイル名を入れる。
6. **枠線とファイル名**（決定②）: 現行版が用紙の外周に描いていた枠線と、用紙の右下に描いていたファイル名を引き継ぐ。「用紙に合わせる」では、余白の内側（内容領域）の外周に矩形の枠線（`.export-frame`）を描き、用紙の右下の余白部分に編集中のファイル名（`.export-filename`、右寄せ、拡張子つき。未保存なら`untitled`）を描く。「図の内容に合わせる」では、枠線もファイル名も描かない（現行版は用紙固定の出力だけだったため、この対応は解釈による。要確認）。2つのクラスのスタイルも`svg-styles.ts`に含める。

### 7.10.5 PNG（renderer）

1. 7.10.4 の SVG 文字列を`Blob`（`image/svg+xml`）にして`Image`へ読み込む。
2. `canvas`を`幅px × 倍率`、`高さpx × 倍率`で作り、背景を白で塗ってから描く。
3. `canvas.toBlob('image/png')` → `ArrayBuffer` → `Uint8Array`にして、`file:export`でmainへ渡す。
4. **上限**: Chromium の canvas には一辺・面積の上限がある。`幅 × 高さ × 倍率²`が上限を超えるときは、ラスタライズせずにエラー（`E-EXPORT-TOO-LARGE`、倍率を下げる案内）にする。上限の具体値は実装時に実測して決める（未決①）。
5. フォントは画面と同じシステムフォント。埋め込みはしない。

### 7.10.6 PDF（main、`main/pdf-exporter.ts`新設）

PDF の外部ライブラリは入れず、Electron の`webContents.printToPDF`を使う（外部仕様5.6が挙げる手段）。

1. mainは非表示の`BrowserWindow`を作る。`show: false`、`webPreferences`は`javascript: false`・`sandbox: true`・`contextIsolation: true`・preloadなし。ネットワークを使わない。
2. 7.10.4 の SVG 文字列を埋め込んだ HTML（`@page { size: …; margin: 0 }`、`body { margin: 0 }`）をdata URLで読み込む。
3. `printToPDF`に、用紙に合わせるなら用紙名（`A4`／`A3`／`A2`）と向き（`landscape`は`orientation === 'LANDSCAPE'`）、内容に合わせるなら`{ width, height }`（インチ。mm から換算）を渡す。`printBackground: true`、余白は 0（SVG 側に余白を含めてあるため）。
4. 結果の`Buffer`を`writeAtomic`で書き、非表示ウィンドウを閉じる（`finally`）。
5. IPC: `file:exportPdf(path, svg, page)`（新設）。`page`は`{ kind: 'paper', size, orientation }`または`{ kind: 'custom', widthMm, heightMm }`。

SVG の生成は renderer、PDF への変換だけ main にするのは、描画ロジック（`SvgRenderer`）を main へ持ち込まず、DOM を使う処理を renderer に閉じるため。

### 7.10.7 IPC と型の変更

| 変更 | 内容 |
|---|---|
| `file:chooseExportPath`（新設） | `(format, suggestedName) => Promise<string \| null>`。`showSaveDialog`に形式別の`filters` |
| `file:export`（既存） | `data`の型を`string`から`string \| Uint8Array`へ（SVG は文字列、PNG はバイト列）。`FileService.exportFile`も`Buffer \| string`にする（7.1節の記述に合わせる。現行のソースは`string`のみで、PNG を渡せない） |
| `file:exportPdf`（新設） | 7.10.6 |
| preload・`TecscdeApi` | 上の3つを`window.tecscde.file`に追加 |

### 7.10.8 エラーと診断

| 場合 | 扱い |
|---|---|
| 保存ダイアログの取り消し | 何もしない |
| 書き込み失敗（権限、ディスク） | `E-EXPORT-FAILED`。既存のファイルは`writeAtomic`により残る |
| PNG が大きすぎる | `E-EXPORT-TOO-LARGE`（7.10.5） |
| PDF の生成失敗 | `E-EXPORT-FAILED`。非表示ウィンドウは必ず閉じる |

診断は第8章の一覧に出す（コード表への追加が要る）。ドキュメントが空（セルなし）のときは、用紙に合わせるなら出力し、内容に合わせるなら用紙全体にフォールバックする。

### 7.10.9 外部仕様への影響

- 5.6節の PDF の行を「対応」へ改めた（2026-10-22。以前は「対応してよい（unverified／実装時に判断）」）。実現手段として`printToPDF`を明記し、画面の表示設定の引き継ぎ（決定①）と、枠線・ファイル名（決定②）も外部仕様に書いた。
- 出力範囲・倍率・既定ファイル名・上書き確認は、親仕様5.6.2の規定の具体化であり、追加の外部仕様は小さい。

### 7.10.10 実装単位案

| # | 内容 | 検証 |
|---|---|---|
| E1 | `svg-styles.ts`への CSS の移動、`SvgExporter`、`file:chooseExportPath`、ツールバーとダイアログ（SVG のみ） | 単体テスト（範囲、単位、スタイル埋め込み）、SVG をブラウザで開いて目視 |
| E2 | PNG（canvas、倍率、上限エラー） | テスト（PNG のマジック、サイズ）、目視 |
| E3 | PDF（`pdf-exporter`、`file:exportPdf`） | テスト（`printToPDF`はモック）、実機でページサイズ・向き・実寸を確認 |
| E4 | `exportFile`の型修正、診断コード、外部仕様 5.6 節の改訂 | 既存テストの更新 |

## 決定済み（2026-10-22）

1. **画面の表示設定の引き継ぎ**: シグニチャ名の表示とリージョンのフィルタ（非表示）は、画面に見えているとおりにエクスポートへ引き継ぐ。ダイアログでは選ばせない。
2. **枠線とファイル名**: 現行版の仕様を引き継ぐ。適用範囲は「用紙に合わせる」のみ（7.10.4の6.）。
3. **入口**: エクスポートの入口はツールバーのボタンのみ。File メニューは設けない（現行実装はアプリケーションメニューを外している: `Menu.setApplicationMenu(null)`）。
4. **PDF の対応**: 対応する（外部仕様5.6節）。

## 未決事項

1. **PNG の上限**: Chromium の canvas の実効上限を実測して、エラーにする閾値を決める。
2. **PDF のページ指定**: `printToPDF`の`pageSize`にカスタムサイズ（インチ）を渡す際の丸めと、内容に合わせる場合の 1 ページ収まりを実機で確認する。
3. **CSS の移動の影響**: `index.html`から SVG 用ルールを`svg-styles.ts`へ移すと、画面のスタイルの出どころが変わる。画面とエクスポートで同じ見た目になるかを E1 で確認する。

## Related

- [[TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計]] — 7.1節（`FileService`）、7.2節（IPC）
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様 第5章（5.6節）]]
- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 05B ファイル操作（後半）|TECSCDE外部仕様 第5章後半（5.6.2節、JS版の規定）]]
- [[TECSCDE-DT-EL実装 — 外部仕様と内部仕様・実装の差分一覧]] — #6
- [[TECSCDE-DT-EL内部仕様]]（目次）

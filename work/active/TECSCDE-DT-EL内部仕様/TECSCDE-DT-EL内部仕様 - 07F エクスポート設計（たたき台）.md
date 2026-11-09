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

**2026-11-07、監査#15による契約更新**: 「画面に見えているとおり」はシグニチャ名と非表示リージョンだけでなく、以下に列挙する図の表示状態全体を引き継ぐ。7.10.4の表示スナップショットと7.10.11の受入条件を追加した。今回の更新は内部設計の具体化であり、実装済み・出力検証済みを意味しない。

## 7.10 エクスポート（SVG・PNG・PDF）

### 7.10.1 位置づけ

- 外部仕様: [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|DT外部仕様5.6節]]（SVG・PNG は対応、PDF は「対応してよい」）と、親仕様5.6.2（出力範囲選択、出力先選択、用紙の縦向き）。PDF は2026-10-22に「対応」と決め、5.6節の PDF の行を改めた（7.10.9）。
- 2026-10-22の設計作成時点の状態: 書き込みの下回り（`FileService.exportFile`、IPC `file:export`）だけがあり、生成処理・UI・保存先ダイアログは無かった（[[TECSCDE-DT-EL実装 — 外部仕様と内部仕様・実装の差分一覧|差分一覧]]#6）。この記録を2026-11-07現在の実装状態の確認結果として扱わない。

### 7.10.2 全体構成

| 段階 | 担当 | 内容 |
|---|---|---|
| 1. 設定 | renderer | 形式（SVG／PNG／PDF）・出力範囲・PNG倍率を選ぶ（7.10.3） |
| 2. 状態確定・保存先 | renderer・main | 形式・範囲の確定時に図の表示スナップショットを取得し、その後に形式別の保存ダイアログ（`file:chooseExportPath`、新設）を開く。取り消したら生成・書込をしない |
| 3. SVG 生成 | renderer | 確定したスナップショットを、画面と別の切り離した`<svg>`に描く（7.10.4）。3形式すべての元になる |
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
}
// 以下は契約案。描画シーンは画面とexportで共用する確定済み図形・文言・スタイル。
interface ExportSnapshot {
  readonly doc: TecscdeDocument;
  readonly title: string;
  readonly view: DiagramViewSnapshot;
  readonly scene: DiagramRenderScene;
  readonly legends: readonly DiagramLegendSnapshot[];
  readonly styles: ResolvedSvgStyles;
}

class SvgExporter {
  /** 画面の SVG とは別の、切り離した <svg> に描いて、単独で開ける SVG 文字列を返す。 */
  static build(snapshot: ExportSnapshot, options: ExportOptions): ExportedSvg;
}
interface ExportedSvg { readonly svg: string; readonly widthMm: number; readonly heightMm: number; }
```

1. **共通描画と状態の確定**: アプリ層が、画面描画と同じドキュメント・表示設定・構造判定結果を一組で取得し、`DiagramViewSnapshot`と`DiagramRenderScene`（案）を作る。場面ごとに可視性や色・強調を独自判定せず、`SvgRenderer`／各要素rendererと共通の図形生成を使う。Map・Set・配列等はコピーし、非同期の保存ダイアログ中にライブストアから変更されない値として保持する。生成対象はこの確定時点の図とする。`SelectionState.empty()`、`gridVisible: false`、カメラのzoom=1・pan=0で出力するが、それ以外の表示状態を既定値へ戻さない。
2. **範囲と境界計算**: `paper`はスナップショットの用紙全体（内容領域＋四辺10mm余白）を使う。`content`は、実際に出力する可視図形の境界を合成し、周囲に5mm余白を足す。セル本体だけでなく、ポート、表示中ラベル、セル名強調、状態記号、検索枠の張り出し、線幅、リージョン外周、可視の結合・スタブと先端記号を含める。非表示セル・両端非表示結合や、スタブに置き換えた元の全結合経路は境界へ含めない。図形生成時のモデル座標と文字計測結果を画面・exportで共有し、切り離したDOMの`getBBox()`へ依存しない。凡例の配置後にその境界も合成する。
3. **単位**: ルートに`width="{W}mm" height="{H}mm" viewBox="0 0 {W·MM_TO_PX} {H·MM_TO_PX}"`を付ける。印刷・PDF で実寸になり、画像として開いても比率が保たれる。
4. **スタイル**: `render/svg-styles.ts`の共通ルールを使い、図に必要なスタイルを`<svg>`内へ埋め込む。セル・ポート・ラベル・結合に加え、リージョン帯、スタブ、セル名強調、active、赤い結合、リージョン外周、RO・!・U、検索ハイライトのルールを含める。色・フォント等のCSS変数はスナップショット取得時の図用テーマ値で具体化し、外部の`index.html`や未解決の`var(--accent)`に依存させない。選択・ホバーの一時的な装飾を通常図形のスタイルへ混入させない。`.grid-line`・選択枠／ハンドル・`.join-preview`・`.rubber-band`は出力しない。
5. **文字列化**: `XMLSerializer`で文字列にする。セル名などCDL由来の文字列は、シリアライザがエスケープする。`<title>`にファイル名を入れる。文字計測と描画は画面と同じ利用可能なフォントを使う。フォント準備を待つ必要がある場合はスナップショット確定前に待ち、境界計算後のフォント差し替えで文字を切らない。
6. **枠線とファイル名**（決定②）: 「用紙に合わせる」では、内容領域の外周に矩形の枠線（`.export-frame`）を描き、用紙の右下の余白部分に確定時点の編集中ファイル名（`.export-filename`、右寄せ、拡張子つき。未保存なら`untitled`）を描く。「図の内容に合わせる」では両方とも描かない（外部5.6節で確定済み）。両クラスのスタイルも埋め込む。

**引き継ぐ状態と責務**:

| 表示状態 | スナップショットに含める内容 |
|---|---|
| リージョン／ネームスペースのフィルタ | 解決済み非表示リージョンと可視セル集合。祖先の非表示も含む6Bの規則を共用 |
| activeOnly | リージョン条件との積集合である可視集合。exportだけ全セル表示へ戻さない |
| 色分け | オン／オフと確定したリージョン色Map。画面と異なる順序で色を再割り当てしない |
| シグニチャ名・セル名強調 | 表示／非表示、文字サイズとセルタイプ名の抑制を含む現在の設定 |
| セルの通常状態 | 編集可否・不完全・未結合の色、5BのRO・!・Uとその理由・件数 |
| active背景 | 現在のactive判定と採用された背景描画 |
| 指定ポートの結合強調 | 現在の強調結合IDと赤色表示。選択状態と混同して除外しない |
| リージョン矩形モード | 現在の有効／無効と、画面と同じ計算で得た外周図形・色 |
| 検索強調 | 第6章6.4の同じ`SearchHighlights`を引き継ぐ。選択とは独立した表示なので出力に残す |

これらを`DiagramViewSnapshot`とシーンへ含め、7.10.4の旧2項目だけの`ExportOptions`を使う経路は残さない。検索結果の再検索・ジャンプ・フィルタ緩和をexportから起動せず、可視の検索ハイライトだけを描く。結合の可視性は6Bと6Cの同じ規則を使い、一端非表示ならスタブとその先端横線を描き、両端非表示なら描かない。検索強調と赤い結合強調が併存する場合も、画面と同じ描画順を使う。

シーンの図形と境界は図の座標（mm）で保持し、画面のカメラ変換を焼き込まない。内容範囲では最終境界の左上を余白5mmの位置へ移す共通の出力変換を一度だけ適用し、負座標や張り出した文字・枠も切らない。用紙範囲では既存の用紙・内容領域の座標変換を使う。

activeの色合成は[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置|6C.2]]で決定済み（2026-11-08。塗りと枠を別の軸とする）で、export側は同じ状態スナップショットから解決済みの塗り・枠の色をSVGへ埋め込む（CSSクラスの参照だけに頼らない）。リージョン矩形（親子の重なり・色・余白、6C.5）と結合強調（直接の結合のみ、6C.3）も2026-11-08に決定済みで、export側は同じスナップショットの確定描画結果（線分・色・強調する結合ID）を共用し、独自に再計算しない。これらの表示モードは`.cde`にも前回セッションにも保存しないが、現在の表示は画像へ反映する（別の契約）。

**凡例の出力（内部設計案）**: 表示中のリージョン凡例と5Bの「セルの状態」凡例も、確定した項目・色・記号・文言からSVGへ描き直す。固定HTMLをそのままコピーせず、非表示リージョンを凡例だけに復活させない。ツールバー・パネル・ダイアログ・検索結果一覧・スクロールバー等のアプリ操作UIは出力対象にしない。

- 用紙範囲では内容領域の左下に凡例ボックスを配置し、既存の画面上の凡例と同じく図上に重ねる。複数の凡例は見出し付きで縦に並べ、必要なら複数列へ折り返す。枠線と右下余白のファイル名を覆わない。
- 内容範囲では、図の外接矩形の下へ5mm空けて凡例を配置し、その分も出力境界へ含める。固定viewportの左下位置を持ち込まない。
- 読み取り可能な凡例が用紙内に収まらない場合は、黙って項目を削らず出力失敗として通知する。内容範囲への変更を案内する。図も凡例も空なら既存の用紙全体へのフォールバックを使う。

**画面カメラと処理中の変更**: 用紙／内容の出力範囲は画面viewportのスクリーンショットではない。パン・ズーム・画面端によるクリップは持ち込まない。ドラッグや結合作成の未確定プレビューは図の確定状態ではないため、操作中は出力開始を抑止し、確定またはキャンセル後に取得する。出力開始後に図・表示・検索語・タイトルが変わっても、この処理のスナップショットは差し替えない。出力のための再配置・自動保存・選択解除・ストア更新は行わない。

### 7.10.5 PNG（renderer）

1. 7.10.4で同じスナップショットから確定したSVG文字列を`Blob`（`image/svg+xml`）にして`Image`へ読み込む。PNG用に表示設定を取り直さない。
2. `canvas`を`幅px × 倍率`、`高さpx × 倍率`で作り、背景を白で塗ってから描く。
3. `canvas.toBlob('image/png')` → `ArrayBuffer` → `Uint8Array`にして、`file:export`でmainへ渡す。
4. **上限**: Chromium の canvas には一辺・面積の上限がある。`幅 × 高さ × 倍率²`が上限を超えるときは、ラスタライズせずにエラー（`E-EXPORT-TOO-LARGE`、倍率を下げる案内）にする。上限の具体値は実装時に実測して決める（未決①）。
5. フォントは画面と同じシステムフォント。埋め込みはしない。

### 7.10.6 PDF（main、`main/pdf-exporter.ts`新設）

PDF の外部ライブラリは入れず、Electron の`webContents.printToPDF`を使う（外部仕様5.6が挙げる手段）。

1. mainは非表示の`BrowserWindow`を作る。`show: false`、`webPreferences`は`javascript: false`・`sandbox: true`・`contextIsolation: true`・preloadなし。ネットワークを使わない。
2. 7.10.4で同じスナップショットから確定したSVG文字列を埋め込んだHTML（`@page { size: …; margin: 0 }`、`body { margin: 0 }`）をdata URLで読み込む。mainで表示設定を再構築しない。
3. `printToPDF`に、用紙に合わせるなら用紙名（`A4`／`A3`／`A2`）と向き（`landscape`は`orientation === 'LANDSCAPE'`）、内容に合わせるなら`{ width, height }`（インチ。mm から換算）を渡す。`printBackground: true`、余白は 0（SVG 側に余白を含めてあるため）。
4. 結果の`Buffer`を`writeAtomic`で書き、非表示ウィンドウを閉じる（`finally`）。
5. IPC: `file:exportPdf(path, svg, page)`（新設）。`page`は`{ kind: 'paper', size, orientation }`または`{ kind: 'custom', widthMm, heightMm }`。

SVG の生成は renderer、PDF への変換だけ main にするのは、描画ロジック（`SvgRenderer`）を main へ持ち込まず、DOM を使う処理を renderer に閉じるため。

### 7.10.7 IPC と型の変更

**型の統一（2026-11-08、監査#28）**: プロセス境界では次の型を正とする。renderer・preload・共有型にNodeの`Buffer`を持ち込まず、mainのファイル書き込み用にだけ変換する。これは内部契約の更新であり、実装適合は未確認。

```ts
// shared/ipc-types.ts
export type ExportData = string | Uint8Array;
// TecscdeApi.fileのexportメソッド
// export(path: string, data: ExportData): Promise<void>;

// preload/index.mts：同じExportDataを型だけimportし、値はそのまま中継
// export: (path: string, data: ExportData): Promise<void> =>
//   ipcRenderer.invoke('file:export', path, data)
```

| 段階 | 型と処理 |
|---|---|
| rendererの`FileGateway.export` | `ExportData`。SVGはstring、PNGはUint8Arrayで渡す |
| preload・共有API・`file:export` | 同じ`ExportData`を中継。文字列化・base64化・Buffer化はしない |
| mainのIPC受信・`FileService.exportFile` | stringまたはUint8Arrayであることを検査し、`ExportData`として受ける |
| main内の変換と原子的書込み | stringはUTF-8の文字列として、Uint8Arrayは`Buffer.from(data)`でバイト列をコピーして`writeAtomic`へ渡す |

バイト列をUTF-8として復号してから書き直さない。`Buffer.from(data.buffer)`ではなく、**渡されたUint8Arrayのビュー範囲だけ**をコピーし、`byteOffset`・`byteLength`の外側のバイトを混入させない。PDFは従来どおりmainの`printToPDF`が返すBufferをmain内で書き、IPCを通じてrendererへBufferを返す契約にはしない。

| 変更 | 内容 |
|---|---|
| `file:chooseExportPath`（新設） | `(format, suggestedName) => Promise<string \| null>`。`showSaveDialog`に形式別の`filters` |
| `file:export`（既存） | sharedの`ExportData = string \| Uint8Array`をrenderer・preload・IPC受信・`FileService.exportFile`で共用する。Bufferへの変換はmain内部の書き込み直前だけとする |
| `file:exportPdf`（新設） | 7.10.6 |
| preload・`TecscdeApi` | 上の3つを`window.tecscde.file`に追加 |

### 7.10.8 エラーと診断

| 場合 | 扱い |
|---|---|
| 保存ダイアログの取り消し | 何もしない |
| 書き込み失敗（権限、ディスク） | `E-EXPORT-FAILED`。既存のファイルは`writeAtomic`により残る |
| PNG が大きすぎる | `E-EXPORT-TOO-LARGE`（7.10.5） |
| PDF の生成失敗 | `E-EXPORT-FAILED`。非表示ウィンドウは必ず閉じる |
| 凡例を用紙内へ配置できない | `E-EXPORT-FAILED`。内容範囲での出力を案内し、項目を黙って省略しない |

診断は第8章の一覧に出す（コード表への追加が要る）。内容範囲の空判定はモデル内の総セル数ではなく、凡例を含む実際の出力図形が空かで行う。空なら用紙全体へフォールバックし、非表示セルを再表示して範囲を埋めない。

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

### 7.10.11 表示スナップショットの受入条件（2026-11-07、監査#15）

以下は実装時に満たす条件であり、今回の文書更新で実装テストを実行したという記録ではない。テストは`tests/renderer/`・`tests/main/`、3形式の目視記録と出力例は`tests/verification/`へ置く。

- シグニチャ名・セル名強調・色分け・親リージョン非表示・activeOnlyを個別と組み合わせで変更し、画面と出力の可視ID・色Map・ラベル設定が一致する。非表示セルを内容範囲へ含めない。
- 一端非表示の結合はスタブと横線だけを出力し、その範囲だけを境界へ含める。遠方の非表示端点まで出力領域を広げない。両端非表示は出力しない。
- active背景・赤い結合・リージョン矩形モード・RO／!／U・検索強調が画面と同じく併存する。選択状態を空にしても通常の状態記号・検索や結合強調を消さない。
- 検索中の出力で検索やジャンプを再実行せず、非表示ヒットのフィルタを緩和しない。グリッド・選択枠／ハンドル・プレビュー・ラバーバンドが出力されない。
- SVGの保存先選択中やPNG/PDF変換中にモデル・フィルタ・検索語・タイトルを変えても、開始時点の1組のスナップショットで出力する。現在の図・選択・dirty・履歴を変更しない。
- SVGを単独で開いてもスタイルと文字が欠けず、アプリのCSS変数へ依存しない。SVG・PNG・PDFの図形構成・色・凡例は共通のSVGに由来する。
- `ExportData`の型がrenderer・preload・mainで一致する。非ASCII文字を含むSVGはUTF-8で保存され、PNGの任意バイトはそのまま保持される。オフセット付きUint8Arrayのsubarrayを渡してもビュー外のバイトを含めず、不正な型は書き込み前に拒否する。renderer・preloadからBufferを生成しない。
- 内容範囲で、ラベル・検索枠・リージョン外周・状態記号・凡例を切らずに収める。画面のズーム・パン・ウィンドウ寸法を変えても、同じ用紙／内容の図を出力する。
- 用紙範囲は枠線とファイル名を描き、内容範囲は描かない。凡例は現在の項目だけを出力し、収まらない場合は黙って省略しない。
- 全セル非表示でも凡例があればその実出力の範囲を使い、図形も凡例も空の場合だけ用紙全体へフォールバックする。縦向き、PNG倍率、PDFページ寸法は既存の確認条件も維持する。

## 決定済み（2026-10-22）

1. **画面の表示設定の引き継ぎ**: 当初のシグニチャ名とリージョンフィルタに加え、2026-11-07の監査#15で7.10.4の表示状態全体を引き継ぐ契約へ具体化した。図の表示設定を出力ダイアログで選び直させない。
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

- [[TECSCDE-DT-EL内部仕様 - 監査対応 49-58 出力と検索]] — 該当する監査項目の契約補足（2026-11-09）。

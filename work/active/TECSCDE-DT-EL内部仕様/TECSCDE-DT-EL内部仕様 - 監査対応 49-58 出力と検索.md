---
date: 2026-11-09
description: "三者監査49〜58の内部仕様契約補足。既決要件と現行コードの差を区別する。"
project: TECS
quarter: Q4-2026
status: active
tags: [work-note, tecs, tecscde, spec]
---

# TECSCDE-DT-EL内部仕様 - 監査対応 49-58 出力と検索

[[TECSCDE-DT-EL内部仕様]]の補足。[[TECSCDE-DT外部仕様 - 監査対応 49-58 出力と検索]]と対になる。

2026-11-09の確定契約・実装境界を記す。関連する旧時点の実装記録を、今回のコードの適合確認として扱わない。既存の決定と未決事項（TBC）を維持し、未決を完成済みにしない。仕様を修正してもソース修正が必要な項目は未実装のままである。

## 監査49

**SVG・PNG・PDF出力、表示スナップショット、バイト列IPCが未実装**

[[TECSCDE-DT外部仕様 - 監査対応 49-58 出力と検索#監査49]]に対応する。

形式と範囲の確定時にdoc、表示、シーン、凡例、具体化したスタイルをコピーして単一ExportSnapshotへ固定する。別SVGへ共通描画を行い、可視図形・文字・線幅・状態記号・凡例まで境界に含め、用紙は四辺10mm、内容は周囲5mmを使う。PNGは同SVGをcanvasへ、PDFはmainの非表示printToPDFへ渡し、処理後はfinallyで閉じる。ExportData=string|Uint8Arrayを共有し、PNGを文字列化せず、mainのみBuffer化してビュー範囲だけを原子的に書く。非同期中にライブ状態を取り直さない。PNG上限の具体値とPDF実機丸め等のTBCは維持し、凡例を黙って省略せず失敗を通知する。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/shell.ts:257` — `runAction(action: string)`
- `src/renderer/gateways/file-gateway.ts:24` — `export(path: string, data: string)`
- `src/shared/ipc-types.ts:137` — `export(path: string, data: string)`

**受入条件**: 3形式、縦横/範囲/倍率、全表示状態・スタブ・凡例・CSS具体化を確認する。／出力中のdoc変更に影響されず、Uint8Arrayのsubarray/非ASCII、取消・書込失敗、PDF窓解放を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 07F エクスポート設計（たたき台）]]、[[TECSCDE-DT-EL内部仕様 - 05B 色に依存しない状態表示]]、[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]、[[TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧]]。

## 監査50

**位置情報だけの診断から、ソースの行・列へジャンプできない**

[[TECSCDE-DT外部仕様 - 監査対応 49-58 出力と検索#監査50]]に対応する。

DiagnosticにsourceRefと座標の基数・列単位を関連付け、producerアダプタとDiagnosticSourceRegistryが原位置、本文世代、実行時cwd、一致確認の有無を保持する。未検証の単位を生成元名だけで決めず、列不明は行のみ、行範囲外は原値と理由を表示する。DefinitionFileViewへ解析時本文または現在ディスクの別モードを渡し、CRLF・UTF8バイト・UTF16・サロゲート境界を検証する。main読込は副作用のないAPIを使い、図のopenPathを流用しない。要求トークンをawait前に発行し、古い完了や文書世代を無効化する。生成元snapshotがなければ利用不能とし、外部ツールを再実行しない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/diagnostics-panel.ts:68` — `private jumpTarget(d: Diagnostic)`
- `src/renderer/app/diagnostics-panel.ts:69` — `return d.relatedCellId !== undefined`
- `src/renderer/diagnostics/types.ts:15` — `export interface Diagnostic`

**受入条件**: 図IDのみ/位置のみ/両方/なし/古いID、複数source同名、相対cwdを確認する。／ASCII/日本語/絵文字/CRLF/EOF/不明単位/範囲外、本文変更、要求逆順、生成元消失を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 08B 診断位置へのソースジャンプ]]、[[TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計]]、[[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]。

## 監査51

**診断の図ジャンプが非表示フィルタを緩和しない**

[[TECSCDE-DT外部仕様 - 監査対応 49-58 出力と検索#監査51]]に対応する。

検索と診断の図ジャンプを、対象解決、必要なフィルタ緩和、選択、パンという共通アプリ層処理へ接続する。現在docに有効なセル/結合だけを対象とし、regionsToReveal相当で祖先と両端の和集合を求める。activeOnlyが対象を隠す場合の緩和は6Cの設計へ統合し、非表示集合を全消去しない。必要な表示状態を確定してから同じ対象を選択・移動し、更新途中で古いIDを再利用しない。図IDが消えていれば#50の位置fallbackへ進み、選択不能なIDを残さない。ソース表示経路とは分離し、診断一覧であることだけを理由にdocや履歴へコマンドを追加しない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/diagnostics-panel.ts:73` — `private jumpTo(index: number)`
- `src/renderer/app/diagnostics-panel.ts:79` — `this.store.setSelection(SelectionState.ofCells`
- `src/renderer/app/search-box.ts:83` — `filters.withRegionsRevealed`

**受入条件**: 非表示のセル・結合両端・親region・activeOnly対象の診断jumpで対象が見えることを確認する。／無関係なfilter保持、位置fallback、ソースjump非干渉、doc/dirty/history不変を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 08B 診断位置へのソースジャンプ]]、[[TECSCDE-DT-EL内部仕様 - 06B 表示フィルタUI設計]]、[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]。

## 監査52

**診断一覧が要求された4列表になっていない**

[[TECSCDE-DT外部仕様 - 監査対応 49-58 出力と検索#監査52]]に対応する。

DiagnosticsPanelViewは現在のレポートから4列のtableまたは同等のアクセシブルな表構造を作り、severityの日本語文字、対象、本文、操作ボタンを分離する。行全体の色とclickだけで移動を表現しない。操作は#50/#51のナビゲータへ診断IDと世代を渡し、一覧更新で古い行番号が別診断を指さないようにする。原位置と本文はDiagnosticの値を維持し、formatDiagnosticはコピー/ログ用の共通整形として残せる。ゼロ件の集計非表示、既存のパネル開閉とGenerate後の表示は保持し、描画だけで診断や履歴を新規生成しない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/diagnostics-panel.ts:57` — `document.createElement("div")`
- `src/renderer/app/diagnostics-panel.ts:63` — `item.textContent = formatDiagnostic(d);`

**受入条件**: error/warning/図位置/ソース位置/両方/移動先なしの4列とボタン可否を確認する。／件数0、一覧差替え、キーボード操作、表示とログ本文の一致を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 08B 診断位置へのソースジャンプ]]、[[TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計]]。

## 監査53

**シグニチャ名検索で結合をヒットさせず、ポートを持つセルだけが一致する**

[[TECSCDE-DT外部仕様 - 監査対応 49-58 出力と検索#監査53]]に対応する。

searchDocumentはJoinごとに実際の描画と同じ呼び口のシグニチャを解決し、結合ラベル検索の文字列へ含める。ポート名と端点名だけのlabelをシグニチャの代用にしない。セル一致と結合一致はkindを分け、AppShellが1回の検索スナップショットから一覧とSearchHighlightsのID集合を導出する。大文字小文字・空語の既存正規化は保持し、型未解決やポート不在でも例外にせず得られる情報だけを検索する。シグニチャ一致を理由にSelectionStateへセルを追加せず、結合の可視線/スタブを描画側へ渡す。検索関数自体はフィルタやdocを更新しない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/view-state/search.ts:51` — `...cell.cports.flatMap`
- `src/renderer/view-state/search.ts:68` — `` if (matches(`${join.cportName} ${join.eportName} ${label}` ``
- `src/renderer/render/join-renderer.ts:70` — `label.textContent = cport.signature;`

**受入条件**: セル/型/シグニチャが異なる名前の図で、signature語が期待するJoinIdを返すことを確認する。／一覧件数・巡回・背面線、未解決型、スタブ、非表示jumpとsnapshot一致を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 06 表示制御設計]]、[[TECSCDE-DT-EL内部仕様 - 06B 表示フィルタUI設計]]。

## 監査54

**ジャンプでフィルタを緩和した事実のrevealed印が再描画直後に失われる**

[[TECSCDE-DT外部仕様 - 監査対応 49-58 出力と検索#監査54]]に対応する。

SearchHit.revealedの現在非表示という性質だけに依存せず、実際のジャンプ前後で表示条件が変わった対象の安定したcell/join IDを表示用集合として記録する。SearchBoxView等の検索UIの一時状態で管理し、検索結果の再計算や同期renderを挟んでも当該印を再適用する。結合は両端のいずれかが必要な緩和対象なら記録し、bothHiddenだけで判定しない。印の寿命は検索セッション単位の内部案とし、検索解除/新しい検索/文書切替で不要IDを除去するが、既に緩和したフィルタは戻さない。結果一覧と描画の共通snapshotは維持し、履歴や保存CDLに印の状態を追加しない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/view-state/search.ts:59` — `revealed: hiddenRegionIds.has(cell.regionId)`
- `src/renderer/view-state/search.ts:69` — `const bothHidden =`
- `src/renderer/app/search-box.ts:83` — `filters.withRegionsRevealed`

**受入条件**: hiddenセル、片端hidden結合、両端hidden結合へjumpし、同期再描画後も印が残ることを確認する。／query変更/解除/doc切替で古い印だけを除去し、緩和済みfilterは戻らないことを確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 06B 表示フィルタUI設計]]、[[TECSCDE-DT-EL内部仕様 - 06 表示制御設計]]。

## 監査55

**フィルタで非表示にした選択セルの枠だけが残る**

[[TECSCDE-DT外部仕様 - 監査対応 49-58 出力と検索#監査55]]に対応する。

SvgRendererのselectionLayerも通常セルと同じ可視セルID集合を受け、selection.cellIdsを列挙した後、存在と可視性を検査してから枠を描く。セルgroupのdisplay:noneだけで別レイヤの枠まで隠れるとは仮定しない。結合枠は共通のjoin可視部分計算を使い、スタブの点列だけを描く。リージョン非表示とactiveOnlyを別実装にせず、ヒットテスト・通常図形・検索強調へ同じ導出結果を射影する。不可視化ではSelectionState自体を変更せず、削除されたIDの整合処理と混同しない。再表示時は現在のモデル位置で枠を再生成し、古い座標の枠を残さない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/render/svg-renderer.ts:197` — `for (const id of selection.cellIds)`
- `src/renderer/render/svg-renderer.ts:209` — `this.selectionLayer.appendChild(rect);`

**受入条件**: 選択→region非表示/activeOnly→再表示で、本体と枠の可視性と選択ID保持を確認する。／結合片端/両端非表示、削除済みID、検索併存、doc/dirty/history不変を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 06 表示制御設計]]、[[TECSCDE-DT-EL内部仕様 - 06B 表示フィルタUI設計]]、[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]。

## 監査56

**ナビゲータの縮小図・ドラッグ・手動表示による自動判定の上書きが未対応**

[[TECSCDE-DT外部仕様 - 監査対応 49-58 出力と検索#監査56]]に対応する。

computeNavigatorの派生結果へ縮小用のセル・結合シーンを接続し、現在viewport矩形と重ねる。NavigatorViewはpointerdown/move/upとcaptureでクリック/ドラッグを共通の座標変換へ渡し、縮小表示の内容領域を逆変換してViewState.panToへ反映する。アスペクト比と余白を考慮し、表示外クリックやゼロ寸法を安全に扱う。可視性は初期autoと手動on/offを分ける内部案とし、autoHiddenとの単純ORで手動onを潰さない。状態は表示専用で起動時既定へ戻し、CDLへ保存しない。doc・用紙・viewport・pan/zoomの変化で縮小シーンと枠を同期し、位置変更から編集コマンドを発行しない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/navigator-panel.ts:32` — `this.svg.append(this.paperRect, this.viewportRect);`
- `src/renderer/app/navigator-panel.ts:34` — `this.svg.addEventListener("click"`
- `src/renderer/app/navigator-panel.ts:60` — `const hidden = !this.visible || model.autoHidden;`

**受入条件**: 既知のセル・結合位置と縮小図の一致、クリック/連続dragのパン、capture外への移動を確認する。／autoHidden状態で手動onが有効となり、pan/zoom/resize更新と非保存を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 06 表示制御設計]]、[[TECSCDE-TS内部仕様 - 06 表示制御設計]]。

## 監査57

**ポート記号の向き・3mm寸法・ズーム追従が仕様と異なる**

[[TECSCDE-DT外部仕様 - 監査対応 49-58 出力と検索#監査57]]に対応する。

portSymbolPointsはedgeだけでなく呼び口/受け口の種別を入力にし、辺法線と種別の組に対応する反転した頂点列を定義する。三角形の基本形はmm単位で一か所へ置き、描画時にMM_TO_PX×zoomを掛ける。現在の固定PORT_SYMBOL_PXによる寸法と、kindをCSSの塗りにだけ使う分岐を置き換える。辺ごとの向き表を明示し、4辺のいずれでも両種が同じ方向にならないことを確認する。ヒットテスト位置・結合の端点は既存のportPositionと共用し、記号の向き変更からMovePortやChangePortEdgeを発行しない。exportも同じ頂点生成を使い、画面と物理寸法を一致させる。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/render/cell-renderer.ts:22` — `const PORT_SYMBOL_PX = 4;`
- `src/renderer/render/cell-renderer.ts:25` — `function portSymbolPoints(edge: EdgeSide, size: number)`
- `src/renderer/render/cell-renderer.ts:124` — `portSymbolPoints(port.edgeSide, PORT_SYMBOL_PX)`

**受入条件**: 両種×4辺を白黒で比較し、同辺で向きが異なることを確認する。／5/100/200%の寸法比、3mm基本形、ヒット/結合端点とexportの一致を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 05 描画・インタラクション設計]]、[[TECSCDE-TS内部仕様 - 05 描画・インタラクション設計]]、[[TECSCDE-DT-EL内部仕様 - 07F エクスポート設計（たたき台）]]。

## 監査58

**activeセルを最上段へ移動する操作・計画・コマンド・通知が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 49-58 出力と検索#監査58]]に対応する。

canMoveActiveToTopはisActiveCellとeditableだけでボタン可否を導出する。prepareMoveActiveToTopはdoc.cellValuesの安定順で対象を確定し、対象外の全セルを固定障害物として、4Gと共通の格子をallowOverlap:falseで有限走査する。8/6mmのずらしや重なり許容のfallbackは用いない。全位置確定後に関係結合を再計算し、値による前提・配置・経路・spill集合を固定した1コマンドへ渡す。applyは同期・純粋で、前提不一致は全体no-opとする。警告と成功ステータスは呼出側で一度だけ登録し、Undo/Redo・文書切替に同期する。対象選択にSelectionStateやフィルタを使わず、保存は各定義元の既存規則に従う。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/shell.ts:257` — `runAction(action: string)`
- `src/renderer/app/shell.ts:379` — `private refreshToolbarState(): void`
- `src/renderer/index.html:525` — `data-action="alignLeft"`

**受入条件**: activeなし/readonlyのみ/非表示active/選択の違いで対象と有効条件を確認する。／最上段成功/次行spill/全拒否、非対象固定、経路・通知・1Undoと状態非干渉を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]、[[TECSCDE-DT-EL内部仕様 - 04G 再配置コマンド設計]]、[[TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計]]、[[TECSCDE-DT-EL内部仕様 - 05 描画・インタラクション設計]]。

## Related

- [[TECSCDE-DT-EL内部仕様]]
- [[TECSCDE-DT外部仕様 - 監査対応 49-58 出力と検索]]

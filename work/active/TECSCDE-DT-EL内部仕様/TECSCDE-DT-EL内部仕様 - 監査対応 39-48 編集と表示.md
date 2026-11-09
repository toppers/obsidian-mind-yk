---
date: 2026-11-09
description: "三者監査39〜48の内部仕様契約補足。既決要件と現行コードの差を区別する。"
project: TECS
quarter: Q4-2026
status: active
tags: [work-note, tecs, tecscde, spec]
---

# TECSCDE-DT-EL内部仕様 - 監査対応 39-48 編集と表示

[[TECSCDE-DT-EL内部仕様]]の補足。[[TECSCDE-DT外部仕様 - 監査対応 39-48 編集と表示]]と対になる。

2026-11-09の確定契約・実装境界を記す。関連する旧時点の実装記録を、今回のコードの適合確認として扱わない。既存の決定と未決事項（TBC）を維持し、未決を完成済みにしない。仕様を修正してもソース修正が必要な項目は未実装のままである。

## 監査39

**複数セル選択時に共通編集項目を表示しない**

[[TECSCDE-DT外部仕様 - 監査対応 39-48 編集と表示#監査39]]に対応する。

PropertyPanelViewは現在の選択セルIDから、項目の有無・型・候補・編集可否の共通部分を純粋に導出する。型やリージョン候補は各セルの制約の積集合とし、全対象に共通かつ編集可能な項目だけを共通編集欄へ出し、権限を満たさない項目を編集可能と見せない。値の比較で一致値と混在表示を分離し、混在表示を実値としてdispatchしない。確定入力から対象IDと更新値を固定した一括計画を作り、全対象を検証してから1コマンドで適用し、1Undoで戻す。実装案として一部だけの無通知成功は避け、条件不一致は通知して計画を適用しない。定義元の単一表示契約は維持し、表示署名に選択ID・共通項目と各値を含めて無関係な再描画による入力消失を防ぐ。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/property-panel.ts:62` — `if (selection.cellIds.size > 1`
- `src/renderer/app/property-panel.ts:63` — `(複数選択 — 個別編集はセルを1つだけ選択してください)`

**受入条件**: 共通属性/候補不一致/値混在/readonly混在/同数の別選択で表示を確認する。／入力確定の一括変更とUndo/Redo、無入力の混在表示で変更が起きないことを確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、[[TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計]]。

## 監査40

**選択肢付き属性もコンボにせず、自由入力にする**

[[TECSCDE-DT外部仕様 - 監査対応 39-48 編集と表示#監査40]]に対応する。

属性名だけの一覧に加えて候補を表す読み取り専用メタデータを型参照からビューへ渡す契約を追加し、エディタ選択を一か所に集約する。候補ありはselect等、候補なしは既存inputを用いる。候補一覧はパーサが認識した定義から取得し、名称や現在値から勝手に合成しない。既存値が候補外の場合も元値を識別して保持し、利用者の確定操作でのみ新値を検証する。EditAttrCommandへ対象IDと確定値を渡し、ビュー構築や候補同期を履歴へ入れない。複数選択では#39の共通候補集合と編集可否を使い、非同期型更新で入力中の値を古い候補へ巻き戻さない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/property-panel.ts:19` — `document.createElement("input")`
- `src/renderer/app/property-panel.ts:172` — `for (const attrName of attrNames)`

**受入条件**: 候補あり/なし/候補外の読込値/readonlyで適切なエディタが表示されることを確認する。／確定1回につき1履歴、取消・表示更新ではdoc不変となることを確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、[[TECSCDE-DT-EL内部仕様 - 03 モデル設計]]、[[TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計]]。

## 監査41

**用紙変更・Undo/Redo・アプリケーション既定の設定と新規適用が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 39-48 編集と表示#監査41]]に対応する。

用紙変更UIは有効なPaperSpecを作り、ChangePaperCommand相当へ固定値として渡す。applyは現在docの用紙だけを不変更新し、セル・ポート・結合を再配置しない。1回の変更を1Undoとし、同値はno-opとする。現在用紙を既定として保存する操作は編集コマンドとは分離し、SettingsGatewayからアプリ設定の一項目だけを部分更新する。設定キー名は内部契約案として既存設定方式へ統合し、未知項目やセッションを上書きしない。新規文書生成は検証済み既定を参照する一方、ローダーの指定/未指定・最小用紙選択は独立させる。Undoで図の用紙を戻してもアプリ既定を副作用で書き戻さない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/shell.ts:257` — `runAction(action: string)`
- `src/renderer/index.html:516` — `<div id="toolbar">`

**受入条件**: A4/A3/A2と縦横の変更・同値・Undo/Redoでセル位置が変わらないことを確認する。／現在用紙の変更と既定保存、新規/消去/ファイル読込の適用範囲が分離されることを確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 04D 読み込み時の最小用紙選択]]、[[TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計]]、[[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]。

## 監査42

**現在の入力モードをステータスへ文字表示しない**

[[TECSCDE-DT外部仕様 - 監査対応 39-48 編集と表示#監査42]]に対応する。

AppShellのステータス更新はstore.getModeから日本語のモード名を導出する。専用のstatus-mode要素等へ書き、ボタンから独立した第二のモード状態をビューに持たない。setModeに伴う既存notifyでモード名とPaletteViewの排他ボタンを同じスナップショットに同期し、開始時も必ず反映する。未知の入力値を正常な選択モードと偽装せず、InputModeの型で表示可能な値を限定する。非同期の診断やファイル表示の更新がモード名を上書きしないよう、固定情報と一過性の操作結果欄を分離する。ステータス書込みからdispatchやsetSelectionを呼ばない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/shell.ts:404` — `private refreshStatus(): void`
- `src/renderer/index.html:572` — `<div id="statusbar">`

**受入条件**: 初期状態・両モードへの切替・他のストア通知で文字とボタンが一致することを確認する。／モード表示更新でdoc/dirty/history/selectionが変わらないことを確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、[[TECSCDE-DT-EL内部仕様 - 05 描画・インタラクション設計]]。

## 監査43

**未保存状態をウィンドウタイトルへ反映しない**

[[TECSCDE-DT外部仕様 - 監査対応 39-48 編集と表示#監査43]]に対応する。

タイトルとステータスは、同じstore.isDirtyの結果と現在ファイル表示名から導出する。document.title等へファイル名とdirty接頭辞を反映し、新規文書は未確定名を用いつつdirtyを独立に付与する。path !== nullでdirty判定を打ち消さない。購読のたびに現在値へ同期し、保存結果の照合・checkpoint更新後、Undo/Redo、文書差替えでも更新する。表示用の別dirtyフラグを持たず、タイトル反映から履歴・保存・CloseGuardの判断を変更しない。ファイル名に由来する文字列はテキスト値として扱いHTML解釈せず、非同期保存が取消/失敗した場合は保存済み表示へ進めない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/index.html:15` — `<title>TECSCDE</title>`
- `src/renderer/app/shell.ts:409` — `const dirty = path !== null && this.store.isDirty();`

**受入条件**: 既存ファイルと新規文書の編集/保存/Undo/Redo/読込でタイトルとstatusが一致することを確認する。／保存取消/失敗で接頭辞を消さず、表示更新だけではdoc/history不変となることを確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、[[TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計]]。

## 監査44

**activeセルの青背景・状態色の優先順位が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 39-48 編集と表示#監査44]]に対応する。

isActiveCellはdocの型参照のactive指定から純粋に判定し、CellVisualStateの編集可否・不完全・未結合とは別の入力として渡す。CellRendererは排他的な単一状態へ潰さず、塗りと枠の解決結果を別々に生成する。複合セレクタまたは解決済みスタイルを用い、CSS宣言順の偶然でreadonlyが青を覆わない構成にする。不完全枠への対応は5Bの一般状態と既存のtype未解決クラスを混同しないよう明示する。状態変化を差分描画条件へ含め、通常表示とexportで同じ色トークンと解決結果を共用する。表示判定でdoc・dirty・履歴を書き換えず、activeの非色覚的補助記号の将来検討TBCは今回確定しない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/render/cell-renderer.ts:65` — `const classes = ["cell-rect"]`
- `src/renderer/index.html:448` — `.cell-rect.readonly`

**受入条件**: active×readonly×不完全の全組合せ、U併存、検索/選択/regionを重ねても優先順位が崩れないことを確認する。／実際の文字色/背景トークンのコントラストと単独SVG出力の一致を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 05B 色に依存しない状態表示]]、[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]、[[TECSCDE-DT-EL内部仕様 - 05 描画・インタラクション設計]]、[[TECSCDE-DT-EL内部仕様 - 07F エクスポート設計（たたき台）]]。

## 監査45

**activeOnlyフィルタと操作UIが未実装**

[[TECSCDE-DT外部仕様 - 監査対応 39-48 編集と表示#監査45]]に対応する。

DisplayFiltersへactiveOnlyの真偽値を追加し、with系更新・equals・初期値・射影で値を落とさない。可視集合はリージョン条件とisActiveCell条件の積集合として共通関数で導出し、SvgRenderer、HitTester、選択オーバーレイ、スタブ、exportへ同じ結果を渡す。検索の対象集合は狭めず、ジャンプ対象が隠れる場合だけactiveOnlyを解除する設計案を6Cに統合し、リージョン緩和の事実も保持する。UIは状態だけを更新し、docや選択を勝手に消さない。現在の可視セルIDを別ストアで重複管理せず、docとフィルタから再導出する。未決の移設レイアウトや保存対象外の規則を実装都合で変更しない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/view-state/display-filters.ts:19` — `private constructor(`
- `src/renderer/render/svg-renderer.ts:118` — `const hidden = view.hiddenRegionIds.has(cell.regionId);`

**受入条件**: active/非active/readonly/親region非表示の積集合と両端/片端スタブを確認する。／非activeヒットへのジャンプ、履歴・dirty・保存内容不変、初期オフとexport一致を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 06B 表示フィルタUI設計]]、[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]、[[TECSCDE-DT-EL内部仕様 - 06 表示制御設計]]、[[TECSCDE-DT-EL内部仕様 - 07F エクスポート設計（たたき台）]]。

## 監査46

**ポート選択に追従する赤い太線の結合強調が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 39-48 編集と表示#監査46]]に対応する。

AppStoreはconnectionFocusEnabledだけを持ち、選択ポートのコピーを別状態に保持しない。resolveHighlightedJoinIdsは現在docとSelectionStateの安定ポートID・種別・配列添字から直接のJoinId集合を純粋に返す。CanvasViewとJoinRendererへ集合を射影し、可視線・スタブの色と太さを通常線から切り替える。集合変更とトグル変更を差分更新へ含め、消えたIDを残さない。検索背面線・選択枠とは異なる層として同時表示し、既存クリック/ドラッグ/Escapeの入力を変更しない。exportは選択を空にする前に確定した強調IDを共通スナップショットへ取り込み、選択由来だからと除外しない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/render/view.ts:20` — `export interface CanvasView`
- `src/renderer/render/join-renderer.ts:59` — `line.setAttribute("class", "join-line");`

**受入条件**: 両ポート種・複数選択・配列・readonly・スタブ・未結合とトグル解除を確認する。／検索/選択との併存、削除/文書切替での古いID除去、export・履歴不変を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]、[[TECSCDE-DT-EL内部仕様 - 06B 表示フィルタUI設計]]、[[TECSCDE-DT-EL内部仕様 - 05 描画・インタラクション設計]]、[[TECSCDE-DT-EL内部仕様 - 07F エクスポート設計（たたき台）]]。

## 監査47

**リージョン矩形モード・親子外周・名前表示が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 39-48 編集と表示#監査47]]に対応する。

computeRegionOutlinesは可視セルIDとRegionTreeから、根以外の各部分木のセル本体矩形を同じmm座標で集める。6Cの階層余白を使って拡張し、元の矩形は保持したまま座標圧縮による和集合と外周線分を導出する。余白値は既存の暫定値として調整可能なまま扱い、未確認の数値を外部の確定値に昇格しない。region-outlines層を背景へ置き、pointer-events:noneでヒットを遮らない。移動、所属、可視性、モード変更で再計算し、色Mapと線分をexportでも共用する。ViewState.regionOutlineModeは表示専用で、セッション・CDL・履歴へ入れず、子孫を含む親の線や名前を決定的に描く。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/render/svg-renderer.ts:62` — `this.svg.append(this.joinLayer`
- `src/renderer/render/view.ts:20` — `export interface CanvasView`

**受入条件**: 矩形の分離/包含/共有辺/角接触、親子同色、兄弟の重なり、名前と外周を確認する。／非表示セル除外、モード初期化/非保存、入力非干渉、export一致を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]、[[TECSCDE-DT-EL内部仕様 - 06B 表示フィルタUI設計]]、[[TECSCDE-DT-EL内部仕様 - 05 描画・インタラクション設計]]、[[TECSCDE-DT-EL内部仕様 - 07F エクスポート設計（たたき台）]]。

## 監査48

**RO・!・Uの独立記号、状態凡例、理由表示が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 39-48 編集と表示#監査48]]に対応する。

deriveCellVisualStateは!editable、celltypeUnresolvedと現在docへ関連付いた既存の構造未解決理由、実在する呼び口要素のjoinId欠落を別々に返す。任意の環境警告・操作拒否を不完全へ混入させず、型未解決時の未結合判定不能はnull等で空集合と区別する。CellRendererは内側の状態行へSVG図形と文字を置き、ラベル・ポート・region帯・選択/検索枠と重ねず、pointer-events:noneと説明用ariaを付ける。AppShellとプロパティは同じスナップショットで凡例と理由を表示する。doc外の判定は現doc世代へ同期してから渡し、古い理由を同名セルへ継承しない。モデル寸法や履歴を表示目的で変えず、画像出力にも通常図形として残す。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/render/cell-renderer.ts:66` — `if (!cell.editable) classes.push("readonly");`
- `src/renderer/render/cell-renderer.ts:68` — `if (cell.celltypeUnresolved) classes.push("unresolved");`

**受入条件**: 各状態と全組合せを白黒でも識別でき、optional/require/判定不能が区別されることを確認する。／状態解消・Undo/Redo・文書差替え、低倍率・最小セル・長い名前・exportの一致を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 05B 色に依存しない状態表示]]、[[TECSCDE-DT-EL内部仕様 - 05 描画・インタラクション設計]]、[[TECSCDE-DT-EL内部仕様 - 06B 表示フィルタUI設計]]、[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]、[[TECSCDE-DT-EL内部仕様 - 07F エクスポート設計（たたき台）]]。

## Related

- [[TECSCDE-DT-EL内部仕様]]
- [[TECSCDE-DT外部仕様 - 監査対応 39-48 編集と表示]]

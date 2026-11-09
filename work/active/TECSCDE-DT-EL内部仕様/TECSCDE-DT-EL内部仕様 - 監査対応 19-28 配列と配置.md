---
date: 2026-11-09
description: "三者監査19〜28の内部仕様契約補足。既決要件と現行コードの差を区別する。"
project: TECS
quarter: Q4-2026
status: active
tags: [work-note, tecs, tecscde, spec]
---

# TECSCDE-DT-EL内部仕様 - 監査対応 19-28 配列と配置

[[TECSCDE-DT-EL内部仕様]]の補足。[[TECSCDE-DT外部仕様 - 監査対応 19-28 配列と配置]]と対になる。

2026-11-09の確定契約・実装境界を記す。関連する旧時点の実装記録を、今回のコードの適合確認として扱わない。既存の決定と未決事項（TBC）を維持し、未決を完成済みにしない。仕様を修正してもソース修正が必要な項目は未実装のままである。

## 監査19

**配列結合の添字省略の採番と、明示・省略混在の警告が未反映**

[[TECSCDE-DT外部仕様 - 監査対応 19-28 配列と配置#監査19]]に対応する。

CSTの結合宣言に非配列・明示添字・空角括弧を識別する情報を残し、collectCell後の同一セル/呼び口グループでassignOmittedSubscripts相当の採番を行います。生成した添字を要素生成と結合ID・端点解決へ共通で渡し、省略形が同じ未添字ポートへ集約されないようにします。serializerは元宣言と変更対象の識別を保持し、変更していない省略形式の原文を維持します。PR23の履歴記録と異なり、今回HEADのcst/document-builderには未反映です。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/cdl/cst.ts:460` — `const cportIndex = Number.isFinite(parsedIndex) ? parsedIndex : undefined;`
- `src/renderer/cdl/document-builder.ts:574` — `` const jid = asJoinId(`${decl.cellName}.${j.cport}${j.cportIndex !== undefined ? `[${j.cportIndex}]` … ``

**受入条件**: c[]複数行の0,1採番、セル/呼び口ごとのリセット／混在警告と読込継続、明示c[2]／無変更原文往復と変更配列の明示添字保存

参照: [[TECSCDE-DT-EL内部仕様 - 04B CDLパーサ設計]]、[[TECSCDE-DT-EL内部仕様 - 04C ファイル別保存契約]]、[[TECSCDE-DT-EL内部仕様 - 04E 可変長配列ポートの要素挿入]]。

## 監査20

**固定長・可変長配列を、要素ごとのポートへ展開しない**

[[TECSCDE-DT外部仕様 - 監査対応 19-28 配列と配置#監査20]]に対応する。

CdlDocumentLoaderは宣言解析後、全ソースの結合とarray_elementsを集約してからCPort/EPort要素を生成し、最後に結合と保存位置を適用します。arrayKind・宣言グループ識別・安定PortIdとsubscriptを別々に持たせ、CPortの最大一本/EPortの複数入結合を要素単位で管理します。可変長EPortは全参照添字を必要数へ含めます。現行assignDefaultPortLayoutは全宣言をsubscript:null一個へ写すため、この段階と型索引/描画/保存の要素識別を接続する必要があります。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/cdl/document-builder.ts:93` — `subscript: null,`
- `src/renderer/model/port.ts:31` — `readonly arraySize: number | null,`

**受入条件**: 固定N/可変/未解決/非配列を区別しc[2]解決／複数ソースからの受け口要素参照／要素別位置・PortTypeIndex・再添字後の安定ID

参照: [[TECSCDE-DT-EL内部仕様 - 03 モデル設計]]、[[TECSCDE-DT-EL内部仕様 - 04B CDLパーサ設計]]、[[TECSCDE-DT-EL内部仕様 - 04E 可変長配列ポートの要素挿入]]。

## 監査21

**ポート選択・移動・辺変更・ポート起点の結合削除へUIから到達できない**

[[TECSCDE-DT外部仕様 - 監査対応 19-28 配列と配置#監査21]]に対応する。

SelectionStateへ所有セル・方向・安定PortIdのポート選択集合を加え、HitTesterの結果から要素を一意解決します。GestureControllerは修飾キー/モードに応じた選択と結合作成を分岐し、ポートドラッグをMovePortCommand、辺変更の明示操作をChangePortEdgeCommandへ接続します。辺上の制限・丸めと接続経路再計算は既存コマンドを共用します。Deleteは選択ポートの結合IDを重複除去して既存削除へ渡し、読み取り専用呼び口の制約をapplyでも検査します。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/render/gesture-controller.ts:153` — `if (hit.kind === "cport") {`
- `src/renderer/render/gesture-controller.ts:198` — `// hit.kind === "eport" | "none": 空白クリック → 矩形選択の開始。`
- `src/renderer/render/view.ts:62` — `export class SelectionState {`

**受入条件**: call/entry/配列要素選択、Shift/Ctrl/排他／辺上移動と明示辺変更、接続経路/UndoRedo／entry全入結合削除、readonly source拒否

参照: [[TECSCDE-DT-EL内部仕様 - 05 描画・インタラクション設計]]、[[TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計]]、[[TECSCDE-DT-EL内部仕様 - 04F 配列ポートの要素削除]]。

## 監査22

**Insertによる可変長配列要素挿入と拒否通知が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 19-28 配列と配置#監査22]]に対応する。

4Eの単一対象直後挿入をprepareArrayPortInsertionで計画し、新PortId・expectedElementIds・挿入位置・配置結果をdispatch前に固定します。InsertArrayPortElementCommandは前提を再検査して未結合要素を一個加え、既存IDを保って後続添字と関連する全結合の参照を更新します。必要な経路再計算も同時に適用し、readonly参照元の書換が必要なら計画全体を拒否します。配置間隔等の未確定詳細を勝手に固定せず、通知はapply外、二重適用はno-opとします。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/commands/port-commands.ts:41` — `export class MovePortCommand extends Command {`
- `src/renderer/render/gesture-controller.ts:299` — `keyDown(key: string, mods: Mods = NO_MODS): boolean {`

**受入条件**: 中間/末尾callとentry、複数入結合保持／固定長/先頭以外の拒否理由/IME等入力ガード／ID安定と1Undo、配置不能/readonly参照元の原子拒否

参照: [[TECSCDE-DT-EL内部仕様 - 04E 可変長配列ポートの要素挿入]]、[[TECSCDE-DT-EL内部仕様 - 05 描画・インタラクション設計]]、[[TECSCDE-DT-EL内部仕様 - 07J 保存チェックポイントと未保存判定]]。

## 監査23

**Deleteによる配列要素削除・再添字・先頭／固定長拒否が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 19-28 配列と配置#監査23]]に対応する。

4FのprepareArrayPortElementDeletionは削除時点のPortId集合と要素列を固定し、削除可能性と再添字に必要な全参照元の編集可否を検査します。DeleteArrayPortElementsCommandは全前提一致時だけ元IDを一括除去し、残存ID/位置/結合を保って最後に添字を詰めます。PortTypeIndexはcommit/UndoRedo後にストアが再導出し、削除済み選択と強調を整合させます。個数情報と変更した結合代入を定義元別に保存し、旧templateから削除情報を復活させません。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/render/gesture-controller.ts:303` — `this.host.dispatch(new DeleteCommand([...sel.cellIds], [...sel.joinIds]));`

**受入条件**: 接続ありfixed/index0も先に解除、entry全件／未結合中間/末尾/複数削除と混在全拒否／同一ID/位置維持、再添字/UndoRedo/array_elements往復

参照: [[TECSCDE-DT-EL内部仕様 - 04F 配列ポートの要素削除]]、[[TECSCDE-DT-EL内部仕様 - 04E 可変長配列ポートの要素挿入]]、[[TECSCDE-DT-EL内部仕様 - 03 モデル設計]]。

## 監査24

**採用済みのarray_elementsによる未結合末尾要素の保存・復元が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 19-28 配列と配置#監査24]]に対応する。

ToolInfoValidatorはarray_elementsを既知キーとして型/範囲/同一キー重複を検証し、ソース別の個数索引を返します。loaderは宣言と結合の必要数へ索引を照合して要素生成後に位置を適用します。serializerは現在モデルから個数を再構成し、削除済みの既知データを復活させず未解決原情報を保持します。DirtyTracker/SaveTicketのSourceSaveStateにも個数を含め、結合が変わらない挿入削除を未保存として検出します。上限数値は既存モデル制約との整合を実装時に定めます。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/cdl/serializer.ts:189` — `ports[p.name] = { edge: p.edgeSide, offset: p.offset };`
- `src/renderer/cdl/tool-info.ts:317` — `const { paper, cell_list, join_list, ...unknownFields } = obj as {`

**受入条件**: 未結合末尾/結合なし/entry/同名別scope/複数source往復／不正0/負/小数/巨大/重複/未解決/旧file／保存中の個数変更をcleanにしない、SaveAs/UndoRedo

参照: [[TECSCDE-DT-EL内部仕様 - 04E 可変長配列ポートの要素挿入]]、[[TECSCDE-DT-EL内部仕様 - 04F 配列ポートの要素削除]]、[[TECSCDE-DT-EL内部仕様 - 07J 保存チェックポイントと未保存判定]]。

## 監査25

**複数セルのコピー・貼り付けで、選択セル間の結合を保持しない**

[[TECSCDE-DT外部仕様 - 監査対応 19-28 配列と配置#監査25]]に対応する。

ClipboardSnapshotをcells/joinsの不変値へ拡張し、appClipboardとCDL断片の両経路へ同じ抽出条件を適用します。pasteFromAppClipboard/tryParseCdlFragmentは断片内で閉じた端点だけを保持し、旧セル/PortIdから新IDへの写像を確定して複製セル間へ再接続します。名前重複回避、定義元、配列添字と幾何offsetを揃え、既存貼付け先セルを断片端点の代用にしません。PasteCommandは解決済み値を同期適用し、CutのOS書込はdispatch外で一回だけ行います。結合経路は新セル配置とポート位置から再計算し、元の経路をそのまま流用しません。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/cdl/fragment.ts:18` — `` const body = Object.entries(attrs).map(([name, expr]) => `  ${name} = ${expr};`); ``
- `src/renderer/commands/clipboard-commands.ts:36` — `` * 元の位置から`PASTE_OFFSET_MM`だけずらし、名前・結合は新規に割り当てる（結合は引き継がない）。 ``

**受入条件**: 一個/複数/片端外/線未選択、call配列とentry複数結合／appClipboardとOS断片で同じ内部結合再現／名前重複/定義元/1UndoRedo/履歴再生時OS副作用なし

参照: [[TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計]]、[[TECSCDE-DT-EL内部仕様 - 04H CDLパーサの診断・断片・拡張点]]、[[TECSCDE-DT-EL内部仕様 - 04C ファイル別保存契約]]。

## 監査26

**読み込み時の衝突回避・最小用紙選択・overflow通知が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 19-28 配列と配置#監査26]]に対応する。

4Dに従い全ソースの採否と保存レイアウト検証後に固定障害物を確定し、候補用紙ごとに同じ初期状態から独立して配置計算します。候補格子(10,10)/横55/縦30と、重ならない最初の位置を共用し、不採用試行の位置や警告を次候補へ持ち越しません。最終候補で横8/縦6のずらしと件数を確定します。固定矩形の範囲外/重複と自動配置overflowを分け、W-AUTO-LAYOUT-OVERFLOWは最終結果だけへ登録します。現行即A4/autoPlacementPositionは未対応です。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/cdl/document-builder.ts:269` — `let paper: PaperSpec = PaperSpec.default();`
- `src/renderer/cdl/document-builder.ts:476` — `const pos = autoPlacementPosition(autoIndex, paperW, paperH);`

**受入条件**: 後読込source固定セル、保存位置/寸法不変／A4失敗A3成功、明示A4、A2overflow最終件数／候補独立性と有限終端、再読込保存位置保持

参照: [[TECSCDE-DT-EL内部仕様 - 04D 読み込み時の最小用紙選択]]、[[TECSCDE-DT-EL内部仕様 - 04B CDLパーサ設計]]、[[TECSCDE-DT-EL内部仕様 - 04G 再配置コマンド設計]]。

## 監査27

**複数ファイルの用紙採用元・競合警告・用紙の保存先が契約と異なる**

[[TECSCDE-DT外部仕様 - 監査対応 19-28 配列と配置#監査27]]に対応する。

4DのPaperResolutionへopen順と採用元SourceIdを保持し、各ソースのpaper検証結果と不正/競合診断を集約します。主のprimarySourceKeyとは独立させ、rendererのソース配列が変わっても保持したopen順で採用元を決定します。serializerは採用元だけ現在doc.paperを出力し、他ソースは原paperを往復保持します。DirtyTrackerの保存対象状態へ採用元のpaper変更を含めます。読取専用/生成ソースを書込対象へ自動昇格しない制約を維持し、保存不能条件を黙って別ソースへ付替えません。用紙採用の対象集合は外部05Bに従い-S/生成を除き、主役の集合と混同しません。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/cdl/document-builder.ts:327` — `paper = PaperSpec.create(p.paper.size, p.paper.orientation ?? "LANDSCAPE");`
- `src/renderer/cdl/serializer.ts:154` — `{ size: prior?.paper?.size ?? doc.paper.size, orientation: prior?.paper?.orientation ?? doc.paper.or…`
- `src/renderer/cdl/tool-info.ts:326` — `const size = VALID_PAPER_SIZES.includes(p.size as PaperSize) ? (p.size as PaperSize) : undefined;`

**受入条件**: 先A3/後A4の採用と競合、内部配列変更でもopen順維持／invalid size/orientation、宣言なし／paperのみ変更のdirty/保存先/他file保持/再読込

参照: [[TECSCDE-DT-EL内部仕様 - 04D 読み込み時の最小用紙選択]]、[[TECSCDE-DT-EL内部仕様 - 04C ファイル別保存契約]]、[[TECSCDE-DT-EL内部仕様 - 07J 保存チェックポイントと未保存判定]]。

## 監査28

**通常の「再配置」「全体再配置」が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 19-28 配列と配置#監査28]]に対応する。

4GのprepareRelayoutは対象/固定セル/用紙/ポート/関係結合の前提を固定し、現在doc.cellValues順でmovesとjoinRoutesを一括計算します。通常格子と有限なずらし候補を共用し、物理的に配置不能なら計画全体を拒否します。RelayoutSelectedCellsCommand/Allは同期applyで全前提を検査して一括更新し、同計画二重適用・古い前提・変更なしはno-opにします。警告はapply外で計画へ関連付け、UndoRedo時も状態と対応させます。active最上段の非重複計画とは混同しません。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/align-actions.ts:10` — `export type AlignAxis = "top" | "left";`

**受入条件**: 混在選択/非表示含むall/対象外障害物/現在用紙／有限終端/配置不能全拒否/最終overflow／位置経路の1UndoRedo、定義元保存と無関係手動経路保持

参照: [[TECSCDE-DT-EL内部仕様 - 04G 再配置コマンド設計]]、[[TECSCDE-DT-EL内部仕様 - 04D 読み込み時の最小用紙選択]]、[[TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計]]。

## Related

- [[TECSCDE-DT-EL内部仕様]]
- [[TECSCDE-DT外部仕様 - 監査対応 19-28 配列と配置]]

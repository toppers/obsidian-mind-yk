---
date: 2026-09-05
description: "TECSCDE-TS内部仕様書 第5章（描画・インタラクション設計）— SvgRenderer/CellRenderer/JoinRenderer/HitTester/GestureControllerのクラス設計。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - architecture
---

Domain note split from [[TECSCDE-TS内部仕様]] (2026-09-05). Chapter 5 of 11（[[TECSCDE内部仕様]]の第6章に対応）。

## 5. 描画・インタラクション設計

SVGツリー構造・更新戦略・ヒットテストの優先順位（ポート＞セル＞結合バー）・ドラッグ状態機械の4状態・結合プレビュー線といった**挙動そのもの**は実装方式に依存しないため、[[TECSCDE内部仕様]]第6章と同一である。本章はこれをクラスとしてどう表現するかに絞る。

### 5.1 描画クラスの階層

現行実装（[[TECSCDE-JS-TS実装]]）の`SvgRenderer`は既にクラスとして存在するが、セル・結合の描画ロジックが1クラス内の条件分岐に混在している。本書はこれを要素種別ごとの下位クラスへ分離することを提案する。

```ts
abstract class ElementRenderer<TModel> {
  abstract createElement(model: TModel): SVGGElement;
  abstract updateElement(model: TModel, element: SVGGElement): void; // 属性のみ更新、再生成しない
}

class CellRenderer extends ElementRenderer<Cell> { /* 矩形・ラベル・ポート記号 */ }
class JoinRenderer extends ElementRenderer<Join> { /* 折れ線・シグニチャラベル */ }

class SvgRenderer {
  private readonly cellElements = new Map<CellId, SVGGElement>();
  private readonly joinElements = new Map<JoinId, SVGGElement>();
  private readonly cellRenderer = new CellRenderer();
  private readonly joinRenderer = new JoinRenderer();

  constructor(private readonly root: SVGSVGElement) { /* #cells, #joins, #join-preview, #selection-overlay, #grid の各<g>を生成 */ }

  onDocumentChanged(prev: TecscdeDocument | undefined, next: TecscdeDocument): void {
    // 差分のあるCell/Joinのみ cellElements/joinElements の対応要素を updateElement で更新する。
    // 3.2.2が禁じる「図全体の再描画」は、この対応表（Map）を持つことで構造的に発生しない。
  }
}
```

`ElementRenderer`のサブクラス分離により、セルの描画ロジックを変更してもJoinRendererに影響しないことが型レベルでも明確になる——既存の単一クラス実装ではこの独立性はレビュー任せだった。

### 5.2 `HitTester`クラス

外部仕様6.2.1の優先順位（ポート＞セル＞結合バー）と、6.2.2が要求する改善（結合バー探索を一定ピクセル半径内に限定）を、独立したクラスに閉じ込める。

```ts
class HitTester {
  constructor(
    private readonly doc: TecscdeDocument,
    private readonly renderer: SvgRenderer,
    private readonly barSearchRadiusPx: number = 8,
  ) {}

  hitTest(point: Point): HitResult {
    // 1. ポート（cportsの矩形+eportsの矩形）
    // 2. セル本体
    // 3. 結合バー（barSearchRadiusPx以内のみ、現行版の「モデル全体探索」を改める）
    // いずれもヒットしなければ HitResult.none
  }
}
```

`hit-test.ts`の関数群をクラスにまとめる理由は、`doc`（現在のドキュメント）と`renderer`（要素の位置情報）という2つの依存を毎回引数で渡す代わりに、コンストラクタで一度だけ受け取ることにある——`GestureController`は`HitTester`のインスタンスを1つ持ち、`doc`が変わるたびに新しい`HitTester`に差し替える（`TecscdeDocument`自体が不変なので、`HitTester`も実質的に不変な値として扱える）。

### 5.3 ドラッグ状態機械（`GestureController`）

現行実装（[[TECSCDE-JS-TS実装]]）の`GestureController`は既にクラスであり、本書もこれをそのまま採用する。外部ライブラリ（XState等）は使わず、外部仕様3.7の4状態（通常／呼び口の上／結合操作中／結合先として有効）を判別可能なUnion型で表現する。

```ts
type DragState =
  | { kind: 'idle' }
  | { kind: 'over-port'; port: PortId }
  | { kind: 'joining'; from: PortId }
  | { kind: 'valid-target'; from: PortId; to: PortId };

class GestureController {
  private state: DragState = { kind: 'idle' };

  constructor(
    private readonly svg: SVGSVGElement,
    private readonly renderer: SvgRenderer,
    private readonly host: GestureHost, // host.dispatch(command) でコマンドを発行する
  ) {}

  private transition(next: DragState): void { this.state = next; /* 対応する描画更新（5.6結合プレビュー等）をここで呼ぶ */ }

  private onPointerUp(hitTester: HitTester, point: Point): void {
    // 遷移の終端で第4章のコマンドを発行する。
    // E（描画）・G（UIシェル）はこの状態機械を経由してのみモデルを変更でき、
    // C・Dへの直接書き込み経路を持たない（2.2の保証をコードレベルでも表現する）。
    this.host.dispatch(/* MoveCellCommand | CreateJoinCommand | MoveJoinBarCommand など */);
  }
}
```

> [!note] `private state`はこのクラスに閉じたUI一時状態であり、モデルではない
> `CLAUDE.md`のイミュータブル方針（既存オブジェクトを変更せず常に新しいオブジェクトを作る）は`TecscdeDocument`・`Cell`・`Command`等の**ドメインデータ**に適用される。`GestureController.state`はドラッグ操作というUI操作1回に閉じた一時的な状態であり、外部に公開されず、ドキュメント（第3章）や履歴（第4章）には一切反映されない。現行実装（[[TECSCDE-JS-TS実装]]）の`gesture.ts`も同じ理由でこのフィールドをprivateな可変状態として持っており、本書はこの既存パターンを踏襲する。

### 5.4 選択状態・ラバーバンド選択

選択状態はモデルの一部ではなく、`SvgRenderer`（または専用の`SelectionState`という小さな値クラス）が保持する一時的なUI状態とする（[[TECSCDE内部仕様]]6.5節と同一の位置付け）。矩形ドラッグによるラバーバンド選択は`HitTester`に矩形版の問い合わせメソッドを追加して対応する。

### 5.5 結合プレビュー線

結合モード中（`DragState.kind === 'joining'`）、`GestureController`が`SvgRenderer`へ仮結線の描画を指示する。モデル（第3章）・履歴（第4章）には一切書き込まない。

## Related

- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 03 画面構成|TECSCDE外部仕様 3. 画面構成]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 06 描画・インタラクション設計|TECSCDE内部仕様 第6章（対応する既存設計）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-TS内部仕様 第4章（本章が発行するコマンド）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様（目次）]]

---
date: 2026-09-05
description: "TECSCDE-DT-TA内部仕様書 第5章（描画・インタラクション設計）— web-sys/wasm-bindgenによるSVG直接操作。SvgRenderer/HitTester/GestureControllerをRustのstructとして再設計。"
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

Domain note split from [[TECSCDE-DT-TA内部仕様]] (2026-09-05). Chapter 5 of 11。

## 5. 描画・インタラクション設計

SVGツリー構造・更新戦略・ヒットテスト優先順位・ドラッグ状態機械の4状態は[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 05 描画・インタラクション設計|TECSCDE-TS内部仕様第5章]]と**同一の挙動**。本章はこれを`web-sys`（RustからWeb APIへの型付きバインディング）で実現する設計に翻訳する。

### 5.1 `SvgRenderer`構造体

```rust
use web_sys::{SvgElement, SvgsvgElement};
use std::collections::HashMap;

pub struct SvgRenderer {
    cell_elements: HashMap<CellId, SvgElement>,
    join_elements: HashMap<JoinId, SvgElement>,
    cell_renderer: CellRenderer,
    join_renderer: JoinRenderer,
}

pub trait ElementRenderer<TModel> {
    fn create_element(&self, model: &TModel) -> SvgElement;
    fn update_element(&self, model: &TModel, element: &SvgElement); // 属性のみ更新、再生成しない
}

pub struct CellRenderer;
impl ElementRenderer<Cell> for CellRenderer { /* 矩形・ラベル・ポート記号。web-sys経由でDOM属性を直接設定 */
    fn create_element(&self, model: &Cell) -> SvgElement { unimplemented!() }
    fn update_element(&self, model: &Cell, element: &SvgElement) {}
}
pub struct JoinRenderer;
impl ElementRenderer<Join> for JoinRenderer { /* 折れ線・シグニチャラベル */
    fn create_element(&self, model: &Join) -> SvgElement { unimplemented!() }
    fn update_element(&self, model: &Join, element: &SvgElement) {}
}

impl SvgRenderer {
    pub fn new(root: &SvgsvgElement) -> SvgRenderer {
        // #cells, #joins, #join-preview, #selection-overlay, #grid の各<g>を生成
        SvgRenderer {
            cell_elements: HashMap::new(), join_elements: HashMap::new(),
            cell_renderer: CellRenderer, join_renderer: JoinRenderer,
        }
    }

    pub fn on_document_changed(&mut self, prev: Option<&TecscdeDocument>, next: &TecscdeDocument) {
        // 差分のあるCell/Joinのみ対応要素を update_element で更新する。
        // 図全体の再描画は行わない（TypeScript版と同じ方針）。
    }
}
```

`[[TECSCDE-TS内部仕様]]`の`ElementRenderer<TModel>`ジェネリック抽象クラスは、Rustではトレイト（`trait ElementRenderer<TModel>`）として同じ形にそのまま翻訳できる——TypeScriptのジェネリック抽象クラスとRustのジェネリックトレイトは、この用途では概ね1対1に対応する。

### 5.2 `HitTester`構造体

```rust
pub struct HitTester<'a> {
    doc: &'a TecscdeDocument,
    renderer: &'a SvgRenderer,
    bar_search_radius_px: f64,
}

impl<'a> HitTester<'a> {
    pub fn new(doc: &'a TecscdeDocument, renderer: &'a SvgRenderer) -> HitTester<'a> {
        HitTester { doc, renderer, bar_search_radius_px: 8.0 }
    }

    pub fn hit_test(&self, point: Point) -> HitResult {
        // 1. ポート → 2. セル本体 → 3. 結合バー（半径内のみ）。[[TECSCDE-TS内部仕様]]5.2節と同一の優先順位
        HitResult::None
    }
}
```

TypeScript版はコンストラクタで`doc`・`renderer`を受け取り、ドキュメントが変わるたびに新しい`HitTester`に差し替えていた。Rust版は**ライフタイム注釈（`'a`）で`doc`・`renderer`への参照が有効な期間をコンパイル時に保証する**——参照先のドキュメントが破棄された後に`HitTester`を使おうとするとコンパイルエラーになり、TypeScript版では実行時にしか気づけない類の不整合が設計段階で排除される。

### 5.3 ドラッグ状態機械（`GestureController`）

```rust
enum DragState {
    Idle,
    OverPort { port: PortId },
    Joining { from: PortId },
    ValidTarget { from: PortId, to: PortId },
}

pub struct GestureController {
    state: DragState,
    svg: SvgsvgElement,
}

impl GestureController {
    fn transition(&mut self, next: DragState) { self.state = next; }

    fn on_pointer_up(&mut self, hit_tester: &HitTester, point: Point) -> Option<Box<dyn Command>> {
        // 遷移の終端で第4章のコマンドを生成して返す。呼び出し元（app層）がHistoryへcommitする。
        None
    }
}
```

TypeScript版の判別可能なUnion型（`type DragState = { kind: 'idle' } | ...`）は、Rustでは**enum（タグ付きユニオン）が言語の第一級機能として直接対応する**——TypeScript版がUnion型で表現していたパターンマッチ（`switch (state.kind)`相当）は、Rustの`match`式が網羅性チェック（全バリアントを処理しないとコンパイルエラー）付きで行える点が実質的な差分である。

> [!note] `state`フィールドの可変性
> [[TECSCDE-TS内部仕様]]5.3節と同じ理由で、`GestureController.state`はこの構造体に閉じたUI一時状態であり、モデル（第3章）や履歴（第4章）には反映されない。Rust版では`&mut self`メソッドを通じてのみ変更可能であり、所有権システムは「同時に複数箇所から`state`を書き換えられない」ことも保証する（借用チェッカーにより、`&mut self`メソッド呼び出し中は他の参照が無効化される）。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 05 描画・インタラクション設計|TECSCDE-TS内部仕様 第5章（一次情報源、挙動は同一）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-DT-TA内部仕様 第4章（本章が生成するコマンド）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様（目次）]]

---

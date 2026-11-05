---
date: 2026-09-05
description: "TECSCDE-DT-TA内部仕様書 第6章（表示制御設計）— ViewState/DisplayFiltersのstruct+impl設計。TecscdeDocumentとは別の型として分離。"
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

Domain note split from [[TECSCDE-DT-TA内部仕様]] (2026-09-05). Chapter 6 of 11。

## 6. 表示制御設計

モジュールF（表示制御）はC・Bから独立し、`.cde`形式に含めない（外部仕様7.5.2）——この境界は[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 06 表示制御設計|TECSCDE-TS内部仕様第6章]]と同一。本章はこれをRustのstructとして表現する。

```rust
pub struct ViewState {
    pub zoom: f64,
    pub pan_center: Point,          // モデル座標系での表示中心
    pub grid_visible: bool,         // 既定false
    pub filters: DisplayFilters,
    pub search_query: Option<String>,
}

impl ViewState {
    pub fn initial() -> ViewState {
        ViewState {
            zoom: 1.0, pan_center: Point { x: 0.0, y: 0.0 },
            grid_visible: false, filters: DisplayFilters::all_visible(), search_query: None,
        }
    }

    pub fn zoom_at(self, point: Point, factor: f64) -> ViewState {
        // 倍率変更時、変更前に中央（またはポインタ位置）にあったモデル座標を変更後も同じ画面位置に保つ
        ViewState { zoom: self.zoom * factor, ..self }
    }
    pub fn toggle_grid(self) -> ViewState { ViewState { grid_visible: !self.grid_visible, ..self } }
    pub fn with_search_query(self, query: Option<String>) -> ViewState { ViewState { search_query: query, ..self } }
}

pub struct DisplayFilters {
    pub region_filter: Option<RegionId>,
    pub namespace_filter: Option<String>,
    pub color_by_region: bool,
    pub show_signature_names: bool,
}

impl DisplayFilters {
    pub fn all_visible() -> DisplayFilters {
        DisplayFilters { region_filter: None, namespace_filter: None, color_by_region: false, show_signature_names: false }
    }
}
```

`ViewState`を`TecscdeDocument`（第3章）とは別の型にすることで「表示フィルタの状態は`.cde`に保存されない」という制約を型システムで表現する方針は[[TECSCDE-TS内部仕様]]第6章と同一。構造体更新構文（`..self`）による不変更新も第3章3.1節と同じ考え方。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 06 表示制御設計|TECSCDE-TS内部仕様 第6章（一次情報源、挙動は同一）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様（目次）]]

---

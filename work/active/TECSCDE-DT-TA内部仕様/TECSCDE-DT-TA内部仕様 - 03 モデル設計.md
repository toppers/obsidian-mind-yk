---
date: 2026-09-05
description: "TECSCDE-DT-TA内部仕様書 第3章（モデル設計）— Cell/CPort/EPort/Join/Region/TecscdeDocumentのstruct+impl設計。所有権システムによる自然な不変性、不変条件の一部をコンストラクタ関数で強制。"
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

Domain note split from [[TECSCDE-DT-TA内部仕様]] (2026-09-05). Chapter 3 of 11。

## 3. モデル設計

### 3.1 方針: 所有権システムによる不変性

[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 03 モデル設計|TECSCDE-TS内部仕様第3章]]は、`readonly`フィールドと「新しいインスタンスを返すメソッド」によって、意図的にイミュータブルな設計を組み立てていた。Rustでは、**所有権システムがこれを言語レベルで後押しする。** メソッドが`self`（参照ではなく値）を受け取ると、呼び出し元の値はムーブ（消費）され、以後アクセスできない——「元の値を書き換えられる余地」自体がコンパイラによって排除される。

```rust
impl Cell {
    pub fn move_to(self, x: f64, y: f64) -> Cell {
        Cell { x: align_round(x), y: align_round(y), ..self } // 構造体更新構文
    }
}
```

不変条件の強制も、TypeScript版の`private`コンストラクタ＋`static create()`と同じ形をRustのイディオムで表現する——コンストラクタ関数（`Cell::create`）をモジュール外から呼べる唯一の生成経路とし、構造体リテラル（`Cell { ... }`）による直接生成はモジュール内に限定する（フィールドを非`pub`にする）。

### 3.2 struct設計

```rust
// model/port.rs
pub struct CPort {
    pub id: PortId,
    pub edge_side: EdgeSide,
    pub offset: f64,               // 辺上位置, mm
    pub subscript: Option<u32>,    // 配列ポートの添字
    pub join_id: Option<JoinId>,   // 結合は最大1本（4.3.1）— Option型そのもので表現
}

impl CPort {
    pub fn create(id: PortId, edge_side: EdgeSide, offset: f64, subscript: Option<u32>) -> CPort {
        CPort { id, edge_side, offset, subscript, join_id: None }
    }
    pub fn with_join(self, join_id: JoinId) -> Result<CPort, InvariantViolation> {
        if self.join_id.is_some() {
            return Err(InvariantViolation::new(format!("CPort {:?} already joined", self.id)));
        }
        Ok(CPort { join_id: Some(join_id), ..self })
    }
    pub fn without_join(self) -> CPort { CPort { join_id: None, ..self } }
}

pub struct EPort {
    pub id: PortId,
    pub edge_side: EdgeSide,
    pub offset: f64,
    pub subscript: Option<u32>,
    pub join_ids: Vec<JoinId>,     // 結合は複数可（4.4.1）— Vecそのもので表現
}

impl EPort {
    pub fn create(id: PortId, edge_side: EdgeSide, offset: f64, subscript: Option<u32>) -> EPort {
        EPort { id, edge_side, offset, subscript, join_ids: Vec::new() }
    }
    pub fn with_join(mut self, join_id: JoinId) -> EPort { self.join_ids.push(join_id); self }
    pub fn without_join(mut self, join_id: JoinId) -> EPort { self.join_ids.retain(|j| *j != join_id); self }
}
```

`CPort`・`EPort`は、TypeScript版が`abstract class Port`からの継承で共通化していた`edge_side`／`offset`／`subscript`を、**継承ではなく単純な重複したフィールドとして**持つ（Rustに継承はなく、共通化するなら委譲か別structへの切り出しになるが、フィールド4つ程度の重複は許容範囲と判断する）。「呼び口=結合1本まで／受け口=複数可」という不変条件は、TypeScript版と同じく**型そのもの**（`Option<JoinId>` 対 `Vec<JoinId>`）で表現される——この点はRustでも変わらない。

```rust
// model/cell.rs
pub struct Cell {
    pub id: CellId,
    pub name: String,
    pub celltype_ref: CelltypeRef,
    pub x: f64, pub y: f64,             // mm, ALIGN丸め済み
    pub width: f64, pub height: f64,
    pub region_id: RegionId,
    pub editable: bool,                  // 10.2.1: locale基準
    pub cports: Vec<CPort>,
    pub eports: Vec<EPort>,
}

impl Cell {
    pub fn create(params: CellCreateParams) -> Result<Cell, InvariantViolation> {
        assert_identifier_syntax(&params.name)?;          // 4.8.1, 6.5.1
        let x = align_round(params.x);
        let y = align_round(params.y);                     // 4.1.1, 7.2.2
        Ok(Cell { x, y, ..params.into() })
    }

    pub fn move_to(self, x: f64, y: f64) -> Cell {
        Cell { x: align_round(x), y: align_round(y), ..self }
    }
}
```

```rust
// model/join.rs
pub struct Join {
    pub id: JoinId,
    pub cport_id: PortId,
    pub eport_id: PortId,
    pub bars: Vec<Bar>,   // HBar/VBarの列
}

impl Join {
    pub fn create(id: JoinId, cport: &CPort, eport: &EPort, bars: Vec<Bar>) -> Result<Join, InvariantViolation> {
        if cport.join_id.is_some() {
            return Err(InvariantViolation::new(format!("CPort {:?} already has a join", cport.id))); // 4.3.1
        }
        Ok(Join { id, cport_id: cport.id, eport_id: eport.id, bars })
    }

    pub fn move_bar(mut self, index: usize, delta: Point) -> Join {
        if let Some(bar) = self.bars.get_mut(index) { *bar = bar.moved_by(delta); }
        self
    }
}
```

```rust
// model/region.rs
pub struct Region {
    pub id: RegionId,
    pub namespace_path: String,     // 4.8: 識別子を兼ねる
    pub children: Vec<Region>,      // Composite パターン
    pub cell_ids: Vec<CellId>,
}

impl Region {
    pub fn add_cell(mut self, cell_id: CellId) -> Region { self.cell_ids.push(cell_id); self }
}

pub struct RegionTree { pub root: Region }

impl RegionTree {
    pub fn find_by_id(&self, id: &RegionId) -> Option<&Region> { /* rootから再帰探索 */ None }
}
```

```rust
// model/document.rs
pub struct TecscdeDocument {
    cells: im::HashMap<CellId, Cell>,   // im crate: 構造共有を持つ永続データ構造
    joins: im::HashMap<JoinId, Join>,
    pub regions: RegionTree,
    pub tool_info_tecsgen: ToolInfoTecsgen,  // 5.1.2: 解釈せず保持するだけ
    pub paper: PaperSpec,
}

impl TecscdeDocument {
    pub fn empty() -> TecscdeDocument {
        TecscdeDocument {
            cells: im::HashMap::new(), joins: im::HashMap::new(),
            regions: RegionTree::empty(), tool_info_tecsgen: ToolInfoTecsgen::empty(),
            paper: PaperSpec::default(),
        }
    }

    pub fn get_cell(&self, id: &CellId) -> Option<&Cell> { self.cells.get(id) }
    pub fn get_join(&self, id: &JoinId) -> Option<&Join> { self.joins.get(id) }
    pub fn cell_count(&self) -> usize { self.cells.len() }

    pub fn with_cell(mut self, cell: Cell) -> TecscdeDocument {
        self.cells.insert(cell.id.clone(), cell);
        self
    }
    pub fn without_cell(mut self, id: &CellId) -> TecscdeDocument {
        self.cells.remove(id);
        self
    }
    // cells/joinsフィールドはprivate（非pub）— 問い合わせメソッド越しにのみアクセスさせる
    // （TypeScript版のTecscdeDocumentと同じカプセル化方針）
}
```

**`im`クレート（永続データ構造、structural sharing）の採用は本書固有の提案である。** TypeScript版は`new Map(this.cellsById)`で更新のたびにMap全体を浅くコピーしていた（3.3節でO(履歴長)のトレードオフとして言及済み）。Rustでは`im::HashMap`（Rc/構造共有ベースの永続ハッシュマップ）を使うことで、`with_cell`が1要素の変更であってもO(1)〜O(log n)に近いコストで新しいインスタンスを得られる——ただし本書はこれを必須要件とはせず、標準の`std::collections::HashMap`を`clone()`する素朴な実装から始め、性能上の必要が生じた場合に`im`クレートへ切り替える余地として記す(unverified／実装時の判断)。

### 3.3 不変条件の対応表

[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 03 モデル設計|TECSCDE-TS内部仕様3.3節]]の6項目と対応は同一。表現方法の差分のみ記す。

| # | 不変条件 | Rustでの表現方法 |
|---|---|---|
| 1 | ALIGN丸め | `Cell::create`/`move_to`内で`align_round()`を強制適用（関連関数） |
| 2 | 呼び口=結合1本まで／受け口=複数可 | `Option<JoinId>` と `Vec<JoinId>` という型そのもの（コンパイル時） |
| 3 | ポートは所属辺上のみ移動可 | `CPort`/`EPort`に辺変更用のメソッドを設けない（型システムでは強制しきれない設計上の欠落） |
| 4 | 識別子構文 | `Cell::create`内の`assert_identifier_syntax()`。戻り値`Result`でコンパイル時にエラー処理を強制する（TypeScript版の`throw`と異なり、呼び出し側は`?`演算子等での処理が必須） |
| 5 | `editable`はlocale基準 | 呼び出し元（B: CDLパーサ）が`locale`を判定して渡す |
| 6 | 配列ポート添字0削除不可 | セルの「ポート削除」メソッドで`subscript == Some(0)`を拒否する実装が必要（第4〜5章で扱う） |

Rust版の#4は、TypeScript版の`throw`ベースの例外と異なり`Result<Cell, InvariantViolation>`を返すため、**呼び出し側がエラーハンドリングを怠るとコンパイルが通らない**——TypeScript版では`try/catch`を書き忘れても実行時まで問題が顕在化しないのに対し、Rust版はコンパイル時に強制される点が実質的な差分である。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 03 モデル設計|TECSCDE-TS内部仕様 第3章（クラス設計の一次情報源）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-TA内部仕様 第2章（本モジュールのプロセス配置根拠）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様（目次）]]

---

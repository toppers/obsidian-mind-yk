---
date: 2026-09-05
description: "TECSCDE-TS内部仕様書 第3章（モデル設計）— Cell/Port/Join/Region/TecscdeDocumentのクラス設計。不変条件の一部を型階層とファクトリメソッドで強制する。"
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

Domain note split from [[TECSCDE-TS内部仕様]] (2026-09-05). Chapter 3 of 12.

## 3. モデル設計

### 3.1 方針: クラスによるカプセル化 + 不変データ

[[TECSCDE内部仕様]]第3章はモデルを`readonly`フィールドのみを持つ plain interface として定義し、型で表現しきれない不変条件（3.3節の6項目）を`invariants.ts`の独立した検証関数群に委ねている。本書はこれをクラスに置き換え、次の2点を狙う。

1. **一部の不変条件を型階層自体で表現する。** 特に「呼び口（CPort）は結合が最大1本、受け口（EPort）は複数可」（外部仕様4.3.1・4.4.1）は、`CPort.joinId: JoinId | null`（単一の値）と`EPort.joinIds: readonly JoinId[]`（配列）という**フィールドの型そのもの**で表現できる。事後検証に頼らず、この不変条件を破るデータはそもそも構築できない。
2. **残りの不変条件を`static create()`ファクトリメソッドに閉じ込める。** ALIGN丸め・識別子構文など、型だけでは表現しきれない制約は、コンストラクタを`private`にし、`static create()`内で検証・正規化してから初期化することで、「検証を経ていないインスタンスが存在しない」ことを保証する。

クラスの導入は可変状態を許容しない。全フィールドは`readonly`のまま、状態変更は新しいインスタンスを返すメソッド（`moveTo`・`withPort`等）を通じてのみ行う（1.3節参照）。コミット粒度は外部仕様6.2.2・6.3.2が定める「ドラッグ完了」「一括削除」単位のままであり、[[TECSCDE内部仕様]]3.1節と同様、mousemoveごとの不変更新コストは実用上問題にならない。

### 3.2 クラス設計

| クラス | 対応する外部仕様 | 要点 |
|---|---|---|
| `Port`（抽象基底） | 4.3 / 4.4 | `edgeSide`・`offset`・`subscript`の共通フィールドのみを持つ。それ自体はインスタンス化しない |
| `CPort extends Port` | 4.3 | 追加フィールド`joinId: JoinId \| null`。結合0〜1本という制約を型で表現 |
| `EPort extends Port` | 4.4 | 追加フィールド`joinIds: readonly JoinId[]`。結合0〜複数という制約を型で表現 |
| `Cell` | 4.1 | `static create()`でALIGN丸め・識別子構文を検証。`moveTo`・`withPort`等は新しい`Cell`を返す |
| `Join` | 4.6 | `static create(cport, eport)`が「CPort側は未結合であること」をここで検証してから`Join`を生成する（生成後の`CPort`は`withJoin`で更新） |
| `Region` / `RegionTree` | 4.9 | Composite パターン。`Region.children: readonly Region[]` |
| `CelltypeRef` / `SignatureRef` | 4.2 / 4.5 | 参照のみを保持する値クラス（あるいは単純な値オブジェクト）。編集対象には含めない |
| `TecscdeDocument` | — | ルート集約。内部の`Map`をprivateフィールドとして隠蔽し、`getCell`/`withCell`等の問い合わせ・更新メソッドのみを公開する |

```ts
abstract class Port {
  protected constructor(
    readonly id: PortId,
    readonly edgeSide: EdgeSide,
    readonly offset: number,      // 辺上位置, mm
    readonly subscript: number | null, // 配列ポートの添字
  ) {}
}

class CPort extends Port {
  private constructor(
    id: PortId, edgeSide: EdgeSide, offset: number, subscript: number | null,
    readonly joinId: JoinId | null,   // 結合は最大1本（4.3.1）— 配列ではなく単一値
  ) { super(id, edgeSide, offset, subscript); }

  static create(id: PortId, edgeSide: EdgeSide, offset: number, subscript: number | null): CPort {
    return new CPort(id, edgeSide, offset, subscript, null);
  }
  withJoin(joinId: JoinId): CPort {
    if (this.joinId !== null) throw new InvariantViolation(`CPort ${this.id} already joined`);
    return new CPort(this.id, this.edgeSide, this.offset, this.subscript, joinId);
  }
  withoutJoin(): CPort {
    return new CPort(this.id, this.edgeSide, this.offset, this.subscript, null);
  }
}

class EPort extends Port {
  private constructor(
    id: PortId, edgeSide: EdgeSide, offset: number, subscript: number | null,
    readonly joinIds: readonly JoinId[],  // 結合は複数可（4.4.1）
  ) { super(id, edgeSide, offset, subscript); }

  static create(id: PortId, edgeSide: EdgeSide, offset: number, subscript: number | null): EPort {
    return new EPort(id, edgeSide, offset, subscript, []);
  }
  withJoin(joinId: JoinId): EPort {
    return new EPort(this.id, this.edgeSide, this.offset, this.subscript, [...this.joinIds, joinId]);
  }
  withoutJoin(joinId: JoinId): EPort {
    return new EPort(this.id, this.edgeSide, this.offset, this.subscript,
      this.joinIds.filter(j => j !== joinId));
  }
}
```

```ts
class Cell {
  private constructor(
    readonly id: CellId,
    readonly name: string,
    readonly celltypeRef: CelltypeRef,
    readonly x: number, readonly y: number,       // mm, ALIGN丸め済み
    readonly width: number, readonly height: number,
    readonly regionId: RegionId,
    readonly editable: boolean,                    // 10.2.1: locale基準
    readonly cports: readonly CPort[],
    readonly eports: readonly EPort[],
  ) {}

  static create(params: CellCreateParams): Cell {
    assertIdentifierSyntax(params.name);           // 4.8.1, 6.5.1
    const x = alignRound(params.x), y = alignRound(params.y); // 4.1.1, 7.2.2
    return new Cell(params.id, params.name, params.celltypeRef, x, y,
      params.width, params.height, params.regionId, params.editable,
      params.cports, params.eports);
  }

  moveTo(x: number, y: number): Cell {
    return new Cell(this.id, this.name, this.celltypeRef,
      alignRound(x), alignRound(y), this.width, this.height,
      this.regionId, this.editable, this.cports, this.eports);
  }

  withCPort(port: CPort): Cell { /* cports配列中の該当idを置換した新しいCellを返す */ }
  withEPort(port: EPort): Cell { /* 同上 */ }
}
```

```ts
class Join {
  private constructor(
    readonly id: JoinId,
    readonly cportId: PortId,
    readonly eportId: PortId,
    readonly bars: readonly Bar[],   // HBar/VBarの列
  ) {}

  static create(id: JoinId, cport: CPort, eport: EPort, bars: readonly Bar[]): Join {
    if (cport.joinId !== null) {
      throw new InvariantViolation(`CPort ${cport.id} already has a join`); // 4.3.1
    }
    return new Join(id, cport.id, eport.id, bars);
  }

  moveBar(index: number, delta: Point): Join {
    const nextBars = this.bars.map((b, i) => i === index ? b.movedBy(delta) : b);
    return new Join(this.id, this.cportId, this.eportId, nextBars);
  }
}
```

```ts
class Region {
  private constructor(
    readonly id: RegionId,
    readonly namespacePath: string,        // 4.8: 識別子を兼ねる
    readonly children: readonly Region[],  // Composite パターン
    readonly cellIds: readonly CellId[],
  ) {}

  addCell(cellId: CellId): Region {
    return new Region(this.id, this.namespacePath, this.children, [...this.cellIds, cellId]);
  }
}

class RegionTree {
  private constructor(readonly root: Region) {}

  findById(id: RegionId): Region | undefined { /* rootから再帰探索 */ return undefined; }
}
```

```ts
class TecscdeDocument {
  private constructor(
    private readonly cellsById: ReadonlyMap<CellId, Cell>,
    private readonly joinsById: ReadonlyMap<JoinId, Join>,
    readonly regions: RegionTree,
    readonly toolInfoTecsgen: ToolInfoTecsgen,  // 5.1.2: 解釈せず保持するだけ
    readonly paper: PaperSpec,
    // 4.1/4.6: モデルに反映しない構文（import / import_C）を入力時のテキストの
    // まま保持し、保存時にそのまま書き戻す。参照先は追跡しない（外部仕様8.1.2）
    readonly preservedImports: readonly string[] = [],
  ) {}

  static empty(): TecscdeDocument {
    return new TecscdeDocument(new Map(), new Map(), RegionTree.empty(),
      ToolInfoTecsgen.empty(), PaperSpec.default(), []);
  }

  getCell(id: CellId): Cell | undefined { return this.cellsById.get(id); }
  getJoin(id: JoinId): Join | undefined { return this.joinsById.get(id); }
  get cellCount(): number { return this.cellsById.size; }

  withCell(cell: Cell): TecscdeDocument {
    const next = new Map(this.cellsById);
    next.set(cell.id, cell);
    return new TecscdeDocument(next, this.joinsById, this.regions,
      this.toolInfoTecsgen, this.paper);
  }
  withoutCell(id: CellId): TecscdeDocument {
    const next = new Map(this.cellsById);
    next.delete(id);
    return new TecscdeDocument(next, this.joinsById, this.regions,
      this.toolInfoTecsgen, this.paper);
  }
  // cells/joins のMapそのものは公開しない（カプセル化）——
  // 既存内部仕様の interface 版は ReadonlyMap を直接公開していたが、
  // 本書はこれをprivateにし、問い合わせメソッド越しにのみアクセスさせる
}
```

> [!info] `preservedImports` は2026-09-13に追加した
> [[TECSCDE内部仕様]]4.1/4.6節の改訂（モデルに反映しない構文はCST上の区間として保持し、保存時にそのまま書き戻す）に対応する。**[[TECSCDE-JS-TS実装]]では、CDL本体の`import`文が解析はされるものの保存時に消えていた**（シリアライザに出力経路が無かった）——同日の移行で修正済み。本書の実装が新規に書き起こされる際に同じ欠落を作らないよう、モデル側の保持枠として明示する。
>
> `toolInfoTecsgen`が「解釈せず保持する」のと動機は同じだが、対象が異なる——前者は`__tool_info__`のJSON、後者はCDL本体の構文である。どちらも**本ツールが意味を与えない情報を往復で失わない**ための枠であり、第3章3.3節の不変条件とは別の軸（保存の完全性）に属する。

### 3.3 不変条件の対応表

| # | 不変条件 | 根拠 | 本書での表現方法 |
|---|---|---|---|
| 1 | 座標・寸法は`ALIGN = 1.0mm`の倍数 | 4.1.1, 7.2.2 | `Cell.create()`/`moveTo()`内で`alignRound()`を強制適用（ファクトリメソッド） |
| 2 | 呼び口の結合は最大1本、受け口は複数可 | 4.3.1, 4.4.1 | `CPort.joinId: JoinId \| null` と `EPort.joinIds: readonly JoinId[]` という**型そのもの**で表現（コンパイル時） |
| 3 | ポートは所属辺上のオフセットのみ変更可能 | 4.3.2 | `Port`に辺変更用のメソッドを設けない（設計上の欠落として表現——型システムでは強制しきれない） |
| 4 | セル名・ネームスペース識別子は`[A-Za-z_][0-9A-Za-z_]*`に一致 | 4.8.1, 6.5.1 | `Cell.create()`内の`assertIdentifierSyntax()`（ファクトリメソッド） |
| 5 | `editable`は`locale`基準で決まる | 10.2.1 | `Cell.create()`の呼び出し元（B: CDLパーサ）が`locale`を判定して渡す。クラス自体は値を保持するのみ |
| 6 | 配列ポートの添字0要素は削除できない | 10.3 #5 | `Cell`の「ポート削除」系メソッドで、`subscript === 0`の要素を拒否する実装が必要（本書ではメソッドシグネチャのみ示し、詳細は第4〜5章[未着手]で扱う） |

不変条件6項目のうち、#2は型階層で完全にコンパイル時保証されるが、#1・#4はファクトリメソッドでの実行時検証、#3・#5・#6は設計上の制約（メソッドを提供しない、呼び出し元の責務とする）にとどまり、クラス化によって全ての不変条件が型レベルで保証されるわけではないことに注意する。

## Related

- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 04 コンポーネント図の表現|TECSCDE外部仕様 4. コンポーネント図の表現]] — 本章の型設計の根拠
- [[TECSCDE内部仕様]] — 第3章（対応する既存の interface ベース設計）との比較対象
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様（目次）]]

---
date: 2026-09-05
description: "TECSCDE-TS内部仕様書 第6章（表示制御設計）— ViewStateクラスにズーム/パン/グリッド/フィルタ/検索を集約し、モデルから独立させる。"
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

Domain note split from [[TECSCDE-TS内部仕様]] (2026-09-05). Chapter 6 of 11（[[TECSCDE内部仕様]]の第7章に対応）。

## 6. 表示制御設計

モジュールF（表示制御）はC（モデル）・B（パーサ）から独立し、`.cde`形式に含めない（外部仕様7.5.2）——この境界は実装方式に関わらず不変であり、[[TECSCDE内部仕様]]第7章と同一である。本章はこれを1つの`ViewState`クラスとして表現する。

### 6.1 `ViewState`クラス

```ts
class ViewState {
  private constructor(
    readonly zoom: number,
    readonly panCenter: Point,          // モデル座標系での表示中心
    readonly gridVisible: boolean,      // 既定false（現行版と同じ見た目）
    readonly filters: DisplayFilters,   // リージョン/ネームスペース/シグニチャ名
    readonly searchQuery: string | null,
  ) {}

  static initial(): ViewState {
    return new ViewState(1.0, { x: 0, y: 0 }, false, DisplayFilters.allVisible(), null);
  }

  zoomAt(point: Point, factor: number): ViewState {
    // 7.1.2: 倍率変更時、変更前に中央（またはポインタ位置）にあったモデル座標を変更後も同じ画面位置に保つ
    return new ViewState(this.zoom * factor, /* 再計算したpanCenter */ this.panCenter,
      this.gridVisible, this.filters, this.searchQuery);
  }
  panBy(delta: Point): ViewState { /* ... */ return this; }
  toggleGrid(): ViewState {
    return new ViewState(this.zoom, this.panCenter, !this.gridVisible, this.filters, this.searchQuery);
  }
  withFilters(filters: DisplayFilters): ViewState {
    return new ViewState(this.zoom, this.panCenter, this.gridVisible, filters, this.searchQuery);
  }
  withSearchQuery(query: string | null): ViewState {
    return new ViewState(this.zoom, this.panCenter, this.gridVisible, this.filters, query);
  }
}
```

`ViewState`は`TecscdeDocument`（第3章）と同様に不変クラスとして設計するが、**`TecscdeDocument`とは別の型**にすることで、「表示フィルタの状態はモデルの一部ではなく`.cde`に保存されない」（7.5.2）という制約を型システムでも表現する——シリアライザ（第4章の対象外、既存内部仕様4章に相当）は`ViewState`を一切参照しないため、保存対象外フィールドを意識して除外する必要がない。

### 6.2 グリッド表示

グリッド単位（`ALIGN = 1.0mm`、第3章3.3節#1）自体は変更不可の定数であり、`ViewState.gridVisible`は表示・非表示の切り替えのみを持つ。ドラッグ中の現在座標（mm）をステータス表示（モジュールG）に常時反映する。

### 6.3 ナビゲータ

用紙全体の縮小表示＋現在の表示範囲を示す矩形は、`ViewState`（`zoom`・`panCenter`）と`PaperSpec`（第3章の`TecscdeDocument`が保持）の両方から算出する読み取り専用の派生値であり、`ViewState`自体にフィールドとして持たせない。用紙全体が表示範囲に収まる縮小率のときは自動非表示にする（7.3.2）。

### 6.4 検索

`ViewState.searchQuery`はフィルタ（`DisplayFilters`）とは独立にモデル全体を対象として検索する。フィルタで非表示の要素がヒットした場合はフィルタを一時的に緩めて強調表示する（7.4.2）。検索ハイライトの巡回機構は、第8章（未着手、[[TECSCDE内部仕様]]9章に対応）の警告一覧からのジャンプ操作としても共用する。

### 6.5 表示フィルタ

```ts
class DisplayFilters {
  private constructor(
    readonly regionFilter: RegionId | null,
    readonly namespaceFilter: string | null,
    readonly colorByRegion: boolean,
    readonly showSignatureNames: boolean,
  ) {}
  static allVisible(): DisplayFilters { return new DisplayFilters(null, null, false, false); }
}
```

非表示リージョンに属するセルへの結合は完全に消さず、非表示側の境界にスタブ記号を描く（7.5.2、描画側は第5章の`JoinRenderer`が担当）。

## Related

- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 07 表示機能|TECSCDE外部仕様 7. 表示機能]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 07 表示制御設計|TECSCDE内部仕様 第7章（対応する既存設計）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様（目次）]]

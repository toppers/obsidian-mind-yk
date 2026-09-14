---
date: 2026-08-30
description: "TECSCDE内部仕様書 第3章（モデル設計）— Cell/Port/Join/Region/Signature の型定義と不変条件"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note split from [[TECSCDE内部仕様]] (2026-08-30, 25KB threshold). Chapter 3 of 12.

## 3. モデル設計

### 3.1 方針: 不変データ構造

モジュールC（モデル）は、TypeScriptでは**不変（immutable）なデータ構造**として定義する。理由は2つある。

1. 5章で規定するコマンドの`apply`/`invert`を「ドキュメントの新しいスナップショットを返す純粋関数」として実装すると、現行版のアンドゥ機構が持っていた2件の不具合（外部仕様6.6.1: 初回コミットのUndo不可、Redoの恒久無効化）の温床になっていた「変更前状態のコピー漏れ」という問題自体が構造的に発生しなくなる。
2. 「Cのみに依存する」というモジュール境界（2.2）を、TypeScriptの型システムでも表現できる。`readonly`修飾と`ReadonlyMap`により、Cを読むモジュール（D以外の全モジュール）がCを書き換えられないことをコンパイル時に保証する。

コミット粒度は外部仕様6.2.2・6.3.2が定める「ドラッグ完了」「一括削除」単位に絞られるため、mousemoveのたびに不変更新のコストが発生するわけではない。ドラッグ中の暫定表示は6章で述べる「コミット前のプレビュー状態」で別途扱い、モデル本体への書き込みはドラッグ完了時の1回に限る。

### 3.2 型定義

| 型 | 対応する外部仕様 | 要点 |
|---|---|---|
| `CellId` / `PortId` / `JoinId` / `RegionId` | — | Brand型による識別子。生の`string`との混同を型で防ぐ |
| `Cell` | 4.1 | `x`/`y`/`width`/`height`（mm, ALIGN丸め済み）、`editable`（10.2.1: locale基準）、`cports`/`eports` |
| `CPort` / `EPort` | 4.3 / 4.4 | `edgeSide`（4値）、`offset`（辺上位置、mm）、`subscript`（配列添字、なしを許容）。共通の`Port`を基底に持つ |
| `Join` | 4.6 | `cportId`・`eportId`、`bars`（`HBar`/`VBar`の列） |
| `RegionTree` | 4.9 | 木構造。`namespacePath`が識別子を兼ねる（4.8） |
| `CelltypeRef` / `SignatureRef` | 4.2 / 4.5 | 参照のみ。定義そのものは編集対象に含めない |
| `ToolInfoTecsgen` | 5.1.1① | `base_dir`・`import_path`・`cpp`等。**解釈せず保持するだけの不透明な値**として持つ（5.1.2） |
| `TecscdeDocument` | — | 上記を束ねるルート集約 |

```ts
interface TecscdeDocument {
  readonly cells: ReadonlyMap<CellId, Cell>;
  readonly joins: ReadonlyMap<JoinId, Join>;
  readonly regions: RegionTree;
  readonly toolInfoTecsgen: ToolInfoTecsgen; // opaque, round-trip only
  readonly paper: PaperSpec;
}
```

### 3.3 不変条件

コンパイル時の型では表現しきれない不変条件は`invariants.ts`にアサーション関数として集約し、コマンド適用後に（開発ビルドでのみ）検証する。

| # | 不変条件 | 根拠 |
|---|---|---|
| 1 | 座標・寸法は`ALIGN = 1.0mm`の倍数 | 4.1.1, 7.2.2 |
| 2 | 呼び口の結合は最大1本、受け口は複数可 | 4.3.1, 4.4.1（10.3 #3） |
| 3 | ポートは所属辺上のオフセットのみ変更可能（辺の変更は別操作） | 4.3.2（10.3 #1） |
| 4 | セル名・ネームスペース識別子は`[A-Za-z_][0-9A-Za-z_]*`に一致 | 4.8.1, 6.5.1 |
| 5 | `editable`はセルの`locale`（定義元ファイル）が編集対象ファイルかどうかで決まり、拡張子や参照経路では決めない | 10.2.1 |
| 6 | 配列ポートの添字0要素は削除できない | 10.3 #5 |

これらは「モデルが常に満たす制約」であり、コマンド（D）はこれを破る変更を生成してはならない。パーサ（B）が読み込み時にこれらを満たさないデータに遭遇した場合はモデルを拒否するのではなく、9章で規定する警告に落として続行する（外部仕様の「エラーで中断しない」方針、9.1.2）。

## Related

- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 04 コンポーネント図の表現|TECSCDE外部仕様 4. コンポーネント図の表現]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様|TECSCDE内部仕様（目次）]]

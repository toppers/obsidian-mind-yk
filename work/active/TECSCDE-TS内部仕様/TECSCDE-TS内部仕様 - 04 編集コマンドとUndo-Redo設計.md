---
date: 2026-09-05
description: "TECSCDE-TS内部仕様書 第4章（編集コマンドとUndo-Redo設計）— Command抽象クラス（apply/invert()なし）とHistoryクラス。replay計算・past/future操作をHistory内にカプセル化する。"
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

Domain note split from [[TECSCDE-TS内部仕様]] (2026-09-05). Chapter 4 of 12（[[TECSCDE内部仕様]]の第5章「編集コマンドとUndo-Redo設計」に対応。本書は独立したCDLパーサ／シリアライザ章を設けないため章番号が1つ前倒しになっている——詳細は[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|目次]]の注記を参照）。

## 4. 編集コマンドとUndo-Redo設計

### 4.1 前提: replayベース`History`の決定を踏襲する

Undo/Redoの方式そのもの（`invert()`を持つコマンドパターンではなく、初期ドキュメント+適用済みコマンド列を再生する`History`）は、実装段階で確定済みの決定であり（[[work/active/tecs/TECSCDE Undo-Redo設計決定|Decision Record]]）、本章はこれを再検討しない。クラスベース化によって変わるのは、この決定を**どう表現するか**であり、決定の中身ではない。

### 4.2 `Command`抽象クラス

```ts
abstract class Command {
  abstract readonly kind: string;
  readonly summary?: string; // UIのステータス表示・履歴一覧向けの短い説明（任意）

  abstract apply(doc: TecscdeDocument): TecscdeDocument;
  // invert() は持たない — [[work/active/tecs/TECSCDE Undo-Redo設計決定|Decision Record]]の決定どおり、
  // 逆操作の実装ミスが逆方向にだけ壊れる非対称バグの発生源を、
  // クラス階層のレベルでも作らない（サブクラスにinvert()を書く余地自体を与えない）
}
```

既存の[[TECSCDE内部仕様]]第5章は`interface Command`として同じ形を定義している。クラス化による差分は小さいが、`abstract class`にすることで「`apply`を実装しないコマンドは型エラーになる」という強制がより明確になる（interfaceでも同じ強制は効くため、これは表現上の差にとどまる）。

### 4.3 `History`クラス — replay計算とpast/future操作のカプセル化

既存の[[TECSCDE内部仕様]]第5章は`History`を`{ initial, past, future }`のplain interfaceとして定義し、現在のドキュメントを求める`past.reduce((doc, cmd) => cmd.apply(doc), initial)`という計算を**呼び出し側**が毎回書く設計になっている。本書はこれをクラスのメソッド・アクセサとしてカプセル化する。

```ts
class History {
  private constructor(
    private readonly initial: TecscdeDocument,
    readonly past: readonly Command[],   // 適用済み（Undoで巻き戻せる）
    readonly future: readonly Command[], // Undoされた分（Redoで進められる）
  ) {}

  static begin(initial: TecscdeDocument): History {
    return new History(initial, [], []);
  }

  /** 現在のドキュメント。past を initial へ再生して求める（O(履歴長)、4.4のトレードオフ参照） */
  get current(): TecscdeDocument {
    return this.past.reduce((doc, cmd) => cmd.apply(doc), this.initial);
  }

  get canUndo(): boolean { return this.past.length > 0; }
  get canRedo(): boolean { return this.future.length > 0; }

  /** 新しいコマンドを確定する。future は破棄する（一般的な線形履歴） */
  commit(command: Command): History {
    return new History(this.initial, [...this.past, command], []);
  }

  undo(): History {
    if (!this.canUndo) throw new InvariantViolation('cannot undo: past is empty');
    const last = this.past[this.past.length - 1]!;
    return new History(this.initial, this.past.slice(0, -1), [last, ...this.future]);
  }

  redo(): History {
    if (!this.canRedo) throw new InvariantViolation('cannot redo: future is empty');
    const [next, ...rest] = this.future;
    return new History(this.initial, [...this.past, next!], rest);
  }
}
```

`past`・`future`は直接公開している（既存内部仕様と同様、履歴一覧UIが列挙できる必要があるため）が、**現在のドキュメントを求める計算（`current`）と、Undo/Redo時の配列操作は`History`の外に漏らさない**。これにより、呼び出し側（UIシェル・アプリ層）は`canUndo`/`canRedo`/`current`/`commit`/`undo`/`redo`という意図の明確なAPIだけを使い、「`past.length > 0`かどうかをUndoボタンの活性判定に使う」といった判定ロジックの重複が複数箇所に散らばることを防ぐ。

外部仕様6.6.1が定める現行版2件の不具合（初回コミットのUndo不可・Redo恒久無効）の解消方針は[[TECSCDE内部仕様]]5.3節と同一であり、本章のクラス設計はこれを`canUndo`/`canRedo`という2つのアクセサに集約する形で表現する——`past.length > 0`という条件式そのものをUI層のあちこちに書かせない、という点が既存のplain interface設計との実質的な差分である。

> [!note] トレードオフ（既存内部仕様5.2節と同一）
> `current`にアクセスするたびに`past`全体を先頭から再生するため、コストは履歴の長さに比例する（O(履歴長)）。単一セッション内の編集規模では実用上問題にならない。非常に長時間の編集セッションで体感遅延が出た場合は、`History`クラス内部にNコマンドごとのスナップショットキャッシュを追加する余地がある——これは`History`の外部インタフェース（`current`/`commit`/`undo`/`redo`）を変えずに実装できるカプセル化の利点である。

### 4.4 コミット粒度

外部仕様が定める「1操作＝1アンドゥ単位」は実装方式に依存しない。[[TECSCDE内部仕様]]5.4節の表（ドラッグ移動=mouseup時に1コマンド・一括削除=全体で1コマンド・属性確定=確定イベントごと・矢印キー移動=1入力=1コマンド）をそのまま踏襲する。ドラッグ中の暫定表示はコマンド未確定のプレビュー状態として描画層（第5章、未着手）が保持し、`History`には反映しない。

### 4.5 コマンドクラス一覧

| コマンドクラス | 対応する外部仕様 | 備考 |
|---|---|---|
| `AddCellCommand` | 6.1.2 | セルタイプ未選択時は生成しない（9章[未着手]で促す） |
| `MoveCellCommand` / `MovePortCommand` | 6.2.2 | ポートは所属辺内オフセットのみ変更（`Port`のフィールドに辺変更メソッドを設けないことと対応、第3章3.3節#3） |
| `ChangePortEdgeCommand` | 4.3.2 | 辺をまたぐ変更を明示的な操作として分離 |
| `DeleteCommand` | 6.3.2 | カスケード削除。結合バー・呼び口・受け口いずれの選択からも呼べる |
| `CreateJoinCommand` | 6.4.2 | `Join.create()`（第3章）のバリデーション（CPort未結合であること）をコマンド生成前のガードとして呼ぶ |
| `DeleteJoinCommand` | 6.4.2 | `CPort.withoutJoin()` / `EPort.withoutJoin()`（第3章）を用いて結合を解除する |
| `MoveJoinBarCommand` | 6.2.2 | `Join.moveBar()`（第3章）を呼ぶ。ドラッグしたバー自身を直接動かし、隣接バーは直交を保つよう自動調整 |
| `EditAttrCommand` / `RenameCellCommand` / `ChangeRegionCommand` | 6.5.2 | `RenameCellCommand`は`Cell.create()`の識別子構文検証（第3章3.3節#4）を再度通す |
| `CopyCommand`（履歴を作らない） / `PasteCommand` / `CutCommand` | 6.7.2 | `CopyCommand`は`History.commit()`を呼ばない特殊な操作として扱う。`CutCommand`は内部で`PasteCommand`の逆＋`DeleteCommand`相当を1コマンドに合成する |
| `AlignTopCommand` / `AlignLeftCommand` | 7.3.2 | 複数選択の整列。基準は選択順で最初のセル |

各コマンドクラスのコンストラクタは、そのコマンドの実行に必要なパラメータ（対象ID・新しい値等）のみを`readonly`フィールドとして保持する。例:

```ts
class MoveCellCommand extends Command {
  readonly kind = 'MoveCell';

  constructor(
    private readonly cellId: CellId,
    private readonly toX: number,
    private readonly toY: number,
  ) { super(); }

  apply(doc: TecscdeDocument): TecscdeDocument {
    const cell = doc.getCell(this.cellId);
    if (!cell) throw new InvariantViolation(`Cell ${this.cellId} not found`);
    return doc.withCell(cell.moveTo(this.toX, this.toY));
  }
}
```

`apply`は`Cell.moveTo()`（第3章、ALIGN丸めをファクトリメソッド内で強制）と`TecscdeDocument.withCell()`（同、新しいインスタンスを返す）という、既に不変条件を保証済みのメソッドだけを呼ぶ。コマンド自身は座標の丸めや識別子検証を重複して行わない——検証責務はモデル層（第3章）に一本化されている。

## Related

- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 06A 編集操作（前半）|TECSCDE外部仕様 6. 編集操作（前半）]]
- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 06B 編集操作（後半）|TECSCDE外部仕様 6. 編集操作（後半、Undo/Redo規定）]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 05 編集コマンドとUndo-Redo設計|TECSCDE内部仕様 第5章（対応する既存の interface ベース設計）]]
- [[work/active/tecs/TECSCDE Undo-Redo設計決定|Decision Record: TECSCDE Undo/RedoをreplayベースのHistoryで実装する]] — 本章が踏襲する前提
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 03 モデル設計|TECSCDE-TS内部仕様 第3章（モデル設計）]] — 本章のコマンドが呼び出すモデルのメソッド群
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様（目次）]]

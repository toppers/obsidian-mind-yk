---
date: 2026-08-30
description: "TECSCDE内部仕様書 第5章（編集コマンドとUndo/Redo設計）— コマンドパターン、現行版2件の不具合の解消方針。実装時にinvert()方式からreplayベースのHistoryへ簡素化（2026-08-30）"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note split from [[TECSCDE内部仕様]] (2026-08-30, 25KB threshold). Chapter 5 of 12.

## 5. 編集コマンドとUndo/Redo設計

### 5.1 コマンドの型

```ts
interface Command {
  readonly kind: string;
  readonly summary?: string; // UIのステータス表示・履歴一覧向けの短い説明（任意）
  apply(doc: TecscdeDocument): TecscdeDocument;
}
```

> [!note] 実装時の設計変更（invert()を採用しない）
> 当初は`apply`と`invert(before, after)`の両方を持たせ、逆操作コマンドでUndoを実現する設計（旧5.1／旧5.2）を構想していた。実装段階で「`past`のコマンド列を初期ドキュメントへ再生（replay）するだけでUndo/Redoが実現できる」ことに気づき、`invert()`は採用しなかった。逆操作を書かずに済む分、「逆操作の実装ミスが逆方向のバグを生む」という発生源自体が存在しなくなり、6.6.1の2件の不具合を防ぐという本章の目的をより単純な手段で達成できる。以下5.2・5.3は実装済みのreplay方式で記述し直したもの。決定の経緯・検討した選択肢・トレードオフは[[work/active/tecs/TECSCDE Undo-Redo設計決定|Decision Record]]を参照。

### 5.2 履歴管理

```ts
interface History {
  readonly initial: TecscdeDocument;   // 履歴の起点（ファイル読込直後 or 空文書）
  readonly past: readonly Command[];   // 適用済み（Undoで巻き戻せる）
  readonly future: readonly Command[]; // Undoされた分（Redoで進められる）
}
```

現在のドキュメントは`History`に保持せず、参照のたびに`past.reduce((doc, cmd) => cmd.apply(doc), initial)`で再生して求める。新しいコマンドが確定すると`future`は破棄する（一般的な線形履歴、外部仕様6.6.1の設計方針を踏襲）。`past`・`future`の操作に長さ0の特別扱いを入れない実装にすることで、外部仕様6.6.1の2件の不具合を構造的に再発させない。

> [!note] トレードオフ
> 参照のたびに`past`全体を先頭から再生するため、コスト は履歴の長さに比例する（O(履歴長)）。単一セッション内で編集されるドキュメントの規模・履歴長では実用上問題にならないと判断したが、非常に長時間の編集セッションで体感遅延が出た場合は、Nコマンドごとにスナップショットを取るなどの中間キャッシュを追加する余地を残す。

### 5.3 現行版2件の不具合の解消方針

| 不具合（外部仕様6.6.1） | 解消方針 |
|---|---|
| `@change_no > 1`のオフバイワンで初回コミットのUndoが効かない | 「1回目のコミットでUndoが効く」ことを回帰テストで直接固定する（`tests/commands.history.test.ts`）。`past.length > 0`のみをUndo可能の条件とし、追加の下限を設けない |
| Redoがコード上完成しているにもかかわらず恒久的に無効化 | UI側でRedoボタン・ショートカット（Ctrl+Shift+Z / Ctrl+Y）を無条件に有効とし、`future.length === 0`のときのみ非活性にする。Undoと非対称な特別扱いを入れない |

### 5.4 コミット粒度

外部仕様が定める「1操作＝1アンドゥ単位」をコマンド粒度でそのまま表現する。

| 操作 | コミット単位 | 根拠 |
|---|---|---|
| ドラッグ移動 | ドラッグ完了（mouseup）時に1コマンド | 6.2.2 |
| 一括削除（複数選択） | 全体で1コマンド | 6.3.2 |
| 属性値の確定 | 確定イベントごとに1コマンド | 6.5.2 |
| 矢印キー移動 | 1キー入力＝1コマンド（1グリッド分） | 6.2.2 |

ドラッグ中の暫定表示（グリッド未満の移動量の蓄積を含む）はコマンド未確定のプレビュー状態として描画層（6章）が保持し、モデル・履歴には反映しない。

### 5.5 コマンド一覧

| コマンド | 対応する外部仕様 | 備考 |
|---|---|---|
| `AddCellCommand` | 6.1.2 | セルタイプ未選択時は生成しない（9章で促す） |
| `MoveCellCommand` / `MovePortCommand` | 6.2.2 | ポートは所属辺内オフセットのみ変更 |
| `ChangePortEdgeCommand` | 4.3.2 | 辺をまたぐ変更を明示的な操作として分離 |
| `DeleteCommand` | 6.3.2 | カスケード削除。結合バー・呼び口・受け口いずれの選択からも呼べる |
| `CreateJoinCommand` / `DeleteJoinCommand` | 6.4.2 | シグニチャ一致判定はコマンド生成前のガードで行う |
| `MoveJoinBarCommand` | 6.2.2 | ドラッグしたバー自身を直接動かし、隣接バーは直交を保つよう自動調整（現行版の「隣のバーが動く」間接性を廃止） |
| `EditAttrCommand` / `RenameCellCommand` / `ChangeRegionCommand` | 6.5.2 | リージョン変更は新設（現行版はスタブのみ） |
| `CopyCommand`（履歴を作らない） / `PasteCommand` / `CutCommand` | 6.7.2 | Cutは内部でPasteの逆＋Delete相当を1コマンドに合成 |
| `AlignTopCommand` / `AlignLeftCommand` | 7.3.2 | 複数選択の整列。基準は選択順で最初のセル |

## Related

- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 06A 編集操作（前半）|TECSCDE外部仕様 6. 編集操作（前半）]]
- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 06B 編集操作（後半）|TECSCDE外部仕様 6. 編集操作（後半、Undo/Redo規定）]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様|TECSCDE内部仕様（目次）]]
- [[work/active/tecs/TECSCDE Undo-Redo設計決定|Decision Record: TECSCDE Undo/RedoをreplayベースのHistoryで実装する]]

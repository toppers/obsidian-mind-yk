---
date: 2026-08-30
description: "TECSCDE JS版のUndo/Redoを、当初文書化したCommand{apply, invert()}方式ではなくreplayベースのHistoryで実装した決定 — 現行版6.6.1の2バグを構造的に再発させない狙い、O(履歴長)のトレードオフ"
status: accepted
project: TECS
quarter: Q3-2026
tags:
  - decision
  - tecs
  - tecscde
---

# Decision: TECSCDE Undo/RedoをreplayベースのHistoryで実装する（invert()方式を採用しない）

## Context

[[TECSCDE内部仕様]]第5章（編集コマンドとUndo/Redo設計）は当初、各コマンドが`apply(doc)`に加えて`invert(before, after)`を持ち、逆操作コマンドを生成してUndoを実現する設計（コマンドパターンの標準形）を規定していた（5.1・5.2の初稿）。

この設計は[[TECSCDE外部仕様]]6.6.1が定める要件——現行版（Ruby/GTK版 V0.5.1）に存在する2件の既知バグ（`@change_no > 1`のオフバイワンで初回コミットのUndoが効かない、Redoがコード上完成しているにもかかわらず恒久的に無効化されている）を構造的に再発させないUndo/Redo機構——を満たすために書かれたものだった。

2026-08-30、`E:\Ccur\typescript\TECSCDE`でのTypeScript実装着手時に、この`invert()`方式を実装する過程で「`past`に積んだコマンド列を初期ドキュメントへ先頭から再生（replay）するだけで現在のドキュメントを再構成でき、`invert()`自体が不要」と判明した。

## Options Considered

1. **Command{apply, invert(before, after)}**（当初文書化した方式・不採用）
   - 各コマンドが順操作`apply`と逆操作`invert`の両方を実装する。
   - `History`は「適用済みコマンド列」と「逆操作コマンド列」の対で構成し、Undoは逆操作コマンドをドキュメントに適用、Redoは元のコマンドを再適用する。
   - 標準的なコマンドパターンで、多くの実装例がある。

2. **replayベースの`History`**（採用）
   ```ts
   interface History {
     readonly initial: TecscdeDocument;
     readonly past: readonly Command[];
     readonly future: readonly Command[];
   }
   ```
   - `Command`は`apply`のみを持ち、`invert`を持たない。
   - 現在のドキュメントは保持せず、参照のたびに`past.reduce((doc, cmd) => cmd.apply(doc), initial)`で再生して求める。
   - Undoは`past`の末尾を`future`へ、Redoは`future`の末尾を`past`へ移すだけの配列操作。

## Decision

**Option 2（replayベースのHistory）を採用した。**

理由: `invert()`方式は、逆操作の実装ミスがそのまま「逆方向にだけ壊れる」バグを生む発生源になる——これはまさに現行版6.6.1の2バグ（初回Undo不可・Redo恒久無効）が実際に起きたのと同じ種類の非対称な特別扱いのバグである。5.3が定める「解消方針」の目的は「この種のバグを構造的に再発させない」ことだったが、`invert()`を書かずに済むreplay方式を採れば、逆操作の実装ミスという発生源自体が存在しなくなり、より単純な手段で同じ目的を達成できると判断した。

実装上も、現在のドキュメントは常に不変なコマンド列を`initial`へ畳み込んだ結果として一意に定まるため、「順操作と逆操作のペアが同期を保っているか」という不変条件を維持する必要がなくなる。Undo/Redoは`past`/`future`という2つの配列間で要素を1つ移動するだけの操作になり、`past.length > 0`・`future.length === 0`という条件だけで判定でき、5.3の2バグの温床だった「長さ0付近の特別扱い」を回避しやすい形になった。

## Consequences

- **6.6.1の2バグの回帰テスト化**: `tests/commands.history.test.ts`で「1回目のコミットでUndoが効く」ことを直接固定。Redoは`future.length === 0`のときのみ非活性とし、Undoと非対称な特別扱いを入れない実装にした。
- **コマンドごとの`invert()`実装・検証が不要になった**: 5.5に列挙する9種のコマンド（`AddCellCommand`・`MoveCellCommand`等）それぞれについて逆操作を書いて検証する作業がまるごと消えた。
- **トレードオフ（コスト）**: 現在のドキュメントを求めるたびに`past`全体を先頭から再生するため、コストは履歴の長さに比例する（O(履歴長)）。単一セッション内の編集規模では実用上問題にならないと判断したが、非常に長時間の編集セッションで体感遅延が出た場合は、Nコマンドごとにスナップショットを取る中間キャッシュを追加する余地を残した（`past`/`future`の配列モデル自体は変更不要）。
- **当初のinvert()設計は本記録以外に残らない**: [[TECSCDE内部仕様]]第5章はreplay方式で書き直され（2026-08-30、コミット`800d601`）、invert()方式は本Decision Recordとgit履歴にのみ残る。コードとコミット後の仕様書だけを読む将来の読み手が「なぜinvert()を使っていないのか」と疑問に思った場合、この記録が唯一の説明になる。
- 2026-08-30、`E:\Ccur\typescript\TECSCDE`での実装・ブラウザ動作確認により、replay方式でセル移動→Undo→Redoの一連の動作が正しく機能することを確認済み（[[TECSCDE-JS-TS実装]]）。

## Related

- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 05 編集コマンドとUndo-Redo設計|TECSCDE内部仕様 第5章（編集コマンドとUndo/Redo設計）]] — 本決定を反映済みの現行仕様
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-TS内部仕様 第4章（クラスベース代替設計）]] — 本決定を踏襲するクラスベース設計
- [[TECSCDE-JS-TS実装]] — 本決定に基づく実装・動作確認の記録
- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 06B 編集操作（後半）|TECSCDE外部仕様 6.6.1]] — 解消対象の現行版2バグの規定
- [[TECSCDE内部仕様]] — 内部仕様書（目次）
- [[North Star]] — 🔴最優先事項としてのTECSCDE JS版実装

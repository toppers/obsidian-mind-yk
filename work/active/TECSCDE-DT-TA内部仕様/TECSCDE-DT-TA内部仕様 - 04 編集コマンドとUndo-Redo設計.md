---
date: 2026-09-05
description: "TECSCDE-DT-TA内部仕様書 第4章（編集コマンドとUndo-Redo設計）— Commandトレイト（トレイトオブジェクトとしてHistoryが保持）、History構造体、Copy/Paste/CutのOSクリップボード連携（invoke経由）。"
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

Domain note split from [[TECSCDE-DT-TA内部仕様]] (2026-09-05). Chapter 4 of 11。

## 4. 編集コマンドとUndo-Redo設計

### 4.1 `Command`トレイト

```rust
pub trait Command {
    fn apply(&self, doc: TecscdeDocument) -> TecscdeDocument;
    // invert() は持たない — work/active/tecs/TECSCDE Undo-Redo設計決定のとおり、
    // 逆操作の実装ミスに由来する非対称バグの発生源を、トレイトのレベルでも作らない
}
```

TypeScript版（[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-TS内部仕様第4章]]）の`abstract class Command`をトレイトに置き換える。`History`が異なる種類のコマンドを同じ配列（`Vec`）に格納する必要があるため、**トレイトオブジェクト**（`Box<dyn Command>`）として保持する——Rustの静的ディスパッチではこの種の異種コレクションを表現できないため、動的ディスパッチが必要になる数少ない箇所の1つである。

### 4.2 `History`構造体

```rust
pub struct History {
    initial: TecscdeDocument,
    pub past: Vec<Box<dyn Command>>,
    pub future: Vec<Box<dyn Command>>,
}

impl History {
    pub fn begin(initial: TecscdeDocument) -> History {
        History { initial, past: Vec::new(), future: Vec::new() }
    }

    /// 現在のドキュメント。pastをinitialへ再生して求める（O(履歴長)、TECSCDE-TS内部仕様4.3節と同じトレードオフ）
    pub fn current(&self) -> TecscdeDocument {
        self.past.iter().fold(self.initial.clone(), |doc, cmd| cmd.apply(doc))
    }

    pub fn can_undo(&self) -> bool { !self.past.is_empty() }
    pub fn can_redo(&self) -> bool { !self.future.is_empty() }

    pub fn commit(mut self, command: Box<dyn Command>) -> History {
        self.past.push(command);
        self.future.clear(); // futureは破棄する
        self
    }

    pub fn undo(mut self) -> History {
        if let Some(last) = self.past.pop() { self.future.insert(0, last); }
        self
    }

    pub fn redo(mut self) -> History {
        if !self.future.is_empty() { self.past.push(self.future.remove(0)); }
        self
    }
}
```

[[TECSCDE-TS内部仕様]]第4章と同じく、`current`（replay計算）・`undo`/`redo`（配列操作）を`History`の外に漏らさない。`self`を消費する（`mut self`を取り新しい`History`を返す）メソッドチェーンは、TypeScript版の「新しいインスタンスを返す」設計をRustの所有権規則がそのまま強制する例である——`history.commit(cmd)`の戻り値を使わずに元の`history`変数を再利用しようとするとコンパイルエラーになる。

`current()`が`self.initial.clone()`を呼ぶ点は、第3章3.2節で述べた`im::HashMap`（採用する場合）の構造共有により、素朴な`std::collections::HashMap`の`clone()`より低コストになる。

### 4.3 コマンド一覧

コマンド一覧・各コマンドの対応する外部仕様は[[TECSCDE-TS内部仕様]]4.5節の表と**同一**。実装例（`MoveCellCommand`）:

```rust
pub struct MoveCellCommand { cell_id: CellId, to_x: f64, to_y: f64 }

impl Command for MoveCellCommand {
    fn apply(&self, doc: TecscdeDocument) -> TecscdeDocument {
        let cell = doc.get_cell(&self.cell_id).expect("cell not found").clone();
        doc.with_cell(cell.move_to(self.to_x, self.to_y))
    }
}
```

### 4.4 `CopyCommand`/`PasteCommand`/`CutCommand` — OSクリップボード連携

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 06B 編集操作（後半）|TECSCDE-DT外部仕様6.7節]]が採用したOSクリップボード連携を、第2章の`ClipboardGateway`（`invoke`経由）を通じて実現する。**Electron版（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-DT-EL内部仕様第4章]]）と異なり、Tauri版はクリップボードもbackend経由の`invoke`を使う**（第2章2.3節）。

```rust
pub struct CopyCommand { cell_ids: Vec<CellId> }

impl CopyCommand {
    // Commandトレイトのapplyは同期的な設計だが、クリップボード書き込みは非同期（invoke）のため、
    // 本コマンドはHistoryへcommitする前に非同期に実行し、結果を待ってから通常のCommandとして扱う
    pub async fn execute(&self, doc: &TecscdeDocument, clipboard: &ClipboardGateway) -> Result<(), JsValue> {
        let fragment = serialize_cells_as_cdl(doc, &self.cell_ids); // TECSCDE-DT外部仕様6.7節のCDL断片構文
        clipboard.write_text(&fragment).await
    }
}
```

**設計上の留意点**: `Command::apply`は同期的（`fn`）だが、クリップボード操作は`invoke`を介するため非同期（`async fn`）になる。この非対称性はTypeScript版にも存在した（Electron版ではpreloadの`clipboard`モジュールが同期APIだったため問題にならなかったが、Tauri版は`invoke`が常に非同期であるため、より顕著に現れる）。本書は`CopyCommand`をUIシェル（モジュールG）からのみ呼ばれる特殊操作とし、`Command`トレイトの`apply`とは別の非同期メソッド（`execute`）として扱うことでこの非対称性を吸収する——`History`へのコミット自体は同期のままでよい（コピーはドキュメントを変更しない、[[TECSCDE-TS内部仕様]]4.5節の表と同じ位置付け）。

`PasteCommand`はアプリ内クリップボードを優先し、空の場合に`ClipboardGateway::read_text()`（非同期）でOSクリップボードのCDL断片を試みる方針も[[TECSCDE-DT-EL内部仕様]]第4章と同一。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-TS内部仕様 第4章（Command/Historyの一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-DT-EL内部仕様 第4章（Electron版のクリップボード連携、対比対象）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-TA内部仕様 第2章（ClipboardGatewayの設計根拠）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様（目次）]]

---

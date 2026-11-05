---
date: 2026-09-05
description: "TECSCDE-TS内部仕様書 第7章（ファイルI/O設計）— FileIOStrategyインタフェース+2実装クラス（Strategyパターン）、FileOpener/FileSaver、DirtyTracker。"
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

Domain note split from [[TECSCDE-TS内部仕様]] (2026-09-05). Chapter 7 of 11（[[TECSCDE内部仕様]]の第8章に対応）。

## 7. ファイルI/O設計

### 7.1 `FileOpener`クラス

```ts
class FileOpener {
  async openFromInput(files: FileList): Promise<OpenResult> { /* <input type="file" multiple> */ }
  async openFromDrop(event: DragEvent): Promise<OpenResult> { /* キャンバス領域へのdrop */ }

  private resolveEditableFile(files: readonly File[]): { editable: File; references: readonly File[] } {
    // 8.1.2: 最後に選択/ドロップされたファイルを編集対象、他は参照専用とする
    const editable = files[files.length - 1]!;
    return { editable, references: files.slice(0, -1) };
  }
}
```

参照専用ファイルから読み込まれたセルは`editable: false`として`Cell`（第3章）へ取り込む——`Cell.create()`のファクトリメソッドが`editable`フィールドをそのまま保持するだけであり、`FileOpener`側は`locale`（定義元ファイル）の判定のみを行う（10.2.1、第3章3.3節#5と対応）。

### 7.2 `FileIOStrategy`（Strategyパターン）

```ts
interface FileIOStrategy {
  save(content: string, suggestedName: string): Promise<void>;
  saveAs(content: string, suggestedName: string): Promise<void>;
}

class FileSystemAccessStrategy implements FileIOStrategy {
  private handle: FileSystemFileHandle | null = null;
  async save(content: string, suggestedName: string): Promise<void> {
    // 開いた際のハンドルへ書き戻す。書き込み完了前に既存内容を破棄しない（5.4.2）よう、
    // 一時バッファへ全体を書き終えてからハンドルへ書き込む。
  }
  async saveAs(content: string, suggestedName: string): Promise<void> {
    this.handle = await (window as any).showSaveFilePicker({ suggestedName });
    await this.save(content, suggestedName);
  }
}

class DownloadFallbackStrategy implements FileIOStrategy {
  async save(content: string, suggestedName: string): Promise<void> { /* 直近のダウンロードファイル名を使ったダウンロード */ }
  async saveAs(content: string, suggestedName: string): Promise<void> { /* ファイル名入力後にダウンロード */ }
}

class FileSaver {
  private readonly strategy: FileIOStrategy =
    ('showOpenFilePicker' in window && 'showSaveFilePicker' in window)
      ? new FileSystemAccessStrategy()
      : new DownloadFallbackStrategy();

  save(content: string, suggestedName: string): Promise<void> { return this.strategy.save(content, suggestedName); }
  saveAs(content: string, suggestedName: string): Promise<void> { return this.strategy.saveAs(content, suggestedName); }
}
```

[[TECSCDE内部仕様]]第8章は`canUseFSAccess`の分岐をトップレベル関数の条件分岐として持つ。本書はこれを`FileIOStrategy`インタフェースの2実装（Strategyパターン、第2章2.2節で予告済み）に分離し、`FileSaver`自身は「どちらの経路か」を知らずに`strategy.save()`を呼ぶだけにする——分岐ロジックが1箇所（コンストラクタ）に閉じ、呼び出し側（モジュールG）は`FileSaver`の公開APIしか見えない。

### 7.3 エクスポート

SVG（第一形式）・PNG（SVG経由のラスタライズ、出力倍率指定可）を`FileSaver`と同じ保存経路（`FileIOStrategy`）に載せる。「用紙に合わせる」「内容に合わせる」の出力範囲選択を提供する（外部仕様5.6.2）。PDFは対象外とし、印刷用スタイルシート（`@media print`）で代替する——[[TECSCDE内部仕様]]8.3節と同一の方針。

### 7.4 未保存確認（`DirtyTracker`）

```ts
class DirtyTracker {
  private constructor(private readonly savedAtHistoryLength: number) {}
  static clean(history: History): DirtyTracker { return new DirtyTracker(history.past.length); }

  isDirty(history: History): boolean { return history.past.length !== this.savedAtHistoryLength; }
  markSaved(history: History): DirtyTracker { return new DirtyTracker(history.past.length); }
}
```

保存操作完了時点の`History.past.length`（第4章）を基準に「未保存」を判定する。第4章の`Undo履歴とは独立に持つ`——現行版の`ChangeSet`を保存要否フラグに流用しない方針（外部仕様6.6.1、[[TECSCDE内部仕様]]8.4節）をクラスとして表現したものであり、`DirtyTracker`は`History`の内部（`current`の再生計算等）には一切関与しない、履歴の長さだけを参照する薄いラッパーである。

## Related

- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 05 ファイル操作|TECSCDE外部仕様 5. ファイル操作]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 08 ファイルI-O設計|TECSCDE内部仕様 第8章（対応する既存設計）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-TS内部仕様 第4章（DirtyTrackerが参照するHistory）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様（目次）]]

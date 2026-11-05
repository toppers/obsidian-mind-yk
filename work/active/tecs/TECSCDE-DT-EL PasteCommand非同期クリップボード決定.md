---
date: 2026-09-11
description: "PasteCommandはClipboardGatewayを直接持たず、OSクリップボードの読み取り済みテキストを渡される設計にする決定。Command.apply()が同期でありClipboardGateway.readText()がPromise<string>であることの不整合が契機。"
project: TECS
quarter: Q3-2026
status: accepted
tags:
  - decision
  - tecs
  - tecscde
---

# Decision: `PasteCommand`は`ClipboardGateway`ではなく解決済みのOSクリップボードテキストを受け取る

## Context

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計|内部仕様第4章4.1節]]のスケッチは、`PasteCommand`が`ClipboardGateway`を直接保持し、`apply()`内で`this.clipboard.readText()`を同期的に呼ぶ設計を示していた（執筆時点でのスケッチは`readText(): string`を想定）。

2026-09-11、実装（[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]の第4章4.1節着手）で、既に実装済みの`ClipboardGateway`（2026-09-07コミット）が`readText(): Promise<string>`であることが判明した。原因はElectron 44自体の`clipboard`モジュールが`navigator.clipboard`に倣って非同期化されたこと（`node_modules/electron/electron.d.ts`の`Clipboard.readText()`が`Promise<string>`を返す）。一方`Command.apply(doc): TecscdeDocument`（第4章4.2節）は同期シグネチャであり、`apply()`内でPromiseをawaitできない。

## Options Considered

1. **`Command.apply()`を非同期化する**（`Promise<TecscdeDocument>`を返す）
   - 利点: スケッチどおり`PasteCommand`が`ClipboardGateway`を直接持てる。
   - 欠点: 全コマンドクラス・`History.current`（`past.reduce((doc,cmd)=>cmd.apply(doc), initial)`）・既存117テストすべてに影響する。ほぼ全コマンドが同期で十分な処理であるにもかかわらず、Paste1件のためにモデル全体の型を非同期化することになり、影響範囲に見合わない。
2. **`PasteCommand`は解決済みの`osClipboardText: string | undefined`を受け取る**（採用）
   - 利点: `Command`階層は同期のまま。OSクリップボードの読み取り（非同期I/O）は、コマンド構築前に呼び出し側（将来のモジュールG／`AppStore`）が`await clipboard.readText()`してから`new PasteCommand(appClipboard, text)`する形になる——他の全コマンドが「実行に必要な値をコンストラクタで受け取る」設計と一貫する。
   - 欠点: 内部仕様4.1節のスケッチが示す`PasteCommand`のコンストラクタ引数（`ClipboardGateway`）と実装が一致しない。

`CopyCommand`/`CutCommand`は`writeText()`の完了を待つ必要がない（結果を使わない発火のみの操作）ため、この非対称は生じない——`ClipboardGateway`をそのまま受け取り、`apply()`内で`void this.clipboard.writeText(...)`と呼ぶ（fire-and-forget）。

## Decision

**選択肢2**。`PasteCommand(appClipboard: readonly Cell[], osClipboardText: string | undefined)`とし、OSクリップボードの読み取り自体は`PasteCommand`の外（呼び出し側）の責務とする。

## Consequences

- `Command`階層・`History`は全コマンドを通じて同期のまま維持される。
- `PasteCommand`のテストは`ClipboardGateway`のモックを必要とせず、文字列を直接渡すだけで書ける（[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|実装]]の`tests/renderer/clipboard-commands.test.ts`参照）。
- ~~未解決のまま残る: 「呼び出し側が`readText()`を先に解決してから`PasteCommand`を構築する」という呼び出し規約自体は、まだどこにも実装されていない（モジュールG次段、`AppStore`の仕事）。実装時にこの規約を破らないよう注意が必要。~~ → **2026-09-11中に解消**: `AppStore.pasteClipboard(osClipboardText)`と`app/clipboard-actions.ts`の`pasteFromClipboard(store, clipboard)`（`readText()`を先に`await`してから`store.pasteClipboard()`を呼ぶ）として実装済み（モジュールGキーボードショートカット配線コミット）。
- 姉妹実装（[[work/active/TECSCDE-TS実装/TECSCDE-TS実装|TECSCDE-TS実装]]・[[work/active/TECSCDE-DT-TA実装/TECSCDE-DT-TA実装|TECSCDE-DT-TA実装]]）がOSクリップボード連携を実装する際、同じ非同期API（ブラウザの`navigator.clipboard`、TauriのclipboardプラグインもPromiseベース）に直面するため、この決定（読み取りをコマンド外に出す）はそのまま踏襲できる可能性が高い。

## Related

- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]] — この決定の契機となった第4章4.1節実装（コミット`0e79b3e`）
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-DT-EL内部仕様 第4章]] — 4.1節（本決定が変更したスケッチの一次情報源）
- [[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定|TECSCDE-DT-EL preload ESM・sandbox決定]] — 同じく実機実装で判明したElectron固有の制約から生まれた決定
- [[work/active/tecs/TECSCDE Undo-Redo設計決定|TECSCDE Undo-Redo設計決定]] — `Command`/`History`が同期である前提の一次情報源
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体

---
date: 2026-08-30
description: "TECSCDE内部仕様書 第11章（モジュール間インタフェース一覧）— 2章の依存図を具体的な契約まで落とした参照補遺"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note split from [[TECSCDE内部仕様]] (2026-08-30, 25KB threshold). Chapter 11 of 12.

## 11. モジュール間インタフェース一覧

2章の依存図を、実際のディレクトリ構成とTypeScriptの型契約まで落とし込む。

```
src/
  model/            (C) types.ts, document.ts, invariants.ts
  cdl/              (B) grammar.ts, document-builder.ts, tool-info.ts, serializer.ts, messages.ts, cdecl.ts
  commands/         (D) command.ts, history.ts, ops/*.ts
  render/           (E) svg-renderer.ts, hit-test.ts, gesture.ts
  view-state/       (F) viewport.ts, filters.ts, search.ts
  ui-shell/         (G) toolbar.ts, palette.ts, property-panel.ts, status-bar.ts, dialogs/
  diagnostics/      (H) collector.ts
  tecsgen-link/     (I) command-builder.ts
  io/               (A) file-open.ts, file-save.ts
  app/
    store.ts          C・F・Hを束ねる中央pub/subストア
    main.ts           起動・依存注入・イベント配線
```

### 11.1 依存の機械的強制

2章の依存図（`A→B→C←D←G`、`F`と`I`の独立性、`H`の読み取り専用性）を`dependency-cruiser`のルールとしてそのまま定義し、CIで`depcruise --validate`を実行する。レビュー担当者の見落としに依存せず、境界違反（例: `render/`が`commands/`を経由せず`model/`へ直接書き込む`import`）をビルドの失敗として検出する。

### 11.2 モジュール間の主要インタフェース

| 提供モジュール | インタフェース | 利用モジュール |
|---|---|---|
| C | `TecscdeDocument`（読み取り専用型） | 全モジュール |
| D | `Command` / `History` / `store.dispatch(cmd)` | G, E（gesture経由） |
| B | `initCdlParser(): Promise<void>`（起動時に1度） / `parse(text): {doc, diagnostics}` / `serialize(doc): string` | A（保存時）, app（初期化は`app/main.ts`が待つ、4.3） |
| F | `ViewState`（読み取り専用型）、`store.viewState` | E, G |
| H | `DiagnosticReport` | G（9.3の一覧表示） |
| I | `buildTecsgenCommand(doc, refs): string` | G（ダイアログ表示のみ） |

### 11.3 開発ツール方針

- ランタイムの`dependencies`は**`web-tree-sitter`と文法パッケージ2種のみ**（2026-09-13改訂）。外部仕様2.2はCDL解析系だけを唯一の外部依存として認めており、これ以外のランタイム依存は引き続き持たない。`devDependencies`は従来どおり（typescript, vite/esbuild、vitest、eslint、dependency-cruiser）。
- **`.wasm`は`public/`配下から素の静的アセットとして配る**（2026-09-13決着）。従来の「出力は単一HTML＋単一JSバンドル」はJS/CSSについての方針であり、`public/samples/*.cdl`という先例が既にある。`data:`URI埋め込みで単一ファイルを維持する案は、base64化で約1.4倍に膨らむ割に得るものが無いため採らなかった。[[TECSCDE-JS-TS実装]]の実測ではwasm 3個（計約409KB）、JSバンドルは408.70 kB（gzip 148.20 kB）、ロード完了はnavigation startから約120ms。
- `tsconfig`は`strict`＋`noUncheckedIndexedAccess`を有効化。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 10 モジュール間インタフェース一覧|TECSCDE-TS内部仕様 第10章（クラスベース代替設計）]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 02 モジュール構成と責務境界|2. モジュール構成と責務境界]] — 本章はこの依存図の具体化
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様|TECSCDE内部仕様（目次）]]

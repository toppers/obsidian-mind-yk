---
date: 2026-09-05
description: "TECSCDE-TS内部仕様書 第10章（モジュール間インタフェース一覧）— クラス構成に基づくディレクトリ構成と、依存の機械的強制方針。"
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

Domain note split from [[TECSCDE-TS内部仕様]] (2026-09-05). Chapter 10 of 11（[[TECSCDE内部仕様]]の第11章に対応）。

## 10. モジュール間インタフェース一覧

第2章の依存図（[[TECSCDE内部仕様]]2.2節と同一、モジュールA〜Iの依存方向）を、本書のクラス構成に基づき実際のディレクトリ構成まで落とし込む。

```
src/
  model/            (C) types.ts (Port, CPort, EPort, Cell, Join, Region, RegionTree),
                          document.ts (TecscdeDocument), invariants.ts (InvariantViolation)
  cdl/              (B) CdlGrammar, CdlDocumentBuilder, CdlSerializer, ToolInfoValidator, CdeclExtractor
  commands/         (D) Command（抽象基底）, History, ops/*.ts（具象コマンドクラス群）
  render/           (E) SvgRenderer, CellRenderer, JoinRenderer, HitTester, GestureController
  view-state/       (F) ViewState, DisplayFilters
  ui-shell/         (G) UiComponent（抽象基底）, Toolbar, PropertyPanel, StatusBar, Palette, dialogs/
  diagnostics/      (H) Diagnostic, DiagnosticsCollector, DiagnosticReport
  tecsgen-link/     (I) TecsgenCommandBuilder
  io/               (A) FileIOStrategy, FileSystemAccessStrategy, DownloadFallbackStrategy, FileOpener, FileSaver, DirtyTracker
  app/
    store.ts          Store（C・F・Hを束ねる中央pub/subストア、現行実装で既にクラス）
    main.ts           起動・依存注入・イベント配線
```

[[TECSCDE内部仕様]]11章のディレクトリ構成と比較すると、ファイル単位の分割はほぼ同一で、**各ファイルがエクスポートする単位が関数群からクラス（またはクラス群）に変わる**点のみが差分である。ディレクトリ＝モジュール境界という対応自体は変わらない。

> [!info] モジュールBの構成は2026-09-13に変わった
> [[TECSCDE内部仕様]]第4章の改訂（構文解析をtree-sitter文法へ委ねる）に追随し、`CdlLexer`・`CdlParser`を廃した。字句解析・構文解析は文法パッケージの責務になり、本モジュールに残るのは**CSTの走査・検証・生成**である。`CdlGrammar`だけが非同期初期化を持ち、`CdlDocumentBuilder.build()`以降は同期で完結する。用いる文法は2.4節のとおり`tools-ts/`版（TypeScriptで記述された`grammar.ts`）。

### 10.1 依存の機械的強制

[[TECSCDE内部仕様]]11.1節と同一の方針を踏襲する。第2章の依存図（`A→B→C←D←G`、`F`と`I`の独立性、`H`の読み取り専用性）をdependency-cruiserのルールとして定義し、CIで`depcruise --validate`を実行する。クラスベースであっても境界違反（例:`render/`が`commands/`を経由せず`model/`へ直接書き込む`import`）はimport文の静的解析で検出できるため、この方針はクラスか関数かに関わらず同じ効果を持つ。

### 10.2 モジュール間の主要インタフェース

| 提供モジュール | インタフェース（クラス） | 利用モジュール |
|---|---|---|
| C | `TecscdeDocument`（`getCell`/`getJoin`等の読み取り専用メソッドのみ公開） | 全モジュール |
| D | `Command`（抽象基底）／`History`（`current`/`commit`/`undo`/`redo`）／`store.dispatch(command)` | G, E（`GestureController`経由） |
| B | `CdlGrammar.init(): Promise<void>`（起動時に1度）／`CdlDocumentBuilder.build(text): {doc, diagnostics}`（初期化後は同期）／`CdlSerializer.serialize(doc): string` | A（保存時）, app（初期化は`main.ts`が待つ） |
| F | `ViewState`（読み取り専用）、`store.viewState` | E, G |
| H | `DiagnosticsCollector.toReport(): DiagnosticReport` | G（第8章8.4節の一覧表示） |
| I | `TecsgenCommandBuilder.build(doc, refs): string` | G（ダイアログ表示のみ） |

C（`TecscdeDocument`）が内部の`Map`をprivateフィールドとして隠蔽し、問い合わせメソッドのみを公開する設計（第3章3.2節）は、既存内部仕様の`ReadonlyMap`直接公開よりも狭いAPI surfaceを利用モジュールに提示する——「全モジュールがCに依存する」という2.2節の事実は変わらないが、依存できる操作の集合はクラス化によってより厳密に絞られる。

### 10.3 開発ツール方針

[[TECSCDE内部仕様]]11.3節と同一。

- ランタイムの`dependencies`は**`web-tree-sitter`のみ**（2026-09-13改訂）。[[TECSCDE外部仕様]]2.2節がCDL解析系だけを唯一の外部依存として認めており、これ以外のランタイム依存は持たない。`devDependencies`は従来どおり（typescript, vite/esbuild、vitest、eslint、dependency-cruiser）
- `.wasm`は`public/`配下から素の静的アセットとして配る（[[TECSCDE内部仕様]]11.3節と同一の決着）。`data:`URI埋め込みは採らない
- **`tools-ts/`版を使う場合、`.wasm`と生成パーサはビルド成果物である。** `tools/`版が`.wasm`を成果物として同梱するのに対し、`tools-ts/`の`.gitignore`は`grammar.js`・`src/`・`*.wasm`を生成物として扱う。したがって取り込みには`npm run generate`（`tsc -p tsconfig.grammar.json` → `tree-sitter generate`）と`npm run build:wasm`の実行が要る——後者は`tree-sitter` CLIとemscripten（またはDocker）を要求する。11.2節#3
- 出力は単一HTML＋単一JSバンドル
- `tsconfig`は`strict`＋`noUncheckedIndexedAccess`を有効化。クラスのprivateフィールドを型レベルで強制するため、`useDefineForClassFields`も有効化を推奨する（本書独自の追加提案）

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 02 モジュール構成と責務境界|TECSCDE-TS内部仕様 第2章（本章はこの依存図の具体化）]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 11 モジュール間インタフェース一覧|TECSCDE内部仕様 第11章（対応する既存設計）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様（目次）]]

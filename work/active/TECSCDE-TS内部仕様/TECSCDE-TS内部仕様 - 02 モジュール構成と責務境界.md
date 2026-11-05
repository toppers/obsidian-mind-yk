---
date: 2026-09-05
description: "TECSCDE-TS内部仕様書 第2章（モジュール構成と責務境界）— 既存内部仕様と同一の9モジュール分割・依存方向に、代表クラス群を対応づける。"
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

Domain note split from [[TECSCDE-TS内部仕様]] (2026-09-05). Chapter 2 of 12.

## 2. モジュール構成と責務境界

### 2.1 モジュール一覧と依存方向は既存内部仕様と同一

外部仕様が課す責務境界は実装方式（関数ベースかクラスベースか）に依存しない。したがって9モジュール（A〜I）の分割・責務・対応する外部仕様章・依存方向は[[TECSCDE内部仕様]]第2章（2.1節の一覧表、2.2節の依存方向図）と**同一であり、本書では再掲しない**。差分は各モジュールの内部表現（クラス設計）にのみ存在する。

### 2.2 モジュール別・代表クラス

| # | モジュール | 代表クラス（本書の提案） | [[TECSCDE内部仕様]]との違い |
|---|---|---|---|
| A | ファイルI/O | `FileIOStrategy`（インタフェース）、`FileSystemAccessStrategy`・`DownloadFallbackStrategy`（実装クラス、Strategyパターン） | 既存は`showOpenFilePicker`の有無で分岐する関数（`file-open.ts`/`file-save.ts`）。本書は分岐先を別クラスに分離し、呼び出し側は`FileIOStrategy`型のみに依存する |
| B | CDLパーサ／シリアライザ | `CdlGrammar`（WASM文法のロードと`Parser`保持）・`CdlDocumentBuilder`（CST→モデル）・`CdlSerializer`・`ToolInfoValidator`・`CdeclExtractor`（`import_C`のC型抽出） | **2026-09-13改訂**: 構文解析自体をtree-sitter文法へ委ねる方針（[[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 04 CDLパーサ／シリアライザ設計\|TECSCDE内部仕様第4章]]）に追随し、`CdlLexer`・`CdlParser`を廃止した。残るクラスはCSTの走査・検証・生成であり、クラス化の利点（各段階の独立した差し替え）はむしろ明確になる。`CdlGrammar`のみ非同期初期化（`init(): Promise<void>`）を持つ。**本書が用いる文法は`tools-ts/`版**（2.4節） |
| C | モデル | `Cell`・`Port`（抽象基底）・`CPort extends Port`・`EPort extends Port`・`Join`・`Region`・`RegionTree`・`TecscdeDocument` | 既存は`readonly`フィールドのみの plain interface。本書は3章で詳述するとおり、不変条件の一部を型階層自体で表現する |
| D | 編集コマンド／Undo-Redo | `Command`（抽象基底、`apply`のみ）、具象コマンドクラス群（`AddCellCommand`・`MoveCellCommand`・`DeleteCascadeCommand`・`CreateJoinCommand`・`EditAttrCommand`・`MoveJoinBarCommand`・`ChangePortEdgeCommand`等）、`History` | 既存は当初`interface Command { apply, invert }`だったが、実装時にreplayベースの`History`へ簡素化（[[work/active/tecs/TECSCDE Undo-Redo設計決定\|Decision Record]]）。本書はこの決定を踏襲し、`Command`基底クラスに`invert()`を持たせない |
| E | 描画（SVGレンダリング） | `SvgRenderer`（既存実装で既にクラス）、`CellRenderer`・`JoinRenderer`（要素種別ごとの下位クラス、共通の`ElementRenderer`抽象基底）、`GestureController`（既存実装で既にクラス） | 既存実装のクラス設計を正式な内部仕様として採用・拡張する。要素種別ごとの描画ロジックを`SvgRenderer`内の条件分岐から下位クラスへ切り出す |
| F | 表示制御（View State） | `ViewState` | 既存は`viewState.ts`のプレーンオブジェクト＋関数。本書はズーム/パン/フィルタ/検索状態を1つのクラスにカプセル化する |
| G | UIシェル | `UiComponent`（共通抽象基底、`mount`/`update`/`destroy`ライフサイクル）、`Toolbar`・`PropertyPanel`・`StatusBar`・`Palette`（`UiComponent`のサブクラス） | 既存はDOM操作を直接行う関数群。本書は各パネルを共通ライフサイクルを持つクラスとして統一し、D・Fへのディスパッチ経路を`UiComponent`のコンストラクタ引数として明示する |
| H | 整合性チェック／診断 | `DiagnosticsCollector` | 既存実装で既にクラス。本書でも同一の設計を採用する |
| I | tecsgen連携 | `TecsgenCommandBuilder`（静的メソッドのみ、状態を持たない） | 既存は関数（`commandBuilder.ts`）。本書はクラスにまとめるが、副作用なし・非実行という制約（8.4.2）上、実質的にnamespaceと同等であり大きな設計差はない |

### 2.3 本章で確定しないこと

- E・G・Hは現行実装（[[TECSCDE-JS-TS実装]]）が既にクラスベースであり、本書と現行実装のギャップは主にC・Dに集中する。E・G・Hのクラス設計は現行実装の追認に近く、本書の新規提案としての比重は低い。
- 依存方向の機械的強制（dependency-cruiser等によるCI検証）は[[work/active/tecs/TECSCDE-実装アーキテクチャ案|TECSCDE-実装アーキテクチャ案]]が既に提案しており、本書でも同じ方針を踏襲する想定（詳細は本書第11章[未着手]で扱う）。

### 2.4 用いるCDL文法パッケージ — `tools-ts/`版を正典とする（2026-09-13）

[[TECSCDE外部仕様]]2.2節が唯一の外部依存として認めるCDL解析系には、同じ文法の版が2つ存在する。

| 版 | 文法の記述 | 生成パーサ・`.wasm` の扱い |
|---|---|---|
| `tools/` | `grammar.js`（プレーンJS） | 成果物として同梱（`.wasm` がそのまま置かれている） |
| **`tools-ts/`（本書が採る）** | `grammar.ts`（`tree-sitter-cli/dsl` の型定義を参照した型チェック付き）を `tsc` で `grammar.js` へ変換してから `tree-sitter generate` | **生成物扱い**。`.gitignore` が `grammar.js`・`src/`・`*.wasm` を除外する |

**`tools-ts/`を採る理由**: 本書はモデルからUIまでをTypeScriptのクラスと型で表現する設計であり（第1章1.3節）、その一貫性を文法の記述にまで伸ばす。`grammar.ts`は`seq`/`choice`/`prec`/`field`が型チェックを受けるため、文法の変更が型エラーとして現れる——`bnf.y.rb`の改訂に追随して文法を触るのは本ツールの保守で実際に起こる作業であり、そこに型の裏付けがあることを重視した。

**選ぶのはソースの正典であって実行時の成果物ではない。** 2026-09-13に両版の生成物を突き合わせたところ、`tree-sitter-cdl`・`tree-sitter-tecs-cdecl`とも**`src/parser.c`・`src/grammar.json`・`src/node-types.json`が完全に一致**した（`STATE_COUNT` 379、`SYMBOL_COUNT` 171、ノード型134件が両版で同一、`LANGUAGE_VERSION` 15）。`.wasm`のバイトサイズだけが僅かに異なるが、これはビルド時のメタデータの差であって文法の差ではない。したがって**実行時の挙動は`tools/`版と同一**であり、既に`tools/`版の`.wasm`を取り込んでいる実装（[[TECSCDE-JS-TS実装]]）がそれを`tools-ts/`版へ差し替え直す実務上の必要はない。

**代償**: `tools-ts/`は生成物を同梱しないため、取り込みには`npm run generate`（`tsc -p tsconfig.grammar.json` → `tree-sitter generate`）と`npm run build:wasm`が要る。後者は`tree-sitter` CLIとemscripten（またはDocker）を要求し、2026-09-13時点の開発環境には`emcc`が無い（Dockerはある）。この手順を踏めない場合に`tools/`版の`.wasm`で代替してよいかは11.2節#3で扱う。

## Related

- [[TECSCDE内部仕様]] — 本章のモジュール一覧・依存方向の一次情報源（2.1・2.2節）
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様（目次）]]

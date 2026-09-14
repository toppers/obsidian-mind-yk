---
date: 2026-08-29
description: "TECSCDE（JS版・フレームワーク非依存）TypeScript実装のアーキテクチャ案。9モジュール→src/配置、モデル型設計、Undo/Redoコマンド設計、CDLパーサ方針、テスト戦略、実装着手順を提案"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - architecture
---

# TECSCDE 実装アーキテクチャ案

> [!info] 位置づけ
> [[TECSCDE内部仕様]]（9モジュールの責務境界・依存方向を定義済み）を踏まえ、TypeScript実装の具体的なパッケージ構成・型設計・テスト戦略を提案したもの。2026-08-30、この案に沿って `E:\Ccur\typescript\TECSCDE` で実装に着手し、動作確認済み（詳細: [[TECSCDE内部仕様]]の文書状態）。

スペックを一式確認しました（0-MD-4ボールト側が2026-08-24更新で最新、0-MD-2側は8/21で古い）。外部仕様全11章＋既存の内部仕様（2章まで執筆済み・9モジュール構成を定義済み）を踏まえた上で、TypeScript実装のアーキテクチャ案を提案します。

前提（外部仕様が既に固定している制約）

- ランタイム依存ゼロ（2.2）：UIフレームワーク・描画ライブラリ・ビルドツールに依存しない。DOM/SVG標準APIのみ。
- サーバなし・ブラウザ単体（2.2/2.3）：CDL解析もCDL生成も、tecsgenの起動も全てブラウザ内で完結。tecsgenは直接起動できない。
- 描画はSVG（2.3, 3.2.2）：オフスクリーンバッファなし、要素属性の差分更新のみ、全体再描画禁止。
- 保存形式は .cde = CDLそのもの（5.1.1）：独自ネイティブ形式を持たない。__tool_info__ の未知情報は解釈せず往復保持。
- Undo/Redoは現行版の2バグ（初回Undo不可・Redo恒久無効）を構造的に解消する（6.6.2）。
- 既存のTECSCDE内部仕様が2章まで執筆済みで、9モジュール（A〜I）の責務境界と依存方向を既に定義しています。以下はこれをTypeScriptの具体的なパッケージ構成に落とし込む提案です。

1. パッケージ構成（9モジュール → src/ 配置）

src/
  model/            (C: モデル/ドメイン中核。他のどこにも依存しない)
    types.ts          Cell / CPort・EPort / Join / Region / Signature参照 / Celltype参照
    document.ts        TECSModel相当。不変条件を持つルート集約
    invariants.ts       呼び口=結合1本まで/受け口=複数可、ALIGN丸め、識別子構文など
  cdl/              (B: CDLパーサ/シリアライザ。DOM・SVGを知らない)
    lexer.ts / parser.ts   cell定義ブロックのみを対象とするサブセット文法
    tool-info.ts            __tool_info__ の要素単位スキーマ検証(5.5.2)
    serializer.ts            ①tecsgenブロック ②cellブロック ③tecscdeブロックの順で出力
    messages.ts              tecsgenのG-code/S-codeメッセージカタログをそのまま踏襲(9.1.2)
  commands/         (D: 編集コマンド/Undo-Redo。Cのみに依存)
    command.ts          Command interface（apply/invert）
    history.ts          線形履歴（past/future）
    ops/                AddCell, MoveCell, DeleteCascade, CreateJoin, EditAttr, ...
  render/           (E: SVG描画。独自の不変条件を持たない)
    svg-renderer.ts     モデル変更イベント→対象要素の属性更新のみ
    hit-test.ts         ポート→セル→結合バーの優先順位、結合バーは半径限定探索(6.2.2)
    gesture.ts          ドラッグの有限状態機械→コマンド発行（自前実装、外部ライブラリなし）
  view-state/       (F: 表示制御。C・Bから独立、.cdeに含めない)
    viewport.ts         ズーム/パン、中心固定ズーム
    filters.ts          リージョン/ネームスペースフィルタ
    search.ts           検索・巡回ハイライト
  ui-shell/         (G: 薄い層。D・Fへディスパッチ、C・Hから読むだけ)
    toolbar.ts / palette.ts / property-panel.ts / status-bar.ts / dialogs/
  diagnostics/      (H: B・Cへの読み取り専用オブザーバ)
    collector.ts        インポート時警告・整合性チェックを1件のレポートに集約
  tecsgen-link/     (I: 葉ノード。副作用なし・非実行)
    command-builder.ts  tecsgenコマンド文字列の組み立てとコピー
  io/               (A: バイト列/テキストの出入りのみ)
    file-open.ts        <input type=file> / drag&drop
    file-save.ts        File System Access API 分岐 + download フォールバック
  app/
    store.ts            C+F+Hを束ねる中央pub/subストア
    main.ts             起動・依存注入・イベント配線

依存方向の機械的強制：内部仕様2.2の依存図をレビュー任せにせず、dependency-cruiserかeslint-plugin-boundariesでルール化し、CIで検証します（例：model/は他のどのディレクトリからもimportされない一方、自身は何もimportしない、view-state/はmodel/とcdl/からのimportを禁止、など）。

2. モデル層（C）の型設計

CLAUDE.mdのイミュータブル方針に沿い、TecscdeDocumentは不変データとして持ちます。コミット粒度は仕様どおり「ドラッグ完了」「一括削除」など1操作＝1回（6.2.2/6.3.2）なので、mousemoveごとの不変更新コストは実用上問題になりません。

interface Cell {
  readonly id: CellId;
  readonly name: string;
  readonly celltypeRef: CelltypeRef;      // 4.2: セルタイプは参照のみ、編集対象外
  readonly x: number; readonly y: number;  // mm, ALIGN=1.0丸め済み
  readonly width: number; readonly height: number;
  readonly regionId: RegionId;
  readonly editable: boolean;              // 10.2.1: locale基準（拡張子では決まらない）
  readonly cports: readonly CPort[];
  readonly eports: readonly EPort[];
}

interface TecscdeDocument {
  readonly cells: ReadonlyMap<CellId, Cell>;
  readonly joins: ReadonlyMap<JoinId, Join>;
  readonly regions: RegionTree;            // 4.9: 木構造
  readonly toolInfoTecsgen: ToolInfoTecsgen; // 5.1.2: 解釈せず保持するだけ
  readonly paper: PaperSpec;
}

3. コマンド/Undo-Redo（D）— 現行版2バグの構造的解消

interface Command {
  apply(doc: TecscdeDocument): TecscdeDocument;
  invert(doc: TecscdeDocument): Command; // 適用前状態から逆操作を生成
}
interface History { past: Command[]; future: Command[]; }

線形履歴を素直な配列操作で実装すれば、「初回コミットからUndo可能」「Redoが常に正しい」は現行版のようなオフバイワンの余地がありません。ここは回帰防止のため、「1回目のコミットでUndoが効く」「Undo→Redoが元の状態と完全一致する」をプロパティベーステストで直接カバーすることを推奨します。

4. CDLパーサ（B）

**2026-09-13改訂**: 構文解析は tecsgen 自身の構文定義から移植した tree-sitter 文法（`tree-sitter-cdl`／`tree-sitter-tecs-cdecl`）に委ね、`web-tree-sitter`（WASM）で読み込みます。外部仕様2.2はCDL解析系のみを唯一の外部依存として認めており、自前のパーサを書く理由が無くなったためです（改訂前は「PEG.js等のランタイムは2.2の『依存ライブラリなし』に抵触するため手書きの再帰下降パーサを推奨」としていました）。全構文を解析し、モデルへ反映する範囲だけを限定します（cellブロック・__tool_info__・ポート構成に必要なcelltype/signature定義。import/import_Cは識別するが参照先を追跡しない）。設計の詳細は[[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 04 CDLパーサ／シリアライザ設計|TECSCDE内部仕様 第4章]]、決定の経緯は[[work/active/CDLParser(tree-sitter利用)/TECSCDE外部仕様 tree-sitter反映案|反映案]]。エラー文言は独自に言い換えず、tecsgenのメッセージカタログ（G-code/S-code）をそのまま踏襲（9.1.2）。

パーサのテストは「既存の.cdl/.cdeサンプルをfixtureにして、parse→serializeのround tripが意味的に一致すること」を軸にすると、5.1.2の「未知情報を解釈せず保持する」要件の回帰も同時に検証できます。

5. 描画層（E）とジェスチャー

モデルID→SVG要素のMapを持ち、変更イベント購読で該当要素の属性のみ更新（全体再描画禁止、3.2.2）。ドラッグは外部ステートマシンライブラリを使わず自前の小さな有限状態機械にし、遷移の終端でCommandを発行する形にすると、「E・GはDを介してのみモデルを変更する」という内部仕様2.2の保証がコードレベルでもそのまま見えます。

6. ファイルI/O（A）

const canUseFSAccess = 'showOpenFilePicker' in window;
で分岐し、利用可能ならファイルハンドル保持で上書き保存（5.4.2）、不可なら常にdownloadにフォールバック。複数ファイル選択時は「最後の1つが編集対象、他は参照専用」（8.1.2）をここで確定します。

7. ビルド・配布

- package.jsonのdependenciesは空。devDependenciesのみ（typescript, vite/esbuildはビルド時限定、vitest, eslint, dependency-cruiser）。ランタイム依存ゼロという仕様要件は「配布物」に対する制約であり、ビルドツール自体の使用とは矛盾しません。
- 出力は単一HTML＋単一JSバンドル（3.1.2の「単一ドキュメント構成」とも自然に整合）。
- tsconfigはstrict＋noUncheckedIndexedAccessを有効化。

8. テスト戦略

┌────────────────────────┬─────────────────────────────────────────────────┐
│           層           │                      手法                       │
├────────────────────────┼─────────────────────────────────────────────────┤
│ model / cdl / commands │ Vitest、純粋関数中心なので容易                  │
├────────────────────────┼─────────────────────────────────────────────────┤
│ cdl round-trip         │ 既存.cdl/.cdeサンプルをfixture化                │
├────────────────────────┼─────────────────────────────────────────────────┤
│ commands (Undo/Redo)   │ プロパティベーステスト（現行版2バグの回帰防止） │
├────────────────────────┼─────────────────────────────────────────────────┤
│ render / gesture       │ Playwright E2E                                  │
└────────────────────────┴─────────────────────────────────────────────────┘

9. 実装着手順の提案

内部仕様12章（未決事項と実装単位案）がまだ未執筆なので、ここに接続する形で、最初の実装単位はUIなしの model + cdl のround-trip（読み込み→保存で意味的に同一の.cdeが得られること）にスコープを絞るのが良いと考えます。UI層（E〜G）より先に、外部との唯一の契約点であるファイル形式を固めておくと、以降の層は全てこの上に積み上げられます。

## Related

- [[TECSCDE内部仕様]] — このアーキテクチャ案が前提とする9モジュールの責務境界・依存方向の定義元
- [[TECSCDE外部仕様]] — 制約（ランタイム依存ゼロ・サーバなし・SVG描画・.cde=CDL）の一次情報源
- [[work/active/tecs/TECS開発|TECS開発]] — 進捗テーブルに本ノートへのリンクあり
- [[perf/competencies/ソフトウェアアーキテクチャ|ソフトウェアアーキテクチャ]] — 9モジュールの`src/`配置と依存方向の機械的強制方針


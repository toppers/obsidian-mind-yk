---
date: 2026-09-23
description: "TECSCDE-DT-EL内部仕様書 第9章9.6節が名前を挙げるが未実装だった`CdeclExtractor`（モジュールB、typedef/struct抽出）の設計。tree-sitter-tecs-cdecl文法のCST走査アルゴリズムと型モデルを規定。2026-09-23同日中に実装完了（`src/renderer/cdecl/`、279テストpass）。実装時に判明した文法の実際の挙動（struct_declaratorのdeclaratorフィールドが無ラベル）を反映し更新。2026-10-21、9B.5のAPI（extract(text)）・結果型・型の写像を実装に合わせて更新。"
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

Domain note split from [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様 第9章]] (2026-09-23)。9.6節が名前を挙げる`CdeclExtractor`（モジュールB）自体の設計を、07B〜07Eの分離パターンに従い独立ファイルとして追加する。

> [!success] 実装完了（2026-09-23、同日中）
> `src/renderer/cdecl/{grammar,types,extractor}.ts`として実装し、[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章]]の`resolveImportClosure`へ統合済み（279テストpass、`npm run check` green）。設計からの実装時差分は9B.7節参照。

## 9B. `CdeclExtractor`設計（モジュールB、typedef/struct抽出）

### 9B.1 前提: 一次情報源の確認結果

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章]]が指摘したとおり、`CdeclExtractor`は2026-09-22時点でJS/TS/DT-ELのどのリポジトリにも実装が存在しない（`grep`で0件）。本節は次の一次資料を実際に読んで確認した事実に基づく（[[Patterns - 検証と調査]]の作法どおり、推測で設計しない）。

- **Ruby版 `tecslib/core/C_parser.y.rb`**（`E:\Crepo\toppers-tecs-svn\toppers\tecsgen\branches\ykominami_r3033\tecsgen\tecslib\core\C_parser.y.rb`）: 手書きの字句解析器（`next_token`）が、`typedef`/`struct`キーワードが文の境界（直前が`;`/`}`）で現れたときだけパーサへトークンを流す状態機械になっており、それ以外（関数定義・`extern`変数・`enum`/`union`単独・プリプロセッサ指令）は一切パーサに渡さない。`typedef`は`Typedef.new_decl_list`、`struct`は`CStructType.new_member`で型情報を蓄積する。
- **`tree-sitter-tecs-cdecl`文法**（`E:\Crepo\toppers-tecs-svn\toppers\tecsgen\branches\ykominami_r3033\tools\tree-sitter-tecs-cdecl`、姉妹パッケージ`tree-sitter-cdl`と同じ移植元リポジトリに同梱）: 上記のRuby字句解析器の実際の挙動（`typedef`/`struct`だけを抽出しそれ以外を読み飛ばす、`extern "C" { ... }`の波括弧内部でも認識する）を移植した専用文法。**汎用Cパーサではない**（README_ja.mdが明記）。**130/130件のCヘッダでERROR/MISSINGノード0件、432個の`typedef_declaration`が構造付きで捕捉されていることを検証済み**（`racc-tree-sitter-summary.md`、2026-09-13時点）。
- **配線状況（2026-09-23確認）**: [[TECSCDE-JS-TS実装]]の`src/cdl/grammar.ts`は姉妹文法`tree-sitter-cdl`（CDL本体用）のみを`initCdlParser()`でロードしており、`tree-sitter-tecs-cdecl`用のロード関数は存在しない。文法パッケージ自身は`lib/index.ts`に`loadTecsCdeclParser()`を用意しており、ロードパターンは`tree-sitter-cdl`と同一（`web-tree-sitter`の`Parser`/`Language`、WASM資産1個）。**したがって本節はゼロからの新規設計であり、既存コードの移植ではない。**
- **TYPE_NAME/IDENTIFIER区別の簡略化**: `C_parser.y.rb`はシンボルテーブル（`Namespace.is_typename?`）で以前に`typedef`された識別子を`TYPE_NAME`へ再タグ付けするが、`tree-sitter-tecs-cdecl`はこれを行わず、型が構文的に有効な位置ならどこでも`identifier`を`type_specifier_or_identifier`として受理し、曖昧さをGLR+`conflicts`で解決する（[[work/active/CDLParser(tree-sitter利用)/TECSCDE外部仕様 tree-sitter反映案|tree-sitter反映案]]が`tree-sitter-cdl`について記録した簡略化と同一方針）。**`CdeclExtractor`側にシンボルテーブルは不要**——文法が構造的に吸収済み。

### 9B.2 スコープの境界（明示）

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章]]と同じ書き方で、本節が閉じる範囲を明示する。

> [!warning] 本節は`CdeclExtractor`自体の入出力契約とアルゴリズムに閉じる
> 抽出した`typedef`/`struct`のレジストリを、実際に**シグニチャのポート型解決**や[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計|第8章の整合性チェック]]へ接続する設計は、本節の範囲外である——第3章（モデル設計）・第8章のいずれにも、この接続を扱う既存設計は無い（2026-09-23確認、`grep`0件）。接続設計は別の未設計課題として残す。
>
> **（2026-10-21 追記）この接続は実装済みである。** 抽出結果`cdeclResults`は`CdlDocumentLoader.loadSources`へ渡され、`CTypeRegistry`で署名の関数型を解決し、ポートの署名参照を完全修飾IDに正規化する。設計と読解の結果は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03 モデル設計|第3章3.4節]]。以下の「ポート型解決という実利用がまだ無い」という記述は、抽出器を設計した時点（2026-09-23）のものである。

### 9B.3 文法ローダ（`renderer/cdecl/grammar.ts`、新設）

> **実装との差（2026-11-17、三者相違一覧 8-19）**: 下のコード例は設計時の形である。実装は、関数形の`initCdeclParser()`ではなく`CdeclGrammar`の静的クラス（`init`・`isReady`・`parserInstance`）で、WASM は`/wasm/`への直接 fetch ではなく main の IPC（`cdl:grammar-assets`）から受け取る。**ファイル名は、ハイフンではなく下線**の`tree-sitter-tecs_cdecl.wasm`（`public/wasm/`）である。差分の一覧は 9B.7（差分 #1・#4）と[[TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計 — 実装時の差分|実装時の差分]]を参照。

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|第9章]]は触れていないが、実際には`renderer/cdl/grammar.ts`の`initCdlParser`と完全に同じパターンが既にJS-TS実装に存在する（[[TECSCDE内部仕様]]4.2/4.3節）。`CdeclExtractor`が使うパーサも同一パターンで用意する——新しい設計判断を持ち込まない。

```ts
// renderer/cdecl/grammar.ts
import { Language, Parser } from "web-tree-sitter";

export interface CdeclParserAssets {
  readonly runtimeWasm: string;
  /** tecs-cdecl文法（C_parser.y.rb 由来）。URL文字列またはバイト列。 */
  readonly cdeclWasm: string | Uint8Array;
}

const BROWSER_DEFAULTS: CdeclParserAssets = {
  runtimeWasm: "/wasm/tree-sitter.wasm",
  cdeclWasm: "/wasm/tree-sitter-tecs-cdecl.wasm",
};

let parser: Parser | undefined;
let initPromise: Promise<void> | undefined;

export function initCdeclParser(assets?: Partial<CdeclParserAssets>): Promise<void> {
  initPromise ??= (async () => {
    const resolved: CdeclParserAssets = { ...BROWSER_DEFAULTS, ...assets };
    await Parser.init({ locateFile: () => resolved.runtimeWasm });
    const language = await Language.load(resolved.cdeclWasm);
    const p = new Parser();
    p.setLanguage(language);
    parser = p;
  })();
  return initPromise;
}

export function isCdeclParserReady(): boolean {
  return parser !== undefined;
}

export function getCdeclParser(): Parser {
  if (!parser) {
    throw new Error(
      "cdeclパーサが未初期化です。import_Cの解決を始める前に initCdeclParser() の解決を待ってください。",
    );
  }
  return parser;
}

export function resetCdeclParserForTest(): void {
  parser = undefined;
  initPromise = undefined;
}
```

第2章2.4節（プロセス配置）の踏襲: `tree-sitter-cdl`と同じくrendererに置く（第11章11.2節#5で決着済みの判断がそのまま適用される——モジュールBはCDL用・cdecl用の2文法とも同一プロセスに置き、追加のIPC設計を増やさない）。WASM資産のロード経路（mainが`fs`で読みIPC経由でrendererへ渡す、第11章11.5節#7）も`tree-sitter-cdl.wasm`と同じ扱いにする。

### 9B.4 型モデル

Ruby版の型クラス（`CIntType`/`CFloatType`/`CBoolType`/`CVoidType`/`CPtrType`/`CArrayType`/`CFuncType`/`CStructType`/`CDefinedType`）を、判別ユニオン1個に単純化して移植する。ポート型解決という実利用がまだ無い（9B.2）ため、C言語の型の「形」を表現できれば十分で、Rubyのクラス階層は追わない。

```ts
// renderer/cdecl/types.ts
export type CType =
  | { readonly kind: "primitive"; readonly name: "void" | "char" | "short" | "int" | "long" | "int64" | "float" | "double" | "bool" }
  | { readonly kind: "pointer"; readonly pointee: CType }
  | { readonly kind: "array"; readonly element: CType; readonly size?: string } // sizeは定数式の生テキスト。評価はしない（9B.2の範囲外）
  | { readonly kind: "function"; readonly returns: CType } // パラメータ型は9B.2の範囲外につき保持しない（2026-10-21: 現行の`cdecl/types.ts`は`parameters?: readonly CType[]`を持つ。他にも組込型17種などを足した共用体に拡張済み。3.4節）
  | { readonly kind: "struct"; readonly tag?: string; readonly members?: readonly CStructMember[] } // タグ参照のみなら members は undefined
  | { readonly kind: "defined"; readonly name: string }; // 他のtypedef名への参照（Ruby版のCDefinedType）

export interface CStructMember {
  readonly name: string;
  readonly type: CType;
}

export interface CStructDef {
  readonly tag: string;
  readonly members: readonly CStructMember[];
}
```

### 9B.5 `CdeclExtractor.extract(text: string): CdeclResult`

本節は、25KB閾値のため[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計 — 9B.5 extract|別ノート]]へ分離した（2026-11-17、逐語）。CST の走査アルゴリズム、型の解決（`typedef`・`struct`・配列・関数型）、診断の扱いは、そちらにある。

### 9B.6 第9章9.6節との統合点

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計#9.6 `import_C`のCプリプロセッサ実行とフォールバック|第9章9.6節]]の手順2・3が「`CdeclExtractor`へ渡す・取り込む」としていた箇所を、本節で具体化する。

```ts
// renderer/app/import-resolution.ts（現行の実装の要約。別ファイルの`cdecl/registry.ts`やグローバルなMapは無い）
async function ingestImportC(
  tecsgenGateway: TecsgenGateway, canonicalPath: string, rawContent: string,
  cppCommand: string | undefined, includeDirs: readonly string[], diagnostics: Diagnostic[],
): Promise<CdeclResult> {
  const cpp = await tecsgenGateway.preprocess(canonicalPath, cppCommand, includeDirs);
  const usedFallback = !cpp.executableFound || cpp.exitCode !== 0;
  const text = usedFallback ? rawContent : cpp.stdout;
  if (usedFallback) diagnostics.push(cppFallback(canonicalPath, { command, originReason, fullPath, failureKind, failureDetail })); // W-CPP-FALLBACK。V0.2.1（09E）で、決定理由・フルパス・失敗の分類と詳細を渡す形に拡張した（2026-11-17に反映。`import-resolution.ts`）
  const result = CdeclExtractor.extract(text);
  if (result.hasErrors) diagnostics.push(cdeclParseError(canonicalPath)); // W-CDECL-PARSE
  return { ...result, usedFallback };
}
// 呼び出し元の resolveImportClosure が、結果を Map<正規化ヘッダパス, CdeclResult> に積んで返す。
// 型を解決する側は cdecl/type-registry.ts の CTypeRegistry（第3章3.4節）。
```

`ingestImportC`自体は9.6節の手順（プリプロセッサ成功時は展開後`stdout`、失敗時は生ヘッダテキスト）を単純に呼び分けるだけで、当初案の`cdeclRegistry`（モジュール内の可変なグローバル）は無く、結果は呼び出し元が返す`Map`に積まれる（2026-10-21更新）。また、`CdeclExtractor.extract()`は入力テキストがどちらの経路由来かを区別しない——[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携|TECSCDE外部仕様8.1.2節]]が既に述べているとおり「プリプロセッサ指令を含まないヘッダに対しては両者の結果は一致する」ため、抽出アルゴリズムを2経路で分ける理由がない。

### 9B.7 実装時の差分

設計案から実装時に判明した14件の差分（#1〜#8は2026-09-23、#9〜#14は2026-10-21にソースと照合して追加）（クラス設計・API形状・グローバル初期化の競合・文法の実際の挙動等）は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計 — 実装時の差分|サテライトノート]]に分離（2026-09-23、25KB閾値）。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計 — 実装時の差分|TECSCDE-DT-EL内部仕様 第9B章 実装時の差分（サテライト、9B.7節の分離先）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様 第9章（9.6節、本節が具体化する呼び出し元）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|TECSCDE-DT-EL内部仕様 第7E章（`CdeclExtractor`未実装を最初に指摘したノート）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧|TECSCDE-DT-EL内部仕様 第10章（モジュールBのインタフェース一覧の`CdeclExtractor.extract(text)`）]]
- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携|TECSCDE外部仕様 第8章8.1.2節（`typedef`/`struct`抽出の規定の一次情報源）]]
- [[work/active/CDLParser(tree-sitter利用)/TECSCDE外部仕様 tree-sitter反映案|TECSCDE外部仕様 tree-sitter反映案（`tree-sitter-tecs-cdecl`の採択経緯・検証実績）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

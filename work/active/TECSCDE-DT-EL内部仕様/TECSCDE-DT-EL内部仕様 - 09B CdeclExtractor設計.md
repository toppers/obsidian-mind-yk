---
date: 2026-09-23
description: "TECSCDE-DT-EL内部仕様書 第9章9.6節が名前を挙げるが未実装だった`CdeclExtractor`（モジュールB、typedef/struct抽出）の設計。tree-sitter-tecs-cdecl文法のCST走査アルゴリズムと型モデルを規定。2026-09-23同日中に実装完了（`src/renderer/cdecl/`、279テストpass）。実装時に判明した文法の実際の挙動（struct_declaratorのdeclaratorフィールドが無ラベル）を反映し更新。"
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

### 9B.3 文法ローダ（`renderer/cdecl/grammar.ts`、新設）

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
  | { readonly kind: "function"; readonly returns: CType } // パラメータ型は9B.2の範囲外につき保持しない
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

### 9B.5 `CdeclExtractor.extract(tree: Tree): CdeclResult`

CSTの走査対象ノードは`tree-sitter-tecs-cdecl`の`node-types.json`で確認済み（2026-09-23、`E:\Crepo\...\tools\tree-sitter-tecs-cdecl\src\node-types.json`）。

```ts
// renderer/cdecl/extractor.ts
import type { SyntaxNode, Tree } from "web-tree-sitter";
import type { CType, CStructDef, CStructMember } from "./types";
import { Diagnostic } from "../diagnostics/diagnostic"; // 第8章の既存クラスを再利用

export interface CdeclResult {
  readonly typedefs: ReadonlyMap<string, CType>;
  readonly structs: ReadonlyMap<string, CStructDef>;
  readonly diagnostics: readonly Diagnostic[];
}

export class CdeclExtractor {
  static extract(tree: Tree): CdeclResult {
    const typedefs = new Map<string, CType>();
    const structs = new Map<string, CStructDef>();

    // トップレベル限定ではなく全ノードを再帰的に走査する。文法側が
    // extern "C" { ... } の波括弧内部でも typedef_declaration / struct_declaration
    // を認識するよう既に作られているため（README_ja.md「_balanced_braces」節）、
    // ここで波括弧の深さを追跡する必要はない——node.typeだけを見ればよい。
    walk(tree.rootNode, (node) => {
      if (node.type === "typedef_declaration") {
        extractTypedef(node, typedefs);
      } else if (node.type === "struct_declaration") {
        extractStructDeclaration(node, structs);
      }
    });

    // ERROR/MISSINGノードが残っていても上記の走査は継続している
    // （第9章9.1節「実行が失敗してもその出力自体は提示する」と同じ方針）。
    // 失敗の事実だけを診断として報告する。
    const diagnostics = collectParseErrors(tree.rootNode);

    return { typedefs, structs, diagnostics };
  }
}

function walk(node: SyntaxNode, visit: (node: SyntaxNode) => void): void {
  visit(node);
  for (const child of node.namedChildren) {
    if (child) walk(child, visit);
  }
}

function extractTypedef(node: SyntaxNode, out: Map<string, CType>): void {
  // fields: type（enum_specifier|primitive_type|struct_specifier|type_qualifier|
  //   type_specifier_or_identifier|typeof_typeの並び、複数可）、declarator（declarator_list、必須）
  const typeNodes = node.childrenForFieldName("type");
  const baseType = resolveDeclarationSpecifiers(typeNodes);
  const declaratorList = node.childForFieldName("declarator");
  if (!declaratorList) return;

  for (const declarator of declaratorList.namedChildren) {
    if (!declarator) continue;
    const { name, type } = resolveDeclarator(declarator, baseType);
    if (name) out.set(name, type);
  }
}

function extractStructDeclaration(node: SyntaxNode, out: Map<string, CStructDef>): void {
  // struct_declaration → struct_specifier（fields: name=struct_tag, body=struct_declaration_list）
  const specifier = node.namedChildren.find((c) => c?.type === "struct_specifier");
  if (!specifier) return;
  const def = resolveStructSpecifier(specifier);
  if (def) out.set(def.tag, def);
}

/** struct_specifier を CType（無名なら members 付き、タグ付きなら参照として） へ、または呼び出し元用に CStructDef へ解決する。 */
function resolveStructSpecifier(specifier: SyntaxNode): CStructDef | undefined {
  const tagNode = specifier.childForFieldName("name"); // struct_tag（IDENTIFIER 1個）
  const bodyNode = specifier.childForFieldName("body"); // struct_declaration_list
  const tag = tagNode?.text;
  const members = bodyNode ? resolveStructBody(bodyNode) : [];
  if (!tag) return undefined; // 無名structはタグでの再参照ができないため registry には載せない（9B.2の範囲外）
  return { tag, members };
}

function resolveStructBody(bodyNode: SyntaxNode): readonly CStructMember[] {
  const members: CStructMember[] = [];
  for (const memberDecl of bodyNode.namedChildren) {
    // struct_member_declaration: fields type（declaration_specifiers）, declarator（struct_declarator_list）
    if (!memberDecl || memberDecl.type !== "struct_member_declaration") continue;
    const typeNode = memberDecl.childForFieldName("type");
    const baseType = typeNode ? resolveDeclarationSpecifiers(typeNode.namedChildren) : voidType();
    const declaratorList = memberDecl.childForFieldName("declarator"); // struct_declarator_list
    if (!declaratorList) continue;
    for (const structDeclarator of declaratorList.namedChildren) {
      // struct_declarator: fields declarator（任意、declarator 1個）, bitfield（任意、式——評価しない）
      const declaratorNode = structDeclarator?.childForFieldName("declarator");
      if (!declaratorNode) continue;
      const { name, type } = resolveDeclarator(declaratorNode, baseType);
      if (name) members.push({ name, type });
    }
  }
  return members;
}

/** declaration_specifiers（複数ノードの並び）を1つのCTypeへ畳み込む。Ruby版のdeclaration_specifiersの
 *  chained-merge（storage class無視・type_specifier/type_qualifierの積み重ね）に対応。 */
function resolveDeclarationSpecifiers(nodes: readonly (SyntaxNode | null)[]): CType {
  for (const node of nodes) {
    if (!node) continue;
    switch (node.type) {
      case "primitive_type":
        return { kind: "primitive", name: mapPrimitiveName(node.text) };
      case "struct_specifier": {
        const def = resolveStructSpecifier(node);
        return def ? { kind: "struct", tag: def.tag, members: def.members } : { kind: "struct" };
      }
      case "type_specifier_or_identifier":
        return { kind: "defined", name: node.text };
      case "type_qualifier": // const/volatile — 型の形には影響しないため無視（Ruby版もqualifierは形に含めない）
      case "storage_class": // extern/static等 — 無視（Ruby版と同じ）
        continue;
      case "enum_specifier": // 単独では到達不可（文法がenum単独をトリガーしない、README_ja.md）。typedef対象にはなり得る
      case "typeof_type":
      case "union_specifier":
        return voidType(); // Ruby版もenum/unionは「voidが宣言されたとする」扱い（C_parser.y.rb 337-340行）
    }
  }
  return voidType();
}

/** declarator（再帰的なpointer/array_declarator/function_declarator/identifierの入れ子）を
 *  名前とCTypeへ分解する。Ruby版のポインタ・配列・関数ポインタ修飾の組み立てに対応。 */
function resolveDeclarator(node: SyntaxNode, baseType: CType): { name?: string; type: CType } {
  if (node.type === "identifier") {
    return { name: node.text, type: baseType };
  }
  if (node.type === "array_declarator") {
    const inner = node.childForFieldName("declarator");
    const sizeNode = node.childForFieldName("size");
    const arrayType: CType = { kind: "array", element: baseType, size: sizeNode?.text };
    return inner ? resolveDeclarator(inner, arrayType) : { type: arrayType };
  }
  if (node.type === "function_declarator") {
    const inner = node.childForFieldName("declarator");
    const funcType: CType = { kind: "function", returns: baseType };
    return inner ? resolveDeclarator(inner, funcType) : { type: funcType };
  }
  if (node.type === "declarator") {
    const pointerNode = node.childForFieldName("pointer");
    const innerType = pointerNode ? resolvePointer(pointerNode, baseType) : baseType;
    const inner = node.namedChildren.find(
      (c) => c && ["array_declarator", "declarator", "function_declarator", "identifier"].includes(c.type),
    );
    return inner ? resolveDeclarator(inner, innerType) : { type: innerType };
  }
  return { type: baseType };
}

/** pointer（再帰的な入れ子で多重ポインタを表現）を CType.pointer の連鎖へ変換する。 */
function resolvePointer(node: SyntaxNode, pointeeType: CType): CType {
  const nestedPointer = node.namedChildren.find((c) => c?.type === "pointer");
  const inner: CType = nestedPointer ? resolvePointer(nestedPointer, pointeeType) : pointeeType;
  return { kind: "pointer", pointee: inner };
}

function mapPrimitiveName(text: string): Extract<CType, { kind: "primitive" }>["name"] {
  // primitive_typeのテキストは "unsigned long" 等、複数トークンを含み得る（declaration_specifiersの
  // 畳み込みでは1個目の primitive_type しか見ないため、"unsigned"/"signed"/"const" 等の修飾語は現状は
  // 落ちる——符号・幅の精密な再現は9B.2の範囲外（ポート型解決という実利用がまだ無いため）。
  const normalized = text.trim().split(/\s+/).pop() ?? "int";
  const known = ["void", "char", "short", "int", "long", "int64", "float", "double", "bool"] as const;
  return (known as readonly string[]).includes(normalized) ? (normalized as (typeof known)[number]) : "int";
}

function voidType(): CType {
  return { kind: "primitive", name: "void" };
}

function collectParseErrors(root: SyntaxNode): readonly Diagnostic[] {
  const diagnostics: Diagnostic[] = [];
  walk(root, (node) => {
    if (node.type === "ERROR" || node.isMissing) {
      diagnostics.push(Diagnostic.warning("W-CDECL-PARSE", `Cヘッダの一部を解析できませんでした（${node.type}）`));
    }
  });
  return diagnostics;
}
```

**設計判断の注記**:
- `mapPrimitiveName`が`unsigned`/`signed`/`const`等の修飾語を落とす簡略化は、9B.2で明示したとおり「ポート型解決という実利用がまだ無い」段階での意図的な割り切り。実際にポート型解決へ接続する設計（別課題）に着手する際は、Ruby版`CIntType`の符号・幅表現（`set_sign`/幅パラメータ）を見直し、必要なら精密化する。
- 無名`struct { ... }`（タグなし）は`typedefs`側の`CType`には`members`付きで反映されるが、`structs`（タグ→定義のレジストリ）には載らない（再参照する手段がタグ以外に無いため）。これはRuby版の`CStructType.new()`（無名）と`CStructType.new(tag)`（タグ付き）の違いに対応する。

### 9B.6 第9章9.6節との統合点

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計#9.6 `import_C`のCプリプロセッサ実行とフォールバック|第9章9.6節]]の手順2・3が「`CdeclExtractor`へ渡す・取り込む」としていた箇所を、本節で具体化する。

```ts
// renderer/cdecl/registry.ts — モジュールBが保持する、ヘッダファイルパスごとの抽出結果
const cdeclRegistry = new Map<string, CdeclResult>();

/** 第9章9.6節の手順2・3の実装。preprocess結果の成否に応じて展開後テキスト or 生テキストを渡す。 */
function ingestImportC(headerPath: string, text: string): CdeclResult {
  const tree = getCdeclParser().parse(text);
  const result = CdeclExtractor.extract(tree);
  cdeclRegistry.set(headerPath, result);
  return result;
}
```

`ingestImportC`自体は9.6節の手順（プリプロセッサ成功時は展開後`stdout`、失敗時は生ヘッダテキスト）を単純に呼び分けるだけであり、`CdeclExtractor.extract()`は入力テキストがどちらの経路由来かを区別しない——[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携|TECSCDE外部仕様8.1.2節]]が既に述べているとおり「プリプロセッサ指令を含まないヘッダに対しては両者の結果は一致する」ため、抽出アルゴリズムを2経路で分ける理由がない。

### 9B.7 実装時の差分

設計案から実装時に判明した8件の差分（クラス設計・API形状・グローバル初期化の競合・文法の実際の挙動等）は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計 — 実装時の差分|サテライトノート]]に分離（2026-09-23、25KB閾値）。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計 — 実装時の差分|TECSCDE-DT-EL内部仕様 第9B章 実装時の差分（サテライト、9B.7節の分離先）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様 第9章（9.6節、本節が具体化する呼び出し元）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|TECSCDE-DT-EL内部仕様 第7E章（`CdeclExtractor`未実装を最初に指摘したノート）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧|TECSCDE-DT-EL内部仕様 第10章（モジュールBのインタフェース一覧に`CdeclExtractor.extract(cst)`と記載済み）]]
- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携|TECSCDE外部仕様 第8章8.1.2節（`typedef`/`struct`抽出の規定の一次情報源）]]
- [[work/active/CDLParser(tree-sitter利用)/TECSCDE外部仕様 tree-sitter反映案|TECSCDE外部仕様 tree-sitter反映案（`tree-sitter-tecs-cdecl`の採択経緯・検証実績）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

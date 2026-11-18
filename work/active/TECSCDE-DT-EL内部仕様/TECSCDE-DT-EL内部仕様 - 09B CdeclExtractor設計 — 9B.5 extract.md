---
date: 2026-11-17
description: "内部仕様9B章の9B.5節（`CdeclExtractor.extract(text)`の設計。CSTの走査アルゴリズムと型の解決）。9B章が25KBを超えたため分離。原文のまま。"
project: TECS
quarter: Q3-2026
status: active
verbatim: true
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

# TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計 — 9B.5 extract

[[TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|9B章]]の9B.5節を分離した（2026-11-17、25KB閾値）。原文のまま。9B章の他の節は、親ノートにある。

### 9B.5 `CdeclExtractor.extract(text: string): CdeclResult`

CSTの走査対象ノードは`tree-sitter-tecs-cdecl`の`node-types.json`で確認済み（2026-09-23、`E:\Crepo\...\tools\tree-sitter-tecs-cdecl\src\node-types.json`）。

> [!note] 2026-10-21 に実装（`src/renderer/cdecl/extractor.ts`）に合わせて更新
> 当初（2026-09-23）の設計案は`extract(tree: Tree)`で、診断（`Diagnostic[]`）も返すものだった。実装は**テキストを受け取り、内部で`CdeclGrammar.parserInstance.parse(text)`する**`extract(text: string)`で、診断は作らず`hasErrors: boolean`と`usedFallback: boolean`だけを返す（診断はヘッダパスを知る呼び出し側が作る）。以下のコードは現行の実装に合わせた要約で、設計案との差は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計 — 実装時の差分|差分の一覧]]（#2、#3、#6、#7、#9〜#14）に記録している。

```ts
// renderer/cdecl/extractor.ts（現行の実装の要約）
import type { Node as SyntaxNode } from "web-tree-sitter";
import { CdeclGrammar } from "./grammar";
import type { CType, CStructDef, CStructMember } from "./types";

export interface CdeclResult {
  readonly typedefs: ReadonlyMap<string, CType>;
  readonly structs: ReadonlyMap<string, CStructDef>;
  readonly usedFallback: boolean; // 抽出器自身は常にfalse。呼び出し側（ingestImportC）が上書きする
  readonly hasErrors: boolean;    // ERROR／MISSINGノードが残っていたか。走査は継続し、捕捉できた範囲は返す
}

export class CdeclExtractor {
  static extract(text: string): CdeclResult {
    const tree = CdeclGrammar.parserInstance.parse(text);
    const typedefs = new Map<string, CType>();
    const structs = new Map<string, CStructDef>();
    let hasErrors = false;
    if (!tree) return { typedefs, structs, hasErrors: true, usedFallback: false };

    // トップレベル限定ではなく全ノードを再帰的に走査する。文法側が extern "C" { ... } の内部でも
    // typedef_declaration / struct_declaration を認識するため、波括弧の深さは追跡しない。
    walk(tree.rootNode, (node) => {
      if (node.type === "ERROR" || node.isMissing) hasErrors = true;
      else if (node.type === "typedef_declaration") extractTypedef(node, typedefs);
      else if (node.type === "struct_declaration") extractStructDeclaration(node, structs);
    });
    return { typedefs, structs, hasErrors, usedFallback: false };
  }
}

function extractTypedef(node: SyntaxNode, out: Map<string, CType>): void {
  const baseType = resolveDeclarationSpecifiers(node.childrenForFieldName("type"));
  const declaratorList = node.childForFieldName("declarator");
  if (!declaratorList) return;
  for (const declarator of declaratorList.namedChildren) {
    if (!declarator) continue;
    const { name, type } = resolveDeclarator(declarator, baseType);
    if (name) out.set(name, type);
  }
}

function extractStructDeclaration(node: SyntaxNode, out: Map<string, CStructDef>): void {
  const specifier = node.namedChildren.find((c) => c?.type === "struct_specifier");
  if (!specifier) return;
  const { tag, members } = resolveStructSpecifierMembers(specifier);
  if (tag) out.set(tag, { tag, members: members ?? [] }); // 無名structはレジストリに載せない
}

/** タグと、本体（{ ... }）があればメンバー一覧。本体が無い（タグ参照のみ）ときmembersはundefinedで、空のstruct定義と区別する。 */
function resolveStructSpecifierMembers(specifier: SyntaxNode): { tag?: string; members?: readonly CStructMember[] } {
  const tagNode = specifier.childForFieldName("name");
  const bodyNode = specifier.childForFieldName("body");
  return { tag: tagNode?.text, members: bodyNode ? resolveStructBody(bodyNode) : undefined };
}

function resolveStructBody(bodyNode: SyntaxNode): readonly CStructMember[] {
  const members: CStructMember[] = [];
  for (const memberDecl of bodyNode.namedChildren) {
    if (!memberDecl || memberDecl.type !== "struct_member_declaration") continue;
    const typeNode = memberDecl.childForFieldName("type");
    const baseType = typeNode ? resolveDeclarationSpecifiers(typeNode.namedChildren) : voidType();
    const declaratorList = memberDecl.childForFieldName("declarator");
    if (!declaratorList) continue;
    for (const structDeclarator of declaratorList.namedChildren) {
      // struct_declaratorのdeclarator子にはフィールド名が付かない（差分#6）ので型で探す
      const declaratorNode = structDeclarator?.namedChildren.find((c) => c?.type === "declarator");
      if (!declaratorNode) continue;
      const { name, type } = resolveDeclarator(declaratorNode, baseType);
      if (name) members.push({ name, type });
    }
  }
  return members;
}

/** declaration_specifiersを1つのCTypeへ畳み込む（最初に意味のある型指定子を採用）。 */
function resolveDeclarationSpecifiers(nodes: readonly (SyntaxNode | null)[]): CType {
  for (const node of nodes) {
    if (!node) continue;
    switch (node.type) {
      case "primitive_type": return mapPrimitiveName(node.text);
      case "struct_specifier": { const { tag, members } = resolveStructSpecifierMembers(node); return { kind: "struct", tag, members }; }
      case "type_specifier_or_identifier": return { kind: "defined", name: node.text };
      case "type_qualifier": // const/volatile
      case "storage_class":  // extern/static等
        continue;            // 型の形に影響しないため無視（Ruby版と同じ）
      case "enum_specifier":
      case "typeof_type":
      case "union_specifier":
        return { kind: "unsupported", name: node.text };
      default: continue;
    }
  }
  return voidType();
}

/** declarator（pointer／array_declarator／function_declarator／identifierの入れ子）を名前とCTypeへ分解する。 */
function resolveDeclarator(node: SyntaxNode, baseType: CType): { name?: string; type: CType } {
  if (node.type === "identifier") return { name: node.text, type: baseType };
  if (node.type === "array_declarator") {
    const inner = node.childForFieldName("declarator");
    const arrayType: CType = { kind: "array", element: baseType, size: node.childForFieldName("size")?.text };
    return inner ? resolveDeclarator(inner, arrayType) : { type: arrayType };
  }
  if (node.type === "function_declarator") {
    const inner = node.namedChildren.find((child) => child && child.type !== "parameter_type_list");
    const params = (node.childForFieldName("parameters")?.namedChildren ?? [])
      .filter((child): child is SyntaxNode => child?.type === "parameter_declaration")
      .map((parameter) => {
        const typeNode = parameter.childForFieldName("type");
        const base = typeNode ? resolveDeclarationSpecifiers(typeNode.namedChildren) : voidType();
        const declaration = parameter.childForFieldName("declarator");
        return declaration ? resolveDeclarator(declaration, base).type : base;
      });
    const funcType: CType = { kind: "function", returns: baseType, parameters: params };
    return inner ? resolveDeclarator(inner, funcType) : { type: funcType };
  }
  if (node.type === "declarator") {
    const pointerNode = node.childForFieldName("pointer");
    const innerType = pointerNode ? resolvePointer(pointerNode, baseType) : baseType;
    const inner = node.namedChildren.find(
      (c) => c !== null && ["array_declarator", "declarator", "function_declarator", "identifier"].includes(c.type),
    );
    return inner ? resolveDeclarator(inner, innerType) : { type: innerType };
  }
  return { type: baseType };
}

/** 入れ子のpointerをCType.pointerの連鎖へ変換する。 */
function resolvePointer(node: SyntaxNode, pointeeType: CType): CType {
  const nested = node.namedChildren.find((c) => c?.type === "pointer");
  const inner: CType = nested ? resolvePointer(nested, pointeeType) : pointeeType;
  return { kind: "pointer", pointee: inner };
}

/** "unsigned long"のような複数トークンは、末尾を基本型名、元の表記をspellingに保持する。未知の名前はunsupported。 */
function mapPrimitiveName(text: string): CType {
  const normalized = text.trim().split(/\s+/).pop() ?? "int";
  const known = ["void", "char", "short", "int", "long", "int64", "float", "double", "bool"];
  return known.includes(normalized)
    ? { kind: "primitive", name: normalized, ...(text.trim() === normalized ? {} : { spelling: text.trim() }) }
    : { kind: "unsupported", name: text };
}

function voidType(): CType { return { kind: "unsupported", name: "型指定子なし" }; }
```

**設計判断の注記**:
- **修飾語の扱い（2026-10-21更新）**: 当初は`unsigned`／`signed`等を落とす簡略化だったが、実装は`mapPrimitiveName`が基本型名（末尾のトークン）と元の表記（`spelling`）の両方を保持し、`unsigned long`なら`name: "long"`、`spelling: "unsigned long"`にする。`const`／`volatile`は`type_qualifier`として型の形に影響しないため無視する。Ruby版`CIntType`の符号・幅表現の精密な再現は、今も行っていない。ポート型解決への接続は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03 モデル設計|第3章3.4節]]。
- **未対応の型指定子**: `enum`・`typeof`・`union`は`{ kind: "unsupported", name: <原文> }`にする（当初案はRuby版に合わせて`void`扱い）。型指定子が見つからないとき（`voidType()`）も`unsupported`（名前は「型指定子なし」）で、`void`とは区別する。未知の基本型名も`int`に丸めず`unsupported`にする。
- **関数の型**: `function_declarator`から引数の型も取り出し、`CType.function.parameters`に持たせる（当初案は戻り値のみ）。
- **WASMの解放**（2026-10-22に修正）: 以前の`extract()`は`parse()`で得た`tree`を`delete()`せず（`CdlDocumentBuilder.build`は`tree?.delete()`を呼ぶ）、ヘッダごとに呼ばれるため、Treeのメモリが解放されない可能性があった（影響の大きさは未測定）。走査を`try { … } finally { tree.delete(); }`で囲み、例外が出ても解放するようにした。抽出結果（`typedefs`・`structs`）は、ノードの`text`から作った純粋なデータでノードを参照しないため、解放後も安全に使える。
- 無名`struct { ... }`（タグなし）は`typedefs`側の`CType`には`members`付きで反映されるが、`structs`（タグ→定義のレジストリ）には載らない（再参照する手段がタグ以外に無いため）。これはRuby版の`CStructType.new()`（無名）と`CStructType.new(tag)`（タグ付き）の違いに対応する。

## Related

- [[TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|9B章 CdeclExtractor設計]]
- [[TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計 — 実装時の差分|実装時の差分]]
- [[TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|第9章 tecsgen連携設計]]

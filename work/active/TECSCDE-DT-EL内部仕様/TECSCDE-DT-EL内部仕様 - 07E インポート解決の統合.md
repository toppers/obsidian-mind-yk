---
date: 2026-09-22
description: "TECSCDE-DT-EL内部仕様書 第7章7.5節（インポート自動追跡）の詳細設計・後半 — renderer側の再帰的解決オーケストレーション（resolveAllImports）、import_Cの第9章9.6節への受け渡し境界、診断への変換（W-UNRESOLVED-REF-FILE再利用）、direct_importとの区別、既存コードへの統合ポイント、未決事項。第7D章から分離（2026-09-22、25KB閾値）。"
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

Domain note split from [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|TECSCDE-DT-EL内部仕様 第7D章]] (2026-09-22, 25KB閾値)。第7D章が定めた`FileService.resolveImports()`をrenderer側でどう使うか、境界、統合ポイントをまとめる。

## 7.5.4 renderer: 再帰的解決オーケストレーション

`import`文の参照先はさらに自身の`import`文を持ちうる（推移的閉包）。この再帰はrenderer側で行う——モジュールBのパース自体はrendererにしかなく、mainはファイルの探索・読み取りしか担わない（第2章2.3節の依存方向）。

```ts
// renderer/app/import-resolution.ts（新規）
import { ToolInfoValidator } from "../cdl/tool-info";
import { CdlDocumentBuilder, type ImportDecl } from "../cdl/cst";
import type { FileGateway } from "../gateways/file-gateway";
import type { ImportRequest, ImportResolutionOptions, OpenFileEntry } from "../../shared/ipc-types.js";
import type { ToolInfoTecsgen } from "../model/tool-info-types";
import type { Diagnostic } from "../diagnostics/types";
import { unresolvedReferenceFile } from "../cdl/messages"; // 7.5.6節

function toImportRequest(decl: ImportDecl): ImportRequest {
  return { kind: decl.kind, specifier: decl.path };
}

/** [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|第7D章7.5.1節]]: モジュールBの既存出力を取り出すだけ。新しい解析は行わない。 */
function extractImportRequests(text: string): readonly ImportRequest[] {
  const { sourceWithBlanks } = ToolInfoValidator.extractBlocks(text);
  return CdlDocumentBuilder.build(sourceWithBlanks).imports.map(toImportRequest);
}

/**
 * 編集対象ファイルの`import`/`import_C`を推移的に解決する。
 * `import_C`は再帰しない——Cヘッダ自身はCDLの`import`文を持たず、内容の扱いは
 * 9.6節（Cプリプロセッサ実行／フォールバック）へ委ねる（7.5.5節）。
 */
export async function resolveAllImports(
  gateway: FileGateway,
  editablePath: string,
  editableText: string,
  toolInfo: ToolInfoTecsgen,
): Promise<{ references: OpenFileEntry[]; diagnostics: Diagnostic[] }> {
  const options: ImportResolutionOptions = { baseDir: toolInfo.baseDir, importPaths: toolInfo.importPath ?? ["."] };
  const resolvedPaths = new Set<string>(); // 循環・重複抑止のキー（正規化済み絶対パス）
  const extraSearchDirs: string[] = []; // 第7D章7.5.3節: 解決が進むごとに成長する
  const references: OpenFileEntry[] = [];
  const diagnostics: Diagnostic[] = [];

  let frontier = extractImportRequests(editableText);
  while (frontier.length > 0) {
    const resolved = await gateway.resolveImports(editablePath, frontier, { ...options, extraSearchDirs });
    const nextFrontier: ImportRequest[] = [];

    for (const r of resolved) {
      if (r.error || !r.canonicalPath) {
        diagnostics.push(unresolvedReferenceFile(r.request.specifier)); // 7.5.6節
        continue;
      }
      if (resolvedPaths.has(r.canonicalPath)) continue; // 循環・重複
      resolvedPaths.add(r.canonicalPath);
      references.push({ path: r.canonicalPath, content: r.content! });

      const dir = r.canonicalPath.replace(/[\\/][^\\/]*$/, "");
      if (!extraSearchDirs.includes(dir)) extraSearchDirs.push(dir); // 累積

      if (r.request.kind === "import") {
        nextFrontier.push(...extractImportRequests(r.content!)); // 推移的closure
      }
    }
    frontier = nextFrontier;
  }
  return { references, diagnostics };
}
```

**バッチ単位**: 1回の`gateway.resolveImports`呼び出しは「現在のフロンティア（まだ解決していない要求の集合）」をまとめて渡す——importが1個ずつIPCの往復を作らない。フロンティアが空になるまでのラウンド数は木の深さに等しく、実際のCDLプロジェクトで想定される深さ（数階層）では往復回数は小さい。

**手動追加（第7C章#8）との合流**: `resolveAllImports`自身は`kind: 'manual'`を発行しない——手動追加は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合#7.7.2 ファイルブラウザからの参照専用追加（#8）|第7C章7.7.2節`addAsReference`]]が別途1件の`kind: 'manual'`要求として`gateway.resolveImports`を直接呼ぶ（同じ`resolveOne`実装を経由するが、`resolveAllImports`のループの外側）。両者は重複判定のキー（正規化済み絶対パス）を共有するべきだが、`resolveAllImports`が使う`resolvedPaths`はこの関数のローカル変数であり、`addAsReference`とは別セッションで動く——**実装時に、既に読み込み済みの参照ファイル集合全体（`store.getReferenceFilePaths()`相当）を両方の重複判定が参照するよう統合する必要がある**（未決事項、7.5.9節）。

## 7.5.5 `import_C`の扱いと第9章9.6節への受け渡し境界

本節（第7D・7E章）が`import_C`に対して行うのは**パスの解決とヘッダの生テキスト読み取りのみ**——`typedef`/`struct`の抽出、Cプリプロセッサの実行とフォールバックは[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計#9.6 `import_C`のCプリプロセッサ実行とフォールバック|第9章9.6節]]が既に規定し、`TecsgenRunner.preprocess()`（main）・`TecsgenGateway.preprocess()`（renderer）まで実装済みである（IPC配線はコミット済み、[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|実装]]の`afb6b32`）。

**境界**: `resolveAllImports`が`kind: "import_C"`の`ResolvedImport`（ヘッダの絶対パス＋生テキスト）を得たら、9.6節の手順（`TecsgenGateway.preprocess(canonicalPath, toolInfo.cpp)`を呼び、成功なら展開後テキストを、失敗なら生テキストを`CdeclExtractor`へ渡す）を実行する。`resolveAllImports`自身は`import_C`の結果を`references`に含めない——参照ファイルとして図には現れないCヘッダ（[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携|TECSCDE外部仕様8.1.1節]]「セルタイプ・シグニチャの定義もこの解析経路で読み込まれるが、図には現れない」）を`OpenFileEntry`（図の参照ファイル一覧に載る想定の型）に混ぜないためである。**実装時の訂正（2026-09-23）**: 当初「呼び出し側（resolveAllImportsの呼び出し元）が実行する」としていたが、実装では`resolveAllImports`/`resolveAddedReference`が共通で使う`resolveImportClosure`自身の中（`import_C`分岐）で`ingestImportC()`を呼ぶ形にした——`tecsgenGateway`を`resolveAllImports`/`resolveAddedReference`の新規パラメータとして受け取り、そのまま`resolveImportClosure`へ渡す。結果は新しい戻り値`cdeclResults: Map<string, CdeclResult>`（canonicalPath→抽出結果）に集約される。

> [!success] `CdeclExtractor`（モジュールB、typedef/struct抽出）— 設計・実装完了（2026-09-23）
> 第9章9.6節が名前を挙げる`CdeclExtractor`クラスは、2026-09-22時点の実装に存在しなかった（`grep`で0件）。2026-09-23、[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|第9B章]]として設計、同日中に`src/renderer/cdecl/{grammar,types,extractor}.ts`として実装し、`import-resolution.ts`の`resolveImportClosure`へ統合した（279テストpass、`npm run check` green）。ポート型解決・第8章の整合性チェックへの実接続は依然スコープ外のまま（9B章9B.2）——`cdeclResults`は戻り値として返るだけで、`store`側の保持先はまだ無い。

## 7.5.6 診断への変換

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計|第8章]]の既存決定により、解決できなかった参照先は**新しい診断コードを作らず**既存の`W-UNRESOLVED-REF-FILE`（`unresolvedReferenceFile()`、`src/renderer/cdl/messages.ts`84〜90行）を再利用する。

> [!note] 文言の見直しが必要（実装時に確定）
> `unresolvedReferenceFile()`の現在の文言「参照専用ファイル `${fileName}` は未解決です（再度ファイル選択してください）」は、8.2.2節の`direct_import`（利用者が手動で再選択する想定）向けに書かれている。本節が追加する`import`/`import_C`自動追跡の失敗は利用者の手動操作を経ないため、「再度ファイル選択してください」という指示は的外れになりうる——`import_path`/`base_dir`の設定を見直すよう促す文言への分岐が実装時に必要（未決事項）。

## 7.5.7 `direct_import`との違い（混同注意）

本節が扱う`import`/`import_C`（CDL構文中の文）と、`__tool_info__.directImport`（[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携|TECSCDE外部仕様8.2節]]）は**起点の異なる別概念**である（8.1.1節が示す表のとおり）。

| | 起点 | 本節での扱い |
|---|---|---|
| `import`/`import_C`（CDL構文） | ファイル内容そのもの | **自動追跡する**（本節、外部仕様8.1節） |
| `direct_import`（`__tool_info__`） | 起動時にコマンドライン引数として編集対象と一緒に渡された「兄弟ファイル」の記録 | **自動追跡しない**——[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様8.2節]]は8.2.2節（ブラウザ版）を「完全に同一、変更なし」と踏襲しており、Electronでファイルシステムに実際アクセスできるようになっても、この一覧の再読み込みは自動化されていない。再読み込みは`W-UNRESOLVED-REF-FILE`の提示に留まる（8.3.2節） |

DT-EL版がファイルシステムへ実際にアクセスできるようになったことで`direct_import`側も自動追跡できる余地はあるが、これは**外部仕様側の変更を要する別提案**であり、本節（第7章7.5節）の範囲には含めない。

## 7.5.8 既存コードへの統合ポイント（実装時の変更点）

`resolveAllImports`（7.5.4節）は、`OpenResult`を`TecscdeDocument`へ組み立てる直前——`applyOpenResult`（`src/renderer/app/file-actions.ts`21〜32行）の内部で呼ぶのが最も自然である。両方の既存呼び出し元（`openFromPath`・renderer起動時の`onBootstrap`ハンドラ、`src/renderer/main.ts`35〜38行）が`applyOpenResult`を経由するため、変更点はこの1箇所に閉じる。

- `applyOpenResult`は非同期になり、`gateway: FileGateway`を新たに受け取る（現在は`store`と`result`のみ）。
- `result.editable`をパースして得た`ImportRequest[]`を`resolveAllImports`で解決し、その`references`を、既存の`result.references`（手動指定・[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合#7.7.1 前回セッションの復元（#7）|第7C章7.7.1節]]の前回セッション復元由来）と**正規化済み絶対パスで重複排除**して合流させたうえで`CdlDocumentLoader.loadSources()`へ渡す。
- `resolveAllImports`が返す`diagnostics`は、`CdlDocumentLoader.loadSources()`が返す既存の診断（構文エラー等）と合流させ、`store.loadDocument()`の`loadDiagnostics`引数へまとめて渡す。
- `CdlDocumentLoader.loadSources()`自身のシグネチャ・純粋性（同期・IPC非依存）は変更しない——推移的解決はすべて`loadSources`呼び出しの**手前**で完了させる。これにより既存のround-tripテスト（`loadSources`を直接同期で呼ぶもの）に影響しない。

この統合により、[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|第7C章]]の#8（7.7.2節`addAsReference`）・#10（7.7.4節`loadOptionsFile`）・#11（7.7.5節）は、それぞれの節が既に書いている`gateway.resolveImports(...)`呼び出しをそのまま実行できるようになる——7C章の記述変更は不要である。

## 7.5.9 未決事項・実装時に確定する事項

- **UTF-8判定の厳密化**（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡#7.5.2 main FileServiceresolveImports|第7D章7.5.2節]]）: `fs.readFile(..., "utf-8")`が不正バイト列を無音で置換する問題への対処方針。
- **手動追加と自動追跡の重複判定統合**（7.5.4節）: `resolveAllImports`のローカルな`resolvedPaths`と、`addAsReference`（第7C章#8）が参照すべき「現在読み込み済みの参照ファイル集合」の統合方法。
- **`W-UNRESOLVED-REF-FILE`の文言分岐**（7.5.6節）: 自動追跡失敗時の適切なメッセージ。
- **`extraSearchDirs`の起動直後の引き継ぎ**（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡#7.5.3 tecsgen本体のアルゴリズムとの対応関係|第7D章7.5.3節]]）: 前回セッションの`base_dir`蓄積を今回の最初の解決ラウンドに反映するかどうか（現状は反映しない設計だが、実害は未検証）。
- ~~`CdeclExtractor`の実装~~ → **解消済み（2026-09-23）**: [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|第9B章]]の設計に基づき実装完了。残るのは抽出結果（`cdeclResults`）をポート型解決・第8章整合性チェックへ接続する設計（9B章9B.2の範囲外のまま）。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|TECSCDE-DT-EL内部仕様 第7D章（本節の前半。resolveImportsの具体アルゴリズム・tecsgen本体との対応検証）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章（7.5節の分離元、7.1〜7.4節）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|TECSCDE-DT-EL内部仕様 第7C章（本節が実装前提を満たす#8/#10/#11の設計本体）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様 第9章（9.6節、import_Cの受け渡し先）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|TECSCDE-DT-EL内部仕様 第9B章（`CdeclExtractor`自体の設計、2026-09-23完了）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計|TECSCDE-DT-EL内部仕様 第8章（W-UNRESOLVED-REF-FILEの再利用決定）]]
- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携|TECSCDE外部仕様 第8章（direct_importとの区別、8.1.1・8.2節）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

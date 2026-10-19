---
date: 2026-09-22
description: "TECSCDE-DT-EL内部仕様書 第7章7.5節（インポート自動追跡）の詳細設計・前半 — モジュールBが既に持つimport解析の再利用、FileService.resolveImports()の具体アルゴリズム、tecsgen本体（Importable#find_file）との対応関係の実地検証。後半（renderer側オーケストレーション・import_C境界・診断・統合ポイント）は第7E章へ分離（2026-09-22、25KB閾値）。"
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

Domain note split from [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章]] (2026-09-22)。第7章7.5節「インポート参照先の解決」が型定義とプロセス概要のみだった状態から、具体アルゴリズム・tecsgen本体との対応検証までを詳細化する（前半）。renderer側オーケストレーション以降は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章]]へ分離（25KB閾値）。

## 7.5 インポート自動追跡（`FileService.resolveImports()`）の詳細設計 — 2026-09-22

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様8.1節]]の`import`/`import_C`自動追跡を実現する。第7C章の手動追加・オプションファイル読み込み・import統一は`FileService.resolveImports()`を共有する。2026-09-22には設計対象だったが、現在は通常CDL由来の全セルを編集可能として実装済みである。

### 7.5.1 モジュールBの既存出力（`ParsedCdl.imports`）——解析はすでにある

`import`/`import_C`文自体は**すでにモジュールBが解析済み**である。[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]]由来の`CdlDocumentBuilder`（`src/renderer/cdl/cst.ts`）が、tree-sitterのCSTを走査する際に`import`/`import_c`ノードを検出し、`ParsedCdl.imports: readonly ImportDecl[]`として返している（53〜61行・157〜170行）。

```ts
// src/renderer/cdl/cst.ts（既存、変更不要）
export interface ImportDecl {
  readonly kind: "import" | "import_C";
  readonly path: string;
  readonly rawText: string; // 保存時に原文のまま書き戻すための複写
}
```

`ParsedCdl.imports`から得る`import`/`import_C`要求をmainのファイルI/Oへつなぐ。現在の`CdlDocumentLoader.loadSources()`は主ファイルと追加読み込みした通常CDLの情報を保持し、変更した各CDLを元のパスへ保存する。

### 7.5.2 main: `FileService.resolveImports()`

```ts
// shared/ipc-types.ts（既存の型を維持。'manual'は第7C章7.7.2節が追加）
export interface ImportRequest {
  readonly kind: "import" | "import_C" | "manual";
  readonly specifier: string; // kind:'manual'は絶対パスそのもの（7.7.2節）
}

export interface ImportResolutionOptions {
  readonly baseDir?: string; // __tool_info__.baseDir（永続化された単一値）
  readonly importPaths: readonly string[]; // __tool_info__.importPath（既定 ["."]）
  readonly cpp?: string; // import_C用。resolveImports自身は使わず、9.6節へ引き渡すだけ
  /**
   * 7.5.3節: 解決が進むごとにrendererが蓄積する追加の探索ディレクトリ
   * （tecsgenの`$base_dir`集合を、chdirを使わずに再現するための引数）。
   * 初回呼び出しでは省略可（空扱い）。
   */
  readonly extraSearchDirs?: readonly string[];
}

export interface ResolvedImport {
  readonly request: ImportRequest;
  readonly canonicalPath?: string; // 正規化済み絶対パス。循環・重複抑止のキー（renderer側で使う）
  readonly content?: string; // UTF-8として読めた場合のみ
  readonly error?: "not-found" | "not-utf8" | "read-failed";
}
```

```ts
// main/file-service.ts に追加
async resolveImports(
  editablePath: string,
  requests: readonly ImportRequest[],
  options: ImportResolutionOptions,
): Promise<readonly ResolvedImport[]> {
  const searchDirs = [
    dirname(editablePath), // 7.5.3節: tecsgen本体には無い、実務上の追加候補
    ...(options.baseDir ? [options.baseDir] : []),
    ...(options.extraSearchDirs ?? []),
  ];
  return Promise.all(requests.map((request) => this.resolveOne(request, searchDirs, options.importPaths)));
}

private async resolveOne(
  request: ImportRequest,
  searchDirs: readonly string[],
  importPaths: readonly string[],
): Promise<ResolvedImport> {
  // 7.7.2節: 'manual'は絶対パスが直接指定されているため、探索を経由せず存在確認のみ行う。
  const candidates =
    request.kind === "manual"
      ? [request.specifier]
      : searchDirs.flatMap((dir) =>
          importPaths.map((p) => (p === "." ? join(dir, request.specifier) : join(dir, p, request.specifier))),
        );

  for (const candidate of candidates) {
    try {
      const content = await fs.readFile(candidate, "utf-8");
      return { request, canonicalPath: resolve(candidate), content };
    } catch (err) {
      const code = (err as NodeJS.ErrnoException).code;
      if (code === "ENOENT") continue; // このcandidateは無かった。次を試す
      return { request, error: code === "EILSEQ" ? "not-utf8" : "read-failed" };
    }
  }
  return { request, error: "not-found" };
}
```

`fs.readFile(path, "utf-8")`はファイルが存在しても不正なUTF-8バイト列だと`TextDecoder`相当の変換で例外にならず**文字化けした文字列をそのまま返す**——Node.jsの`utf-8`デコードは無効バイト列を`U+FFFD`に置換して継続するため、`not-utf8`を確実に検出するには不正シーケンスの有無を明示的に確認する処理が要る（**実装時に確定**、[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|外部仕様5.1.2節]]がCDLをUTF-8前提とする以上、無視できない差ではあるが、置換文字が実害を伴うかは未検証）。

### 7.5.3 tecsgen本体のアルゴリズムとの対応関係——実地検証で「未検証」を解消する

これまで本節（旧7.5節）は「編集対象ファイルのディレクトリ→base_dir→import_pathの順」を**独自の簡略化**と自認し、tecsgen本体の実際の解決順序との一致を「inferred・未検証」としていた。今回、一次資料`Importable#find_file`（`E:\Crepo\toppers-tecs-svn\toppers\tecsgen\branches\ykominami_r3033\tecsgen\tecslib\core\componentobj\importable.rb`49〜95行）を実際に読み、対応関係を確定する。

```ruby
# importable.rb（要約）— 実際の探索順序
def find_file(file)
  $import_path.each { |path|                    # フェーズ1: import_pathを現在のDir.pwd起点で試す
    pt = (path == ".") ? file : "#{path}/#{file}"
    if File.exist?(pt)
      $base_dir[Dir.pwd] = true                  # 成功したCWD自体をbase_dir集合へ追加
      return pt
    end
  }
  $base_dir.each_key { |bd|                      # フェーズ2: 蓄積済みbase_dirを1つずつchdirして再試行
    $import_path.each { |path|
      Dir.chdir(bd)
      pt = "#{path}/#{file}"
      if File.exist?(pt)
        $base_dir[bd] = true
        return pt
      end
    }
  }
  return nil
end
```

**3つの重要な事実**（コード自体から読み取れる、憶測ではない）:

1. `$base_dir`はハッシュ＝**集合**であり、tecsgen起動時は空。**同一tecsgen実行中に成功した解決のたびにディレクトリが追加され、後続のimportの探索範囲が広がっていく**（累積的）。
2. `import_path`はどのフェーズでも**同じ相対解釈**（`path == "."`なら`file`そのもの、そうでなければ`"#{path}/#{file}"`）で使われる。フェーズ1と2の違いは「起点ディレクトリ」だけである——フェーズ1は現在の`Dir.pwd`起点、フェーズ2は`Dir.chdir(bd)`した後の`bd`起点。
3. **「編集対象ファイル自身のディレクトリ」を優先候補として特別扱いする分岐はコード上どこにも無い。** フェーズ1が実質それに近い効果を持つのは、tecsgenの起動時のCWDが呼び出し元シェルのディレクトリ（多くの場合、対象ファイルの置き場所と一致する）であることが多いという**運用上の偶然**に過ぎない。

**対応関係の確定（旧「inferred・未検証」を解消）**:

| tecsgen本体 | 本節の設計 | 対応 |
|---|---|---|
| フェーズ1（現在の`Dir.pwd`起点） | `searchDirs[0] = dirname(editablePath)` | **一致しない場合がある**（3の理由）。ただしCLIの慣習的な使い方（対象ファイルのあるディレクトリで実行する）と実務上ほぼ一致する |
| フェーズ2（`$base_dir`を1つずつchdirして再試行） | `searchDirs`の2番目以降（`options.baseDir`→`extraSearchDirs`） | **構造は一致**（両方とも「起点ディレクトリを1つずつ替えてimport_path全体を再試行」） |
| `$base_dir`の累積（同一実行中に成長する集合） | `extraSearchDirs`（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章7.5.4節]]でrenderer側が成長させ、次回呼び出しへ渡す） | **意図は一致するが値が違う**——`__tool_info__.baseDir`は永続化された**単一の直近値**（8.2.1節の`get_base_dir`が返すのも`@last_base_dir`という単一値）であり、tecsgenの実行中に築かれる**履歴全体の集合**ではない。永続化データから履歴全体を復元することはできない |
| `Dir.chdir`によるプロセス全体の作業ディレクトリ変更 | 使わない。`searchDirs`は呼び出し側（renderer）が明示的に持つ値のリスト | **意図的な差**——mainプロセスのCWDをリクエストごとに変更するのは並行するIPCハンドラ間で状態が競合し危険。tecsgenは単一プロセス・単一実行のバッチツールのためchdirが安全だが、Electronのmainプロセスは複数のIPC呼び出しを並行に処理し得る |

**結論（決定）**: 3の理由により「編集対象ファイルのディレクトリ→蓄積された起点ディレクトリの列→各起点でのimport_path全探索」という本節の構造は、**tecsgen本体のフェーズ2部分（累積探索）を`Dir.chdir`無しに再現し、フェーズ1相当（現在のCWD起点）を実務上最も近い代替である「編集対象ファイルのディレクトリ」に置き換えたもの**であり、恣意的な簡略化ではない。**唯一埋まらない差**は、`base_dir`が単一の永続化値である以上、**tecsgenの一度の実行内で蓄積される履歴全体をアプリ再起動後にも復元することはできない**という点——ただしこれは`extraSearchDirs`（同一の開く操作の中で解決が進むにつれて成長する）が実行時には解消しており、影響が残るのは「前回セッションの`base_dir`蓄積を今回のセッション開始時点で引き継げない」という起動直後の1点に限られる。実害の有無は未検証のまま残す——`import_path`に`"."`が既定で含まれる限り、多くのプロジェクトでは編集対象ファイルの置き場所からの相対探索で事足りるため、この差が実際に解決失敗を招くかは実装後の検証課題とする。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|TECSCDE-DT-EL内部仕様 第7E章（本節の続き。renderer側オーケストレーション・import_C境界・診断・統合ポイント）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章（本節の分離元、7.1〜7.4節）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|TECSCDE-DT-EL内部仕様 第7C章（本節が実装前提を満たす#8/#10/#11の設計本体）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様 第8章（8.1節、本節が実装する自動追跡の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

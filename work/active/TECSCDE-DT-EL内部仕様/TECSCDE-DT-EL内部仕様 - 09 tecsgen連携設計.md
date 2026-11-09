---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様 第9章 — tecsgen実行・C前処理・Plugin生成型の取り込み。opts経由のPlugin型取り込みで文字コード指定がなければ-k utf8を追加し、明示指定は尊重する。欠落は2026-10-22に解消済み。"
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

> [!info] V0.2.0差分設計（2026-11-06）
> V0.2.0の起動パス解決・即時反映・版再確認と、外部実行とは別のメモリ内処理は[[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理]]を優先します。Cプリプロセッサの設定仕様まで変更するものではありません。差分章は実装前の内部設計です。


Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 9 of 11. Electron固有化の中心章の1つ。

## 9. tecsgen連携設計

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様第8章8.4節]]が採用した「tecsgenをサブプロセスとして直接実行する」を、Electronの`child_process`で実現する。コマンド文字列の組み立て（`TecsgenCommandBuilder`）は[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 09 tecsgen連携設計|TECSCDE-TS内部仕様第9章]]の設計を**そのまま踏襲、変更なし**——第2章2.3節のとおり、この部分は純粋な文字列処理でありrendererに残る。新規に追加するのは実際の実行部分である。

> [!note] `-k`（CDLファイルの文字コード指定）: 2026-09-24に追加、opts経由のPlugin型取り込みの欠落も2026-10-22に解消済み
> [[work/active/tecsgen/tecsgen外部仕様 - 05 コマンドラインインターフェース|tecsgen外部仕様第5章]]によれば、tecsgenはCDLファイルの文字コードを`-k, --kcode`（値は`euc`／`sjis`／`none`／`utf8`、既定`euc`）で指定する。2026-09-21にこのオプションが組み立てられていない欠落を見つけ（踏襲元のTS内部仕様第9章は、ブラウザ版が「コマンド文字列を提示するだけで実行しない」設計だったため、実害がなかった）、**2026-09-24に追加した**（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|11.2節#6]]、コミット`6425b25`）。
>
> **現行の実装**（`renderer/tecsgen/command-builder.ts`の`TecsgenCommandBuilder.buildArgs`）: 引数の**先頭に常に`-k utf8`を置く**。続けて、`importPath`の1件ごとに`-I <path>`、`defineMacro`の1件ごとに`-D <macro>`、`cpp`があれば`-c <cmd>`、参照専用ファイル、編集対象ファイルの順に並べる。`buildCommandLine`（「コマンドをコピー」）も同じ`buildArgs`を使うので、提示される文字列にも`-k utf8`が含まれる。理由はコード内のコメントのとおり、CDLファイルはUTF-8前提（[[TECSCDE外部仕様]]5.1.2節）なのに、tecsgenの既定が`euc`だから。**実際に文字化けや構文エラーが出るか（`-k`なしの場合）は未確認(inferred)**。
>
> **`-k utf8`が付かない経路があった → 解消（2026-10-22）**: `.tecsgen-opts`から開いたときのPlugin型の取り込み（9.7節）は、`TecsgenRunner.generatedTypes`がオプションファイルの中身をそのまま引数にし、`-k`が付かなかった（tecsgenの既定は`euc`）。**オプションファイルに`-k`／`--kcode`が無いときは、`-g <dir>`の直後に`-k utf8`を足す**ようにした（書かれていればその値を尊重する）。`-k`の判定は`-k <code>`・`-k<code>`・`--kcode <code>`・`--kcode=<code>`の各形。実測（tecsgen-rb 1.9.1）では、UTF-8のコメントを含むCDLは`-k`なしでも成功したが、生成物の案内文の言語が変わった（`-k`なしは英語、`-k utf8`は日本語）。コメント以外に非ASCIIがあるCDLの挙動は未確認。
>
> また、`.tecsgen-opts`の解析（7.7.4節）は`-k`／`--kcode`を読み取らず無視する（値の`utf8`などはCDLファイル名でないので`cdlFiles`に入らない）。

### 9.1 `TecsgenRunner`クラス（mainプロセス）

```ts
// main/tecsgen-runner.ts（型は shared/ipc-types.ts。抜粋。全体の一次情報はソース）
export interface CppResult { stdout: string; stderr: string; exitCode: number | null; executableFound: boolean }

// 起動失敗の種類（9.7節）。終了コードでは表せないものを、実行結果とは別に持つ。
export type TecsgenLaunchFailureKind = 'not-found' | 'permission' | 'timeout' | 'output-overflow' | 'launch-error';
export interface TecsgenLaunchFailure { kind: TecsgenLaunchFailureKind; command: string; detail: string }
export interface TecsgenResult {
  stdout: string; stderr: string; exitCode: number | null;
  executableFound: boolean;               // ENOENT（見つからない）のときだけfalse
  launchFailure?: TecsgenLaunchFailure;   // 起動失敗のとき設定される
}

class TecsgenRunner {
  // 実行ファイルは環境変数 TECSGEN_COMMAND（無ければ tecsgen）。シェルは介さない（外部仕様2.4節）。
  run(args, cwd?, execOptions?): Promise<TecsgenResult>;      // 既定は30秒。cwd指定時の既定は120秒・16MiB
  generate(args, cwd?): Promise<TecsgenResult>;               // 「実行(Generate)」用。cwdを指定しても30秒のまま
  generatedTypes(args, editingFilePath, optionsFilePath?): Promise<GeneratedCdlResult>;  // Plugin型の取り込み（9.7節、外部仕様8.1）
  preprocess(headerPath, cppCommand?, includeDirs?): Promise<CppResult>;  // import_C のCプリプロセス（9.6節）
  version(): Promise<TecsgenVersionResult>;                   // 版の確認（第9C章）
}
```

> [!note] この節のコードは抜粋
> 2026-10-22に、擬似コードを全文で持つのをやめた。引数の追加（`cwd`、`includeDirs`）やメソッドの追加（`generate`、`generatedTypes`）のたびに、ここが古くなっていたため。メソッドの一覧と型は上のとおりで、本体の挙動は9.7節（`run`の結果の写像、起動失敗の分類）、9.6節（`preprocess`）、第9C章（`version`）、第7C章7.7.4節（`generate`の`cwd`）にある。IPCで公開される全体の型は`src/shared/ipc-types.ts`の`TecscdeApi`が一次情報。`run`は、実行ファイルを`TECSGEN_COMMAND`から決め、`execFile`で起動して、成功なら`{ exitCode: 0, executableFound: true }`を返す。`ENOENT`は`launchFailure: { kind: 'not-found' }`と`executableFound: false`、権限なし・タイムアウト・出力過多などは`exitCode: null`と該当の`launchFailure`、数値の終了コードで終わったもの（`tecsgen`自身の失敗）は`exitCode`にその値を入れて返し、例外にしない。

**非0終了時の契約（2026-11-08、監査#26）**: `run()`は、tecsgenが数値の非0終了コードで終わっても、その理由でPromiseをrejectしない。`exitCode`に終了コードを設定し、`executableFound: true`、`launchFailure`なし、標準出力・標準エラー出力を保持した`TecsgenResult`を返す。下位の`execFile`が非0終了をエラーとして通知しても、`run()`内で結果へ変換する。呼び出し側は非0終了を`try/catch`の例外経路として処理せず、返された結果を診断解析へ渡す。構文・意味エラーで実行が失敗した場合も、出力自体は提示する。起動失敗の`launchFailure`との区別は9.7節の表に従う。

### 9.2 IPCハンドラの登録（main）

```ts
// main/ipc.ts（tecsgen関連のチャネルの抜粋）
ipcMain.handle('tecsgen:generate', (_e, args, cwd?) => tecsgenRunner.generate(args, cwd));
ipcMain.handle('tecsgen:generatedTypes', (_e, args, editingFilePath, optionsFilePath?) => tecsgenRunner.generatedTypes(args, editingFilePath, optionsFilePath));
ipcMain.handle('tecsgen:preprocess', (_e, headerPath, cppCommand?, includeDirs?) => tecsgenRunner.preprocess(headerPath, cppCommand, includeDirs));
ipcMain.handle('tecsgen:version', () => tecsgenRunner.version());
```

### 9.3 `TecsgenGateway`クラス（renderer）

```ts
// renderer/gateways/tecsgen-gateway.ts（window.tecscde.tecsgen を薄くラップする。抜粋）
class TecsgenGateway {
  generate(args, cwd?): Promise<TecsgenResult>;
  generatedTypes(args, editingFilePath, optionsFilePath?): Promise<GeneratedCdlResult>;
  preprocess(headerPath, cppCommand?, includeDirs?): Promise<CppResult>;
  version(): Promise<TecsgenVersionResult>;
}
```

### 9.4 実行結果の診断への変換

```ts
class TecsgenResultParser {
  // <ファイル名>:<行>:<列>: error|warning: <メッセージ> を解析する（TECSCDE外部仕様9.1.1の書式）
  static parse(result: TecsgenResult): readonly Diagnostic[] {
    const out: Diagnostic[] = [];
    // 起動失敗は種類ごとに1件のエラーにする（9.7節）。見つからない場合はそれだけを返す
    if (result.launchFailure) {
      out.push(Diagnostic.error(codeOf(result.launchFailure.kind), describeLaunchFailure(result.launchFailure)));
      if (result.launchFailure.kind === 'not-found') return out;
    }
    const lines = (result.stdout + result.stderr).split('\n');
    out.push(...lines.map(line => this.parseLine(line)).filter((d): d is Diagnostic => d !== null));
    // 非0終了なのに書式に一致するエラー行が1つも無ければ、E-TECSGEN-FAILEDを1件足す（9.7節）
    if (!result.launchFailure && result.exitCode !== 0 && !out.some(d => d.severity === 'error')) {
      out.push(Diagnostic.error('E-TECSGEN-FAILED', describeTecsgenFailure(result)));
    }
    return out;
  }

  private static parseLine(line: string): Diagnostic | null { /* 正規表現で書式を解析し Diagnostic.error/warning を構築 */ return null; }
}
```

解析結果は第8章の`DiagnosticsCollector.report()`へ渡し、インポート診断と同じ一覧・ジャンプ機構で提示する。[[TECSCDE-DT-EL内部仕様 - 08B 診断位置へのソースジャンプ|8B]]に従い、実行時cwd・原位置の単位・解析時ソースを関連付ける（2026-11-08、監査#18の追加契約）。生成本文は一時ディレクトリ削除前に保持し、クリック時の再生成や消えた一時パスへの読込で代用しない。実装適合は未確認。

### 9.5 実行の起点

「実行(Generate)」操作（[[TECSCDE-DT外部仕様]]8.4.2節）はモジュールG（UIシェル）から`TecsgenGateway.generate()`を呼ぶ。実行は利用者が明示的にトリガーする操作に限り、保存やインポートのたびに自動実行しない方針は[[TECSCDE-DT外部仕様]]と同一。

### 9.6 `import_C`のCプリプロセッサ実行とフォールバック

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様8.1節]]が定める`import_C`の2経路の優先順位を実装する。

1. 第7章7.5節で`import_C`対象のCヘッダが解決された際、rendererは`TecsgenGateway.preprocess(headerPath, cpp)`を呼ぶ。
2. プリプロセッサの実行が成功（`executableFound === true && exitCode === 0`）した場合、展開後の`stdout`テキストをrendererの`CdeclExtractor`（モジュールB、設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|9B章]]）へ渡し、`typedef`／`struct`定義を取り込む。
3. プリプロセッサが見つからない（`executableFound === false`）または実行に失敗した（`exitCode !== 0`）場合は、未展開の生ヘッダテキストに対して`CdeclExtractor`を実行する**フォールバック経路**へ切り替える。
4. フォールバック時は第8章の`W-CPP-FALLBACK`警告を発行し、`#include`未展開・`#ifdef`未評価の差分が生じ得る旨を利用者に提示する。

### 9.7 tecsgen起動失敗の診断（2026-10-21、[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 02 動作環境|DT外部仕様2.4節]]・[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|DT外部仕様8.4.2節]]・[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 09 エラーと警告|DT外部仕様9.1節]]とソースの照合）

外部仕様の規定: tecsgen本体は利用者の環境に依存する外部プロセスで、**実行ファイルが見つからない、または起動に失敗した場合は、その旨をエラーとして提示する**（2.4節、8.4.2節）。実行結果は9章の形式に変換し、同じ一覧・同じジャンプ機構で提示する（9.1節）。以下は、根拠を`main/tecsgen-runner.ts`、`renderer/diagnostics/tecsgen-result-parser.ts`、`renderer/tecsgen/failure-summary.ts`、`renderer/app/tecsgen-actions.ts`、`renderer/app/file-actions.ts`の読解とした現行実装の振る舞い（テストは読んでいない）。

**tecsgenを起動する経路は2つある**: 利用者が明示的に起動する「実行(Generate)」と、CDLを開くときに内部で起動して**Plugin生成CDLの型を取り込む**経路（2026-10-22に、外部仕様8.1節に時機・起動・読み取り・失敗を、9.4節に失敗時の診断を規定した）。

**`TecsgenRunner.run`の結果への写像**（9.1節の擬似コードとの差を含む）:

| 起こったこと | `TecsgenResult` | 備考 |
|---|---|---|
| 正常終了 | `exitCode: 0`、`executableFound: true` | |
| `ENOENT`（実行ファイルが無い） | `exitCode: null`、`executableFound: false`、出力は空、`launchFailure: { kind: 'not-found', … }` | 実行ファイルが無い場合 |
| 非0で終了 | `exitCode: e.code`（数値）、標準出力・標準エラー出力を保持。`launchFailure`は無い | tecsgenは走ったので起動失敗ではない |
| 権限なし（`EACCES`・`EPERM`） | `exitCode: null`、`executableFound: true`、`launchFailure: { kind: 'permission', … }` | 2026-10-22に分類を追加 |
| タイムアウトによる強制終了（`killed`） | 同上、`kind: 'timeout'`、出力は得られた分 | 同上 |
| 出力量が`maxBuffer`を超えた（`ERR_CHILD_PROCESS_STDIO_MAXBUFFER`） | 同上、`kind: 'output-overflow'` | 同上 |
| 上記以外（`TECSGEN_COMMAND`が空、`E2BIG`など） | 同上、`kind: 'launch-error'`、`detail`にエラーコードまたはメッセージ | 同上 |

**起動失敗の定義と診断への写像**（2026-10-22。外部仕様2.4節・8.4.2節の「実行ファイルが見つからない、または起動に失敗した場合はエラーとして提示する」の実現）: 実行ファイルが**無い**場合と、**実行時に**起動・実行が異常になった場合の両方を、`TecsgenResult.launchFailure`で一貫して表す。`TecsgenResultParser`は`launchFailure`を持つ結果を、種類ごとに次の1件のエラー（位置なし）へ変換する。`executableFound`は互換のため残し、`ENOENT`のときだけ`false`になる（`import_C`のプリプロセッサの経路は従来どおりこれを使う）。

| `kind` | コード | 文言の要点 |
|---|---|---|
| `not-found` | `E-TECSGEN-NOT-FOUND` | 実行ファイル名（`TECSGEN_COMMAND`を使っていればその先頭）が、PATH上またはTECSGEN_COMMANDの指定先に無い。インストールしてPATHに追加するか、TECSGEN_COMMANDを設定して再起動する |
| `permission` | `E-TECSGEN-NO-PERMISSION` | 実行権限が無い。権限と実行可能な形式かを確認する |
| `timeout` | `E-TECSGEN-TIMEOUT` | 制限時間内に終了せず強制終了された |
| `output-overflow` | `E-TECSGEN-OUTPUT-OVERFLOW` | 出力が上限を超えて強制終了された |
| `launch-error` | `E-TECSGEN-LAUNCH-FAILED` | 起動できなかった（`detail`を添える） |

- `not-found`以外は、得られた出力の書式行も続けて診断にする（一覧の先頭に起動失敗のエラーが並ぶ）。
- 非0で終了し、かつ書式に一致するエラー行が1つも無いときは、`E-TECSGEN-FAILED`（error）を1件足す。文言は`describeTecsgenFailure`（終了コードと、エラーらしい行または出力の末尾）。従来はこの場合に診断が1件も出なかった。
- 文言は`renderer/tecsgen/failure-summary.ts`の`describeLaunchFailure`が作る。Generate経路（`TecsgenResultParser`）とPlugin型の取り込み経路（下記の`W-PLUGIN-TYPE-LOAD`）が同じ関数を使うので、同じ失敗は同じ文言になる。
- 分類は`main/tecsgen-runner.ts`の`classifyLaunchFailure`（数値の終了コードなら起動失敗ではない）。実装は`TecsgenResult`の型（`shared/ipc-types.ts`）、`TecsgenResultParser`、`app/file-actions.ts`に反映済み。テストは`tests/main/tecsgen-runner.test.ts`と`tests/renderer/tecsgen-result-parser.test.ts`。

- **実行ファイルの決定**: 環境変数`TECSGEN_COMMAND`があれば、それを引用符つきで分割した先頭を実行ファイル、残りを先頭の引数として使う（空なら例外→上の表の「上記以外」）。無ければ`tecsgen`をPATHから探す。擬似コードの`execFileAsync('tecsgen', …)`固定とは異なる。
- **時間と出力量**: Generate（`TecsgenRunner.generate(args, cwd?)`、2026-10-22新設）は`timeout: 30_000`のみ（`maxBuffer`はNodeの既定）。`.tecsgen-opts`を開いているときは`cwd`（そのあるディレクトリ、第7C章7.7.4節）を指定するが、上限は変えない。Plugin型の取り込み（`run(args, cwd)`）は`timeout: 120_000`、`maxBuffer: 16MiB`。`run`の引数も擬似コードに無い。

**Generate経路**（`app/tecsgen-actions.ts`）: 前提（保存先がある、実行中でない、未保存なら自動保存して未保存が残らない）を満たさなければ、何も実行せずに返す。`TecsgenResultParser.parse`の結果を`store.setTecsgenDiagnostics`へ渡す。
- **起動失敗**: 上の表のとおり、`kind`に応じたエラー（`E-TECSGEN-NOT-FOUND`など）1件（severity=error、位置なし）。見つからない場合の文言は「tecsgen が見つかりません（実行ファイル '…' が PATH 上、または TECSGEN_COMMAND の指定先に無い）。…」。
- **それ以外**: 標準出力と標準エラー出力を行ごとに解析し、書式（`<ファイル>:<行>:<列>: error|warning: <本文>`、または位置なしの`error|warning: <本文>`）に一致した行だけを診断にする。本文が`G1015`のようなtecsgenのコードで始まれば`code`へ分け、無ければ`ERROR`／`WARNING`とする。**一致しない行は捨てる**（進捗出力で一覧を汚さないため）。ただし非0終了でエラー行が1つも無ければ`E-TECSGEN-FAILED`を足す。

**Plugin型の取り込み経路**（`app/file-actions.ts`の`generatedTypes`の呼び出し）: 失敗しても開く処理は続行し、警告`W-PLUGIN-TYPE-LOAD`（severity=warning）1件にまとめる。
- **起動失敗**: 「Plugin生成型を読み込めませんでした: 」に`describeLaunchFailure`の文を続ける。見つからない場合は「tecsgen が見つかりません（実行ファイル '…' が PATH 上、または TECSGEN_COMMAND の指定先に無い）。tecsgen をインストールして PATH に追加するか、環境変数 TECSGEN_COMMAND に起動コマンドを設定してアプリを再起動してください。」。
- **非0終了**: 同じ接頭辞に`describeTecsgenFailure`の文を続ける。これは「tecsgen が失敗しました（終了コード N）」に、標準エラー出力→標準出力の順で、`error`／`fatal`／`エラー`を含む行（重複除去、各行300文字まで、最大10行、超過は「…ほか N 件」）を添える。該当行が無ければ出力の末尾10行。
- **読み込み側の例外**（Plugin生成CDLの件数1万・総量100MiBの上限超過、文字コードの判定失敗など）も同じ警告にまとめる。

**`import_C`のCプリプロセッサ**（9.6節）は、`ENOENT`でも、それ以外の起動失敗でも非0でも、`exitCode !== 0 || !executableFound`としてフォールバックし、`W-CPP-FALLBACK`を出す。ここでは9.6節の規定と実装が一致している。

> [!warning] 外部仕様との差分（読解のみ）
> 1. ~~**`ENOENT`以外の起動失敗が診断にならない**~~ → **解決（2026-10-22）**: 起動失敗を`launchFailure`で種類別に表し、Generate経路・Plugin型の取り込み経路ともエラー（または警告）として提示するようにした。非0終了で書式に一致する行が無い場合も`E-TECSGEN-FAILED`で提示する（上の「起動失敗の定義と診断への写像」）。
> 2. **Generateの30秒・既定`maxBuffer`**: Plugin型の取り込みより小さい上限で、tecsgenが成功時にも大量の進捗を標準出力へ出す（`failure-summary.ts`の注記）ため、出力過多で強制終了される可能性がある（動作は未確認）。 **決定（2026-10-22）: 上限は変更しない（Generate は30秒・既定 `maxBuffer` のまま）。実測はしない。超過した場合は `E-TECSGEN-TIMEOUT`／`E-TECSGEN-OUTPUT-OVERFLOW` として提示されるため、実際に問題が出てから見直す。**
> 3. ~~**`TECSGEN_COMMAND`**: 外部仕様に無い~~ → **解消（2026-10-22）**: 外部仕様2.4節と8.4.2節に規定を追加した（書式・適用範囲・反映・失敗・Windowsでの注意）。文言は2026-10-22に、PATHと`TECSGEN_COMMAND`の指定先の両方を挙げ、実際に起動しようとした実行ファイル名を示す形に直した。
> 4. ~~**Plugin型の取り込みの失敗**: 外部仕様に規定が無い~~ → **解消（2026-10-22）**: 外部仕様9.4節に、警告（`W-PLUGIN-TYPE-LOAD`）にとどめて開く処理を続ける、と規定した（現行動作のとおり）。
> 5. ~~`W-PLUGIN-TYPE-LOAD`と`E-TECSGEN-NOT-FOUND`は、警告コード表にも載っていない。~~ → **解消（2026-10-22）**: 外部仕様9.4節に`E-TECSGEN-*`・`W-PLUGIN-TYPE-LOAD`・`W-TECSGEN-VERSION-*`の一覧を載せた。TS内部仕様8.3節のコード表（親仕様）はDT-ELでは変更せず、DT-EL固有のコードは内部仕様8章の記述で補う。

### 9.8 tecsgenの版の確認（2026-10-22）

起動時に`tecsgen --version`で版を確認し、古い場合に警告する設計は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09C tecsgen版の確認|第9C章]]に置いた（外部仕様8.4.2）。25KB閾値のため別ノートにした。9.1節の`version()`と9.3節の`TecsgenGateway.version()`は、第9C章の`TecsgenVersionResult`を返す形に改めた。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|TECSCDE-DT-EL内部仕様 第9B章（9.6節が名前を挙げる`CdeclExtractor`自体の設計、2026-09-23）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様 第8章（本章が実装する外部仕様、8.1・8.4節）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 09 tecsgen連携設計|TECSCDE-TS内部仕様 第9章（TecsgenCommandBuilderの一次情報源。TS版は`-k`を持たず、DT-ELが追加した）]]
- [[work/active/tecsgen/tecsgen外部仕様 - 05 コマンドラインインターフェース|tecsgen外部仕様 第5章（`-k`/`--kcode`の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様 第11章（`-k`の決定記録、11.2節#6）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章（インポート参照先解決）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計|TECSCDE-DT-EL内部仕様 第8章（診断の集約先・W-CPP-FALLBACK）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（プロセス配置の根拠）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

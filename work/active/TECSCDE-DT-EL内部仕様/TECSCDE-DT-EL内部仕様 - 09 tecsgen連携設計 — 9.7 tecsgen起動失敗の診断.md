---
date: 2026-11-17
description: "内部仕様9章の9.7節（tecsgen起動失敗の診断。起動失敗の定義、診断への写像、分類表）。9章が25KBを超えたため分離。原文のまま。"
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

# TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計 — 9.7 tecsgen起動失敗の診断

[[TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|第9章]]の9.7節を分離した（2026-11-17、25KB閾値）。原文のまま。第9章の他の節は、親ノートにある。

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

- **実行ファイルの決定**: 環境変数`TECSGEN_COMMAND`があれば、それを引用符つきで分割した先頭を実行ファイル、残りを先頭の引数として使う（空なら例外→上の表の「上記以外」）。無ければ、V0.2.0以降は、保存済みの`tecsgenPath`、実在する`TECSPATH`、`PATH`の順に決める（[[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理|9D]]。V0.1.0は`PATH`上の`tecsgen`）。擬似コードの`execFileAsync('tecsgen', …)`固定とは異なる。
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

## Related

- [[TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|第9章 tecsgen連携設計]]
- [[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理|9D]]
- [[TECSCDE-DT-EL内部仕様 - 09E V0.2.1 Cプリプロセッサ設定と失敗詳細|9E]]

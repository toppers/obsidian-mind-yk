---
date: 2026-11-09
description: "三者監査59〜69の内部仕様契約補足。既決要件と現行コードの差を区別する。"
project: TECS
quarter: Q4-2026
status: active
tags: [work-note, tecs, tecscde, spec]
---

# TECSCDE-DT-EL内部仕様 - 監査対応 59-69 環境と文書

[[TECSCDE-DT-EL内部仕様]]の補足。[[TECSCDE-DT外部仕様 - 監査対応 59-69 環境と文書]]と対になる。

2026-11-09の確定契約・実装境界を記す。関連する旧時点の実装記録を、今回のコードの適合確認として扱わない。既存の決定と未決事項（TBC）を維持し、未決を完成済みにしない。仕様を修正してもソース修正が必要な項目は未実装のままである。

## 監査59

**tecsgen設定・自動探索・保存後の再確認が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 59-69 環境と文書#監査59]]に対応する。

mainの設定サービスとパス解決器を唯一の解決点とし、Generate・Plugin外部取り込み・版確認が同じ有効設定を使う。sharedのDTO、IPC、preload、SettingsGateway経由で保存値・起動元・revisionを返す。未設定と空保存を区別し、解除後の次の解決は既存9D.3に従う。保存は既存JSONを部分更新し、現在の図や実行中プロセスを変えない。版再確認はrevisionで旧応答を除外し、正常になった場合も旧環境診断と旧設定由来の起動失敗を除く。現在の設定API・Runnerは未反映なので要実装とし、優先順位、空解除、保存失敗、逆順応答、診断差替えを受入条件とする。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/main/tecsgen-runner.ts:124` — `const [executable, ...prefixArgs] = process.env.TECSGEN_COMMAND`
- `src/shared/ipc-types.ts:126` — `readonly allowEditSystemDefined: boolean;`
- `src/renderer/app/tecsgen-version.ts:92` — `if (diagnostics.length > 0) {`

**受入条件**: 4段階の優先順位、自動保存、確認失敗値の保存、空解除、旧revision破棄、成功再確認で旧警告が消えること。設定保存失敗時は図と現設定を保持。

参照: [[TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界]]、[[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、[[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理]]。

## 監査60

**確定済みのPlugin型取り込み内部経路・方式選択が未実装**

[[TECSCDE-DT外部仕様 - 監査対応 59-69 環境と文書#監査60]]に対応する。

file-actionsはPluginTypeProviderを介し、ExternalPluginTypeProviderとInternalPluginTypeProviderを設定snapshotで選ぶ。pluginTypeSourceを設定DTOへ追加し、内部はWeb Workerと実行ごとのVFSで処理する。既存9D.6の30秒暫定上限、1万ファイル・100MiB、失敗時の生成物不採用、保存・セッション除外、仮想ソース表示を維持する。照合前のRegistryは空のままとし、未登録候補の実装を勝手に完了扱いしない。現在は外部generatedTypesへの直接呼出しだけなので基盤と方式選択は要実装。外部起動・ディスク書込0回、対象外警告、次回読込適用、自動切替なしを検証する。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/file-actions.ts:75` — `const generated = await tecsgenGateway.generatedTypes(args, result.editable.path, result.optionsFile…`
- `src/shared/ipc-types.ts:126` — `readonly allowEditSystemDefined: boolean;`
- `src/main/tecsgen-runner.ts:151` — `const outputDir = await fs.mkdtemp(join(tmpdir(), "tecscde-plugin-types-"));`

**受入条件**: 対象付表が空でも内部方式を選べ、対象外警告を出して外部実行しないこと。方式変更は次の読込のみ。失敗・上限・Worker停止・仮想表示と保存除外を確認。

参照: [[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、[[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理]]、[[TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案]]。

## 監査61

**空のTECSGEN_COMMANDを起動失敗にせず、既定コマンドへ戻る**

[[TECSCDE-DT外部仕様 - 監査対応 59-69 環境と文書#監査61]]に対応する。

TecsgenRunnerの入口で環境変数の存在をundefinedとの比較で判定し、truthy判定による空文字の黙殺を除く。設定済み値を既存splitCommandで解析し、空のtoken列・空の実行ファイル・閉じない引用符はlaunch-errorへ写像する。公開runは数値の非0終了と同様に例外を漏らす方式へ戻さず、launchFailureを持つ結果を返す。設定サービス経由でも同じ存在判定を共用し、PATH等への暗黙fallbackは行わない。現在のrunは空文字を未設定と同一視するため要実装。未設定・空文字・空白・引用空文字・不正引用・正常な引用パスを分け、誤った既定実行が0回であることを検証する。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/main/tecsgen-runner.ts:122` — `let command = process.env.TECSGEN_COMMAND || "tecsgen";`
- `src/main/tecsgen-runner.ts:124` — `const [executable, ...prefixArgs] = process.env.TECSGEN_COMMAND`
- `src/main/tecsgen-runner.ts:127` — `if (!executable) throw new Error("TECSGEN_COMMAND is empty");`

**受入条件**: undefinedだけが次候補へ進むこと。不正な明示値でexecFileが呼ばれずlaunch-errorになること。Generate/Plugin/版確認の既存severityを確認。

参照: [[TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計]]、[[TECSCDE-DT-EL内部仕様 - 09C tecsgen版の確認]]、[[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理]]。

## 監査62

**コピー用コマンドが、引用符を含むcpp等を正しく引用しない**

[[TECSCDE-DT外部仕様 - 監査対応 59-69 環境と文書#監査62]]に対応する。

buildArgsを実行用の真の引数列として維持し、copy formatterは別の純粋関数に分離する。copy対象シェル、実行コマンドの引用、内部引用符・空引数・改行・シェル特殊文字の表現はTBCとして管理し、未決のまま安全な一行実行を保証しない。既存quoteIfNeededは空白を含む値を二重引用符で囲むだけで、cpp内部の引用符を保持できないためソース修正が必要である。ただし実行APIへescape済み文字列を戻してはならない。シェル契約確定後にround-trip試験を追加し、引用されたWindowsパス、空白を含むcpp、空引数、特殊文字を確認する。実コマンドを実行せず構文解析だけでも引数境界を検証できる。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/tecsgen/command-builder.ts:34` — `` return /\s/.test(arg) ? `"${arg}"` : arg; ``
- `src/renderer/tecsgen/command-builder.ts:50` — `return ["tecsgen", ...TecsgenCommandBuilder.buildArgs(input).map(quoteIfNeeded)].join(" ");`

**受入条件**: コピー先シェル確定まではTBC。確定後は構文解析によるargv一致を試験し、直接実行のbuildArgsに二重escapeが入らないことを確認。

参照: [[TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計]]、[[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理]]。

## 監査63

**アプリ版がpackage.jsonへ一本化されず、ログ先頭行にも版がない**

[[TECSCDE-DT外部仕様 - 監査対応 59-69 環境と文書#監査63]]に対応する。

rendererの版はbuild scriptがpackage.versionからdefineで注入し、vitestにも同じ値を供給する。mainはapp.getVersion()を使用し、LogServiceへ必須のappVersionを渡す。serializerのTECSCDE_TS_VERSION手書き値を除き、CDE_FORMAT_VERSIONは別定数のまま保持する。コミット短縮hashは従来の内部2.5に従い取得不可ならunknownとする。現在のbuild optionsにdefineがなく、保存版は手書き0.1.0、ログheaderも版なしなので要実装である。package版を変えたビルドとテストで、保存CDL・main版・renderer版・ログheaderが一致し、形式版が不用意に変わらないことを確認する。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/model/tool-info-types.ts:18` — `export const TECSCDE_TS_VERSION = "0.1.0";`
- `scripts/build-renderer.mjs:18` — `const options = {`
- `src/main/log-service.ts:55` — `` const header = `# TECSCDE 診断ログ（起動: ${this.startedAt.toISOString()}）\n`; ``

**受入条件**: テスト用package版を注入した出力とserializer/表示/log headerの一致。app版更新でもcde_format_versionは独立維持。既存完了記録と対象checkoutを区別。

参照: [[TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界]]、[[TECSCDE-DT-EL内部仕様 - 09C tecsgen版の確認]]。

## 監査64

**診断ログが指定の固定logs/ではなく、起動cwd優先になる**

[[TECSCDE-DT外部仕様 - 監査対応 59-69 環境と文書#監査64]]に対応する。

mainの設定ディレクトリ解決をログでも共用し、logsDirectory()で固定の絶対ディレクトリを求める。LogServiceはその一つの保存先を受け取り、process.cwd()を候補へ追加しない。ファイル名と遅延作成・追記queueは維持し、作成前にmkdirを行う。固定先の失敗は#66の失敗結果として返し、任意ディレクトリへのfallbackは実装しない。現在のmain/indexはcwdとuserData/logsを候補として渡しており、Windowsでは設定のLocal AppDataとも一致しないため要実装。cwd・起動パス・開くCDLを変えても同じ設定ディレクトリ配下へ出力し、失敗時には他所のファイルを作らないことを検証する。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/main/index.ts:42` — `const logService = new LogService([process.cwd(), join(app.getPath("userData"), "logs")]);`
- `src/main/log-service.ts:57` — `for (const dir of this.dirs) {`
- `src/main/app-settings.ts:37` — `if (process.platform === "win32" && process.env["LOCALAPPDATA"]) {`

**受入条件**: 書込可能なcwdでも固定logsへ出力すること。Windows設定先との一致。固定先を拒否した場合はcwdへfallbackせず、アプリ継続と失敗通知。

参照: [[TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界]]、[[TECSCDE-DT-EL内部仕様 - 09C tecsgen版の確認]]。

## 監査65

**診断ログを新しい30個に制限する処理がない**

[[TECSCDE-DT外部仕様 - 監査対応 59-69 環境と文書#監査65]]に対応する。

mainのLogService初期化または専用初期化処理でpruneOldLogsを一度呼び、固定logsのディレクトリ直下を列挙する。対象名の通常ログファイルだけを抽出し、名前順の新しい30個を除いて削除する。サブディレクトリや対象外名を再帰削除しない。列挙・削除の失敗は処理継続とし、ログ書込失敗の通知規約とは分ける。新規ログは#67の遅延作成契約を維持する。現在のLogServiceは名前の生成と追記のみで保持数制限がないため要実装。0・30・31個以上、対象外ファイル混在、削除拒否、起動時に実ログがない場合を一時ディレクトリで検証し、利用者の実logsを試験で清掃しない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/main/log-service.ts:29` — `this.fileName = logFileName(this.startedAt);`
- `src/main/index.ts:42` — `const logService = new LogService([process.cwd(), join(app.getPath("userData"), "logs")]);`

**受入条件**: 一時ディレクトリで0/30/31件、対象外名・ディレクトリ保持、削除拒否時継続を確認。今回の作業で利用者のログは削除しない。

参照: [[TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界]]、[[TECSCDE-DT-EL内部仕様 - 09C tecsgen版の確認]]。

## 監査66

**ログ書込失敗が、画面の一度限りの警告にならない**

[[TECSCDE-DT外部仕様 - 監査対応 59-69 環境と文書#監査66]]に対応する。

mainのLogService.appendは成功、既通知の失敗、今回初めての失敗を区別できる結果を返し、初回だけnewFailure相当を立てる。shared DTOからIPC・preload・LogGatewayへ同じ結果型を通し、rendererの単一appenderが画面用診断を登録する。DiagnosticsLoggerは当該コードをログ対象から外し、通知のためにappendを再呼出ししない。現在はappendがPromise<void>で失敗をconsoleへ送るだけなので両プロセスのソース修正が必要である。初回作成拒否、成功後の追記拒否、失敗の連続、診断一覧再描画を試験し、通知1回・ログへの当該警告0回・図の状態不変を確認する。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/main/log-service.ts:51` — `` console.error(`ログファイルへ追記できませんでした: ${this.filePath}`, error); ``
- `src/main/log-service.ts:68` — `console.error("ログファイルを作成できませんでした:", this.dirs, lastError);`
- `src/shared/ipc-types.ts:186` — `append(lines: readonly string[]): Promise<void>;`

**受入条件**: 初回/追記失敗と反復で画面通知1回。警告自身をappendへ送らず再帰0回。IPC結果型と図・履歴・dirty非干渉を確認。

参照: [[TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界]]、[[TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計]]。

## 監査67

**診断もtecsgen版記録もない状態で、区切り行だけのログを作り得る**

[[TECSCDE-DT外部仕様 - 監査対応 59-69 環境と文書#監査67]]に対応する。

DiagnosticsLoggerは現在ファイルの区切りを保留状態として持ち、最初の実際の診断行またはtecsgen版行と同じ追記で確定する。LogServiceは実記録があるときだけheaderと本文を作成し、区切りだけの要求を作成契機にしない。版の直接追記も同じ初期化状態と整合させ、headerを二重に書かない。現在はstore.filePathの変更だけで区切りをoutへ積み、非空配列ならmainがファイルを作るため要実装である。診断0・版なし・ファイル切替だけ、最初の診断、版のみ、診断の消滅と再出現を試験し、不要なログ0件と必要時の区切り順を確認する。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/diagnostics-logger.ts:25` — `` if (filePath) out.push(`--- ${filePath} ---`); ``
- `src/renderer/app/diagnostics-logger.ts:33` — `if (out.length > 0) {`
- `src/main/log-service.ts:61` — `await fs.writeFile(candidate, header + text, "utf8");`

**受入条件**: 診断0/版なし/ファイル切替のみでwriteFile0回。版のみ・診断のみではheader1回と正しい区切り。既存の差分追記と保持処理を壊さない。

参照: [[TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界]]、[[TECSCDE-DT-EL内部仕様 - 09C tecsgen版の確認]]。

## 監査68

**複数行メッセージがログの「1行1件」規則を破る**

[[TECSCDE-DT外部仕様 - 監査対応 59-69 環境と文書#監査68]]に対応する。

診断データは原メッセージを保持し、共通formatterがログ・一覧向けの一行表現を作る。本文中のCR/LFとliteralなescape表記が識別できる可逆エスケープを用い、物理改行はLogServiceの行区切りだけとする。ファイルパス・コード・位置を別の診断へ分割せず、UIとログの同じ診断表現を共通化する。現在のfailure-summaryは本文内に改行を生成し、formatDiagnosticとLogServiceはそれをそのまま書くため要実装である。CRLF・LF・CR、文字としてのバックスラッシュ、日本語、複数エラー抜粋で、1診断1物理行、内容保持、一覧との対応、別診断との境界を検証する。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/tecsgen/failure-summary.ts:45` — `` return `${header}:\n${picked.map((line) => `  ${line}`).join("\n")}${omitted}`; ``
- `src/renderer/diagnostics/format.ts:8` — `` return `[${d.code}] ${loc}${d.message}`; ``
- `src/main/log-service.ts:40` — `` const text = `${lines.join("\n")}\n`; ``

**受入条件**: 各改行、literal escape、日本語、複数行失敗概要で内容を保持し1診断1物理行。表示とログで同じ一行formatterを使い、raw診断値は変更しない。

参照: [[TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界]]、[[TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計]]、[[TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計]]。

## 監査69

**このワークスペースにユーザーズ／リファレンスマニュアル成果物が揃っていない**

[[TECSCDE-DT外部仕様 - 監査対応 59-69 環境と文書#監査69]]に対応する。

内部1.6とV02-11を文書成果物の契約として維持し、ユーザーズは起動・読込・配置・結合・保存・情報設定、リファレンスは操作・設定キーの優先順位・ファイル書式・診断・制約を扱う。実装後の画面と受入確認へ照合し、既存READMEから案内できるようにする。現workspaceのdocsは設計文書と図だけで、二つのマニュアルは未整備である。ただしこの不足の解消自体は文書の執筆・編集・公開範囲の作業であり、アプリの実行ソース修正は不要と判定する。後の成果物検証ではリンク切れ、手順と実画面の一致、未実装を利用可能と書いていないことを確認する。

**実装要否**: ソースコードの修正は不要です。 文書成果物の整備が必要ですが、アプリ実行コードの変更は要りません。

**現行コード根拠（5cf2d85）**:

- `README.md:7` — `- 開発ドキュメント（Markdown形式ファイル）を、開発の記録として、以下で公開しています。`
- `README.md:100` — `## CDL の読み込みと保存`
- `README.md:128` — `` 診断パネルに表示される内容は、`tecscde-log-YYYYMMDD-HHMMSS.txt` にも追記されます。カレントディレクトリを優先し、書き込めない場合は他のディレクトリにフォールバックしま… ``

**受入条件**: 今回は本文を作成せず、外部1.6/内部1.6/V02-11の対応と未整備状態を確認。後日作成時にREADME導線・リンク・画面手順を照合。外部サイト/別checkoutの文書は未確認。

参照: [[TECSCDE-DT-EL内部仕様 - 01 概要]]、[[TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案]]。

## Related

- [[TECSCDE-DT-EL内部仕様]]
- [[TECSCDE-DT外部仕様 - 監査対応 59-69 環境と文書]]

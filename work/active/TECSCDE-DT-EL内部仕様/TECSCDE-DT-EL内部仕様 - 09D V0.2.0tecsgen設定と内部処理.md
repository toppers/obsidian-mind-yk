---
date: 2026-11-06
description: "V0.2.0のtecsgenパス解決・設定保存・即時反映・版診断更新と、メモリ内仮想ファイル・プラグイン相当処理の境界設計。"
project: TECS
quarter: Q4-2026
status: proposed
tags: [work-note, tecs, tecscde, spec, architecture]
---

# 9D. V0.2.0 tecsgen設定と内部処理

[[TECSCDE-DT-EL内部仕様]]第9章・第9C章の追加設計です。根拠は[[TECSCDE-DT外部仕様 - 02 動作環境]]2.5、[[TECSCDE-DT外部仕様 - 03 画面構成]]3.8.1、[[TECSCDE-DT外部仕様 - 08 CDL 連携]]8.4.3・8.5、[[TECSCDE-DT外部仕様 - 09 エラーと警告]]9.4.xです。新しい識別子は内部設計案であり、実装済みを意味しません。

## 9D.1 プロセス配置

| 処理 | 所有先 |
|---|---|
| 設定表示・入力・確認結果 | rendererの情報ダイアログ |
| 設定ファイルの読み書き | mainの既存`app-settings.ts`を拡張 |
| 環境変数・実在確認・PATH探索 | mainの`TecsgenPathResolver`（案） |
| 外部コマンド実行・版取得 | mainの既存`TecsgenRunner` |
| 版の解釈・診断の表示 | 9Cの既存renderer処理を拡張 |

`shared/ipc-types.ts`にDTOとAPIを定め、mainのIPC、preloadの`contextBridge`、rendererのゲートウェイを経由します。rendererから環境変数やOSへ直接アクセスしません。

## 9D.2 パス解決

実行設定は次の優先順位で解決します。

1. 環境変数`TECSGEN_COMMAND`。従来の起動コマンドとして扱い、引数を含み得る値を`tecsgenPath`へ転記しません。
2. `settings.json`の`tecsgenPath`。設定済みならこれを使い、ファイルが消えていても別のtecsgenへ黙って切り替えません。起動失敗は既存のエラー経路へ渡します。
3. 未設定なら`TECSPATH`の値が実在するか調べ、実在すればtecsgenへのパスに採用します。
4. それでも決まらなければ`PATH`をOSの区切りで分け、先頭のディレクトリからOSに応じた実行ファイルを探します。Windowsの拡張子一覧と候補内の優先順はTBCです。

自動探索で見つかった値は`tecsgenPath`として保存します。見つからなければ未設定のままとし、情報ダイアログへ未検出の状態を返します。`TECSGEN_COMMAND`による上書きがあっても保存値は保持し、その値が使われないことを表示します。

外部仕様は`TECSPATH`の「値が実在する」ことを条件にしています。その値がディレクトリだった場合の実行ファイルへの変換や`.rb`の起動方法は未規定です。既存の`TECSGEN_COMMAND`対応から推測して自動変換を追加せず、実装前のTBCとします。`tecsgenPath`はコマンド文字列ではなくパスとして扱い、引用符や空白をシェルへ連結して実行しません。

## 9D.3 設定の保存と即時反映

既存の設定オブジェクトに`tecsgenPath?: string`、`cdlFilesRoot?: string`、`pluginTypeSource?: 'external' | 'internal'`（既定`external`。9D.6）を追加します。Windowsの保存先は`%LOCALAPPDATA%/tecscde-dt-el/settings.json`、それ以外は既存のElectron `userData`方針とし、OS別の具体パスは外部仕様のTBCを維持します。設定保存時は現在のJSONへ変更項目だけをマージし、未知項目、`fileBrowserRoot`、`lastSession`等を保持します。設定なし・不正JSONは既存の既定値読み込みに従います。

- 確認が失敗したパスも保存可能とします。型の妥当性と実行可能性を混同しません。
- 空にして保存した場合は`tecsgenPath`を解除します。保存後の版再確認は次の設定解決に当たるため、そこでTECSPATH・PATHから再探索し、見つかれば自動検出値を保存します。ダイアログには再探索後の有効値を表示し、未設定を維持する操作とは扱いません。
- 保存成功後、mainの実行設定を更新し、以後開始するGenerate・版確認・Plugin型取り込みで同じ解決結果を使います。既に起動した処理のコマンドは途中で変えません。
- `TECSGEN_COMMAND`、`TECSPATH`、`PATH`そのものは変更しません。外部で変えた環境変数はアプリ再起動後に反映されます。
- 設定変更によって開いているCDLを勝手に読み直しません。保存されたパスと実際に優先されるコマンドの区別をダイアログへ返します。

## 9D.4 版確認と診断更新

起動時の非同期確認に加え、設定を保存したときにも実行設定を解決し直して版を確認します。候補の「確認」ボタンでは入力中の候補だけを検査し、その結果を保存済み設定の環境診断と混ぜません。標準出力／標準エラー出力の扱い、版の比較、古い版・不明の診断は9Cを再利用します。

再確認には世代番号または実行設定のrevisionを付けます。設定Aの確認中にBへ変更された場合、遅れて到着したAの結果を捨て、現在の設定の結果だけを反映します。

`environmentDiagnostics`のうちtecsgenの版・検出に属する診断を一群として差し替えます。外部仕様9.4.xに従い、古い設定に対する`E-TECSGEN-NOT-FOUND`等も現在の一覧から除きます。一般のCDL診断や別のツールの診断まで全消去しません。過去のログファイルを消すという意味ではありません。

新しい結果が対象以上なら旧警告は消え、古い版・不明なら新しい警告へ置き換えます。未検出時に起動直後から不要な警告を出さない9Cの方針は保持します。設定欄の未検出表示と、Generate等の必要時のエラーを区別します。`E-TECSGEN-NOT-FOUND`の案内には「情報」からの設定を加えます。

## 9D.5 設定IPC契約案

| API案 | チャネル案 | 役割 |
|---|---|---|
| `settings.getToolSettings()` | `settings:getToolSettings` | 保存パス・有効な起動元・TECSPATH・一覧対象ディレクトリ・Plugin生成型の取り込み方式を取得 |
| `settings.updateToolSettings(patch)` | `settings:updateToolSettings` | パス／対象ディレクトリ／取り込み方式を部分更新し、有効設定とrevisionを返す |
| `settings.chooseTecsgenPath()` | `settings:chooseTecsgenPath` | ネイティブファイル選択、キャンセル可 |
| `tecsgen.checkPath(path)` | `tecsgen:checkPath` | 未保存候補の版確認。設定は変更しない |
| `tecsgen.version()` | 既存`tecsgen:version` | 現在有効な設定で版確認 |

DTOはstructured clone可能な値に限定し、`PATH`全体は返しません。設定更新は書き込み成功／失敗を判別できる結果型にします。mainでも入力型と項目を検査し、任意の環境変数や任意の設定キーを書き換える汎用APIにはしません。既存インタフェースとの統合時はこの責務を維持し、重複APIを作らないよう調整します。

## 9D.6 tecsgen相当のメモリ内処理

外部プロセス実行とは別の経路として、`VirtualFileSystem`と`InternalTecsgenProcessor`（いずれも案）を置きます。ここで確定するのは、処理入力と生成物の受け渡しがメモリ内で完結し、対象処理でtecsgenを起動せず、ディスクへの入力CDL・生成物の書き出しを行わない境界です。既存の外部実行・一時ディレクトリ方式に単に別名を付けたものにはしません。

```ts
interface VirtualFileSystem {
  read(path: string): string | undefined;
  write(path: string, text: string): void;
  list(): readonly string[];
}
// 契約の骨格案。対象プラグイン決定後にOptions/Resultを具体化する。
// InternalTecsgenProcessor.process(inputs, options)
//   → 仮想生成物と診断（すべてメモリ上）
```

CDLの入力はアプリが保持するソース群のスナップショットとして渡します。プラグイン相当処理は仮想ファイルAPIのみを受け取り、`fs`や外部プロセスへ依存しない計算として分離する案です。仮想パスの正規化、重複名、再実行時の生成物の寿命を明示し、失敗時に前回の生成物と今回の生成物を混ぜません。

生成CDLから型を構築する場合は既存のパーサ／ビルダーの入口へ接続します。仮想パスを実在する定義ファイルのフルパスとして表示せず、生成物を利用者の保存元・セッション参照へ混入させません。

### 内部処理の設計（2026-11-08 決定）

外部仕様8.5で決定された併用方式（置き換えではない）、対象プラグイン、仮想内容の表示の内部設計は次のとおりです。

1. **構成**: `PluginTypeProvider`インタフェースを置き、`ExternalPluginTypeProvider`（既存の`TecsgenGateway.generatedTypes`）と`InternalPluginTypeProvider`の2つを実装します。`file-actions.ts`の呼び出し側は、設定で選ばれた実装を使うだけにします（重複した経路を作りません）。
2. **設定**: `pluginTypeSource: 'external' | 'internal'`（既定`external`）を9D.3の`settings.json`と9D.5の`getToolSettings`・`updateToolSettings`に含めます。保存した直後に有効な設定を更新し、次の読み込みから使います。開いているCDLを勝手に読み直しません。
3. **処理**: `InternalTecsgenProcessor.process(inputs, { enabledPlugins })`は、`fs`と外部プロセスに依存しない純粋な計算です。rendererのWeb Workerで実行し、`VirtualFileSystem`だけを入出力にします。
   - `PluginRegistry`（名前 → ハンドラ）に、外部仕様8.5の付表に載ったプラグインだけを登録します。照合ができるまで、登録は空です。
   - ソースから`generate(...)`を抽出し、登録のないプラグインは`W-PLUGIN-UNSUPPORTED`にします。
4. **仮想パス**: `plugin:/<プラグイン名>/<ファイル名>.cdl`に正規化します。重複名は、8.1の規則（結合と属性の多い方）で採ります。
5. **寿命**: 実行ごとに新しい`VirtualFileSystem`を作ります。成功すれば、以前の生成物と入れ替えます。失敗すれば、新旧どちらの生成物も取り込みません（混ぜない）。
6. **上限**: ファイル数と合計サイズは8.1と同じ上限（10,000ファイル、100MiB）とします。処理時間は上限（暫定30秒）を設け、超えたらWorkerを終了して失敗（`W-PLUGIN-TYPE-LOAD`）にします。
7. **フォールバックの禁止**: 内部処理の失敗から外部実行へ、または外部実行の失敗から内部処理へ、自動で切り替えません。どちらを使ったかは診断ログに記録します。
8. **仮想内容の表示**: 生成された型の定義ファイルは、仮想パスを`TypeDefinitionSource`に持たせ、定義ファイルウィンドウが読み取り専用で`VirtualFileSystem`の内容を表示します。実在するパスの扱い（コピー・保存）を仮想パスには適用しません。生成物を保存元・セッション参照へ混入させません。
9. **同一性**: 内部処理の生成物は、外部tecsgenの記録済みの出力との照合（ゴールデン照合）で一致したものだけを、付表の登録対象にします。基準データは`tests/fixtures/tecsgen-golden/sample1-mruby-bridge/`（tecsgen 1.9.1、CDL 55ファイル。採取条件はREADME）です。外部は2回の実行で全件が一致する決定的な出力で、照合は両者の改行をLFに正規化して行います（基準データはWindowsのCRLF）。
10. **MrubyBridge系の登録条件**（2026-11-08の調査）: 署名の関数引数の構造体からセルタイプ名を導くため、C型（`import_C`のtypedef・struct）の解決が必要です。初期化セルの並びは`generate(...)`の処理順に依存し、生成物の中の`generate(...)`が別のプラグインを呼ぶ多段の連鎖も再現する必要があります。これらを満たして基準データと一致するまで、`PluginRegistry`への登録は空とします。`HRP2*Plugin`系はCDLを生成しない（全て0バイト）ため、対象外です。

## 9D.7 実装時の受入確認

- 優先順位4段階、探索順、空入力解除、未検出、空白入りのパス、未知設定項目保持、保存失敗をmainのテストで確認します。Windows拡張子等はTBC確定後に試験値を追加します。
- 保存直後に次の実行へ反映され、`TECSGEN_COMMAND`優先時の表示が一致します。候補の確認は保存済み設定を変えません。
- 版確認が逆順で完了しても最新だけを採用し、旧版・不明から正常に変えた場合は古い診断だけが消えます。
- 内部処理（2026-11-08追加）: 外部プロセス呼び出しとディスク書き込みが0回であること。対象プラグインの生成物が、外部tecsgenの記録済みの出力と一致すること（ゴールデン照合）。対象外のプラグインで`W-PLUGIN-UNSUPPORTED`になること。失敗時に新旧の生成物が混ざらないこと。上限と時間切れで失敗すること。方式の切り替えが次の読み込みから反映され、開いているCDLを読み直さないこと。内部処理から外部実行へ（または逆に）自動で切り替わらないこと。仮想内容が定義ファイルウィンドウに読み取り専用で表示されること。対象プラグインの期待値は、付表が確定してから用意します。
- テストは`tests/main/`・`tests/renderer/`、実機の設定・版確認記録は`tests/verification/`に置きます。

## Related

- [[TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計]]
- [[TECSCDE-DT-EL内部仕様 - 09C tecsgen版の確認]]
- [[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]
- [[TECSCDE-DT-EL内部仕様 - 07G V0.2.0CDLファイル一覧生成]]
- [[TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案]]

- [[TECSCDE-DT-EL内部仕様 - 監査対応 59-69 環境と文書]] — 該当する監査項目の契約補足（2026-11-09）。

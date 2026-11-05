---
date: 2026-10-22
description: "TECSCDE-DT-EL内部仕様書 第9章9.8節（tecsgenの版の確認）の詳細設計 — 起動時に tecsgen --version で版を読み、V1.3.1.0 より古い・読めない場合に警告する。stdout が空で版が stderr に出る点への対応を含む"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note split from [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様 第9章]]（2026-10-22、09が25KBに近いため別ノートにした）。外部仕様は[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|DT外部仕様8.4.2節]]（2026-10-22決定）。2026-10-22に実装済み（自動表示を含む）。実機での警告表示の確認は未了。

## 9C. tecsgenの版の確認

### 9C.1 経緯

外部仕様8.4.2は「`tecsgen --version`で版を確認できる」としていたが、従来の実装は`TecsgenRunner.version()`が定義されているだけで、呼び出し元が無かった（[[TECSCDE-DT-EL実装 — 外部仕様と内部仕様・実装の差分一覧|差分一覧]]#7）。さらに`version()`は標準出力だけを返すが、tecsgen-rb 1.9.1を`--version`で実行すると、標準出力は空で、`tecsgen  version 1.9.1`が**標準エラー出力**に出た（終了コード0、2026-10-22に実測。Electronからの実行は未確認）。そのため従来の実装のままでは、版が取れない。

### 9C.2 取得（main）

```ts
// shared/ipc-types.ts
type TecsgenVersionResult =
  | { readonly kind: 'ok'; readonly text: string }          // 標準出力、空なら標準エラー出力（trim）。空文字もありうる
  | { readonly kind: 'not-found' }                          // ENOENT（実行ファイルが無い）
  | { readonly kind: 'failed'; readonly detail: string };   // ENOENT以外の起動失敗、または非0終了

// main/tecsgen-runner.ts
async version(): Promise<TecsgenVersionResult> {
  const r = await this.run(['--version']);                  // 30秒タイムアウトのまま（9.7節）
  if (r.launchFailure?.kind === 'not-found') return { kind: 'not-found' };
  if (r.launchFailure) return { kind: 'failed', detail: describeLaunchFailure(r.launchFailure) };
  if (r.exitCode !== 0) return { kind: 'failed', detail: `終了コード ${r.exitCode}` };
  return { kind: 'ok', text: (r.stdout.trim() || r.stderr.trim()) };
}
```

IPC `tecsgen:version`と`TecscdeApi.tecsgen.version`の戻り値の型を`Promise<TecsgenVersionResult>`に改める（従来は`Promise<string | null>`）。

### 9C.3 解釈と比較（renderer、`app/tecsgen-version.ts`新設）

```ts
const MIN_TECSGEN_VERSION = [1, 3, 1, 0] as const;   // 外部仕様2.2節（DT外部仕様2章）。定義はここ1か所

/** "tecsgen  version 1.9.1" → [1,9,1]。読めなければ undefined。 */
function parseTecsgenVersion(text: string): readonly number[] | undefined;
/** 数値の列として辞書式に比べる。足りない桁は0（1.9.1 は 1.9.1.0 と同じ）。 */
function compareVersions(a: readonly number[], b: readonly number[]): number;
```

- 抽出: まず`/version\s+v?(\d+(?:\.\d+)*)/i`、無ければ文字列中で最初の「数字.数字…」の並び。どちらも無ければ`undefined`。
- 比較は数値で行う（`1.10`は`1.9`より新しい）。

### 9C.4 診断

| 条件 | コード | severity | 文言 |
|---|---|---|---|
| 版が`MIN_TECSGEN_VERSION`より古い | `W-TECSGEN-VERSION-OLD` | warning | 「tecsgen の版 {版} は、本アプリが対象とする V1.3.1.0 以降より古いため、CDL を正しく扱えない場合があります。」 |
| `kind: 'ok'`だが版を読めない、または`kind: 'failed'` | `W-TECSGEN-VERSION-UNKNOWN` | warning | 「tecsgen の版を確認できませんでした（{理由}）。」 |
| `kind: 'not-found'` | なし | — | 見つからない場合は、「実行(Generate)」やPlugin型の取り込みで必要になったときにエラー・警告として出る（9.7節）。起動時に毎回出すと、tecsgenを使わない利用者に不要な警告になる |
| 対象以上 | なし | — | 版は診断ログに1行記録する（`tecsgen version: 1.9.1`） |

警告は位置を持たない。

### 9C.5 時機と保持

- **一覧の自動表示**（2026-10-22決定）: 警告を保持したら、診断パネルを自動で開く（ステータスバーの件数だけでは、起動直後に気づきにくいため。「実行(Generate)」の後に開く扱いと同じ）。`AppShell.openDiagnostics()`を公開し、`checkTecsgenVersion`の`onWarning`コールバックから呼ぶ。診断が出ないとき（見つからない、対象以上）は開かない。
- **時機**: 起動時に1回。`shell.start()`の後に非同期で実行し、UIをブロックしない（起動ドキュメントの読み込みとは独立）。再確認はしない。
- **保持**: `AppStore`に`environmentDiagnostics`を新設し、`setEnvironmentDiagnostics`で設定する。`getReport()`は既存の3種（ロード時、整合性チェック、tecsgen実行結果）に加えて、これも集約する。**`loadDocument`でも、Generateの結果の差し替え（`setTecsgenDiagnostics`）でも消えない**（既存の`tecsgenDiagnostics`はそのたびに入れ替わるため、同じ場所に積むと消えてしまう）。
- **ログ**: 診断ログは`DiagnosticsLogger`が診断パネルの内容を書くので、警告は自動で残る。版の取得に成功したときの1行は、起動処理から`LogGateway.append`で直接書く。

```ts
// renderer/app/tecsgen-version.ts
export async function checkTecsgenVersion(
  store: AppStore, tecsgen: Pick<TecsgenGateway, 'version'>, log: Pick<LogGateway, 'append'>,
  onWarning?: () => void,   // 警告を保持した直後に呼ぶ（診断パネルを開く）
): Promise<void>;
// renderer/main.ts: shell.start() の後で
//   void checkTecsgenVersion(store, tecsgen, new LogGateway(), () => shell.openDiagnostics());
```

### 9C.6 外部仕様との関係と論点

- 外部仕様8.4.2の規定（起動時1回、古い・読めない場合に警告、見つからない場合は出さない、実行中保持、診断ログへ記録）を、そのまま実装する設計。
- **新しい版の扱い**: 対象より新しい版では警告しない。上限は設けない（外部仕様2.2節の対象は「V1.3.1.0以降」）。
- **`TECSGEN_COMMAND`**: 版の確認も、`TECSGEN_COMMAND`で指定されたコマンドを使う（`run`が共通のため）。
- **論点（要確認）**: tecsgen-python3の`--version`の出力形式（Ruby版との一致はP6bで確認済みと記録されているが、出力先が標準エラー出力かどうかはこのノートでは確かめていない）。

### 9C.7 テスト（実装時）

- `TecsgenRunner.version`: 標準出力のみ／標準エラー出力のみ／両方空／`ENOENT`／権限なし／非0終了。
- `parseTecsgenVersion`: `tecsgen  version 1.9.1  `、`V1.3.1.0`、`1.10`、数字なし。
- `compareVersions`: `1.10 > 1.9`、`1.9.1 == 1.9.1.0`、`1.3.0.9 < 1.3.1.0`。
- `checkTecsgenVersion`: 古い→`W-TECSGEN-VERSION-OLD`、読めない→`W-TECSGEN-VERSION-UNKNOWN`、`not-found`と対象以上→診断なし、`loadDocument`／Generate後も残る。警告を保持したときだけ`onWarning`を呼ぶ。
- `AppShell.openDiagnostics()`: 環境診断があるとき、呼ぶと診断パネルが開く（通知だけでは開かない）。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様 第9章]] — 9.1節（`TecsgenRunner`）、9.3節（`TecsgenGateway`）、9.7節（起動失敗）
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様 第8章（8.4.2節）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計|TECSCDE-DT-EL内部仕様 第8章（診断コード）]]
- [[TECSCDE-DT-EL実装 — 外部仕様と内部仕様・実装の差分一覧]] — #7
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

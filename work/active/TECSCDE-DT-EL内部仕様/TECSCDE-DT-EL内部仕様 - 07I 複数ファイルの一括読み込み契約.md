---
date: 2026-11-07
description: "監査#16の内部設計。主ファイルの役割とソースの読み込み順を分離し、複数ファイルの要求・結果DTO、起動とUIの共通経路、一括適用を統一する。"
project: TECS
quarter: Q4-2026
status: active
tags: [work-note, tecs, tecscde, spec, architecture]
---

# 7I. 複数ファイルの一括読み込み契約

[[TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合]]7.7.4に残る「説明では主ファイルから開くが、コードでは追加ファイルから開く」という不一致を解消します。以下の振る舞いは確定契約です。API・補助関数の名称は案ですが、役割・順序を分離する規則を任意にするものではありません。2026-11-09の三者監査#5でも現行`5cf2d85`は未対応と確認しており、`status: active`は仕様の有効性だけを表します。外部規定は[[TECSCDE-DT外部仕様 - 05A 開く（読み込み）]]5.3のオプションファイル内の列挙順と主ファイルの選択です。

## 7I.0 現行コードとの対応（2026-11-09、三者監査#5）

| 境界 | 確定契約 | 現行`5cf2d85` |
|---|---|---|
| main・IPC | 役割と順序を持つ要求DTOを受け取り、その順で本文を返す | `FileService.openPaths(paths)`／`readPaths`が配列末尾を主とする |
| renderer | `sourceOrder`を保って解決・構築し、主キーを明示 | `applyOpenResult`がreferences→editableの順に配列を組む |
| ローダー | `primarySourceKey`で主役を決め、編集可否から推定しない | `loadSources`が最後のeditableソースを主とする |
| ストア・セッション | 主・参照集合と通常ソース全体の順序を同時に保持 | `sourceOrder`の保持・保存がない |
| 非同期結果の仲裁 | 7I.7の要求世代・文書世代・変更revisionで適用を検査 | `file-actions.ts`に世代・revision検査なし。未反映（三者監査#6） |

この差は仕様の修正だけでは解消しません。main・shared／preload／gateway・renderer・ローダー・セッションを同じ契約へ変更する実装が必要です。

## 7I.1 主ファイルと読み込み順

**読み込み順と主ファイルの役割を別の値として渡します。** 配列の逆転や、先頭／末尾というAPI内部の暗黙の位置から主ファイルを決めません。

1. `.tecsgen-opts`から得たCDLパスは、オプションファイルのディレクトリを基点に絶対パス化します。
2. **元の列挙の最後のCDLを`primaryPath`にします。** パスの重複排除より先に役割を確定します。
3. `sourceOrder`は、元の列挙順から同一の正規化済みパスの重複だけを除き、最初の出現順を保持します。主ファイルのために先頭や末尾へ移しません。
4. `referencePaths`は`sourceOrder`から`primaryPath`だけを除いたものです。これは編集不可という意味ではなく、主ファイル以外の役割です。

例えば`A.cdl B.cdl C.cdl`なら、`sourceOrder=[A,B,C]`、`primaryPath=C`、`referencePaths=[A,B]`です。`A.cdl B.cdl A.cdl`なら、`sourceOrder=[A,B]`、`primaryPath=A`、`referencePaths=[B]`です。同名セルの先勝ち等を、主ファイルを移動する配列操作で変えません。

この重複除去を`extraImportPaths`へ流用しません。`-I`・`-S`は原文の順序と重複を保持し、相対値の基点は`optionsFilePath`の親ディレクトリです。

## 7I.2 明示的な一括I/O契約

```ts
// shared/ipc-types.ts：値のみ。mainのFileServiceとrendererのFileGatewayで共用。
interface OpenPathsRequest {
  readonly sourceOrder: readonly string[];
  readonly primaryPath: string | null; // nullは主ファイルなしのセッション復元用
  readonly referencePaths: readonly string[];
  readonly optionsFilePath?: string;
  readonly extraImportPaths: readonly string[];
  readonly systemDirs: readonly string[];
}
interface OpenPathsBatch extends OpenPathsRequest {
  readonly files: readonly OpenFileEntry[]; // sourceOrderと同じ順の読込済みテキスト
}
type OpenPathsResult =
  | { readonly kind: 'ok'; readonly batch: OpenPathsBatch }
  | { readonly kind: 'failed'; readonly path: string; readonly detail: string };

// renderer: FileGateway.openPaths(request)
// preload: window.tecscde.file.openPaths(request)
// main: IPC file:openPaths → FileService.openPaths(request)
// すべて同じ要求・結果型、Promise<OpenPathsResult>を使う。
```

mainでも、パスが正規化済みで重複がないこと、主ファイルがあれば集合内に存在すること、`referencePaths`が`sourceOrder`から主ファイルを除いた列と一致することを検証します。主ファイルありの要求で空の`sourceOrder`は拒否します。主ファイルなしの復元は`primaryPath: null`を明示し、追加CDLだけ、または全項目が空のセッションも表現できます。矛盾した要求を配列の並べ替えで黙って補正しません。`systemDirs`は既存のオプション解析で絶対パス化した値を渡します。

I/Oは全ファイルを読み終えるまで成功結果を返しません。並列に読む場合も、完了順でなく`sourceOrder`順に結果を並べます。明示ファイルの1件でも読めなければ`failed`とし、途中結果をストアへ適用しません。通常のimport先未解決は、後段の既存の警告処理と区別します。

## 7I.3 ローダーとストアへの適用

`OpenPathsRequest.primaryPath`と`primarySourceKey`は、同じ正規化済み定義元パスを境界ごとに表す値です。`files`をbasenameで対応付けず、各`OpenFileEntry.path`から一意に対応付けます。主役のために本文配列を並べ替えません。

```ts
// 既存LoadOptionsのcdeclResults・systemDirs等は維持し、この項目を追加する。
interface LoadOptions {
  readonly primarySourceKey?: string | null;
}
```

rendererは`batch.files`を`sourceOrder`順に既存の参照解決・型解決・モデル構築へ渡します。import追跡による重複・循環抑止と追加順序は既存の7D・7Eの規則を使い、明示ソースの相対的な順序を逆転させません。

解決後は、importで追加した通常CDLも含めて実際の解析順と参照集合を確定します。ストア・セッションへ渡す`sourceOrder`は、この解決後の通常ソース全体の順序とし、Plugin生成ソースを除きます。入力batchは書き換えず、解決後の結果へ拡張された順序・参照集合を持たせます。

`CdlDocumentLoader.loadSources()`のオプションに`primarySourceKey`（案）を追加し、一括読み込みでは`batch.primaryPath`のソースキーを必ず渡します。主ファイルの採用とその`preservedImports`・テンプレートの選択は、この明示値に従います。`editable`な最後のソースを主ファイルとする従来の推定を、この経路で使いません。読み取り専用の主ファイルも役割として保持し、編集可否は別の判定とします。単一ファイルを開く経路も、明示的な主ファイルを渡します。

旧来の簡便な`loadSources`呼び出しで`primarySourceKey`を省略する場合の互換は維持できますが、複数ファイルを開くUI・起動・復元経路からは省略しません。用紙の採用元は4Dと外部05Bの5.3.x項目8で決定済みであり、主ファイル指定とは別に、対象通常CDLを開いた順で最初の有効な宣言から決めます。主役のための並べ替えを用紙決定へ持ち込みません。

主ファイルなしの復元では`primarySourceKey: null`を明示します。これは省略時の旧推定とは異なり、追加CDLを勝手に主ファイルへ昇格させません。空の主文書と参照集合を組み立て、全項目が空なら空文書を返します。 この空成功batchは7H.0の有効セッション復元であり、bootstrapの失敗nullやsamplesへのfallbackに変換しません。オプションファイル内のCDL 0件は7I.4の入口で拒否するため、空セッション復元と混同しません。

明示された文字列キーに一致する通常ソースがない、またはPlugin生成ソースを主に指定した場合は構築失敗とし、別ソースを主へ代替して適用しません。`undefined`の旧推定互換は、明示的な役割を持たない旧補助呼び出しだけです。UI・起動・復元・`loadSingle`では文字列か`null`を渡します。

主の`preservedImports`や主文書の元情報は、編集可否と独立して指定ソースから取得します。保存用テンプレートはeditableかつ非generatedに限るため、読み取り専用主では主の保存用テンプレートがなくても正常です。その場合に別のeditableソースのテンプレートやimportsを代用しません。`null`の空主文書にも参照の元情報を流用しません。各ソースのレイアウト等と、4Dの用紙採用元はそれぞれの契約で保持します。

`optionsFilePath`・`extraImportPaths`・`systemDirs`を読み込みコンテキストとして、import解決より前に渡します。ただしライブストアへ先に設定せず、処理中のローカル値として使います。全解決・モデル構築に成功したあと、**図、主ファイル、追加ファイル、関連設定を一度だけストアへ適用**します。`addAsReference()`と`openFromPath()`を組み合わせ、同じ図を逐次置換する実装にはしません。

## 7I.4 ファイルブラウザと起動の共通手順

ファイルブラウザでオプションファイルを開く概略は次のとおりです。補助関数と依存注入の詳細は実装時に既存の`file-actions`へ統合します。

```ts
async function loadOptionsFile(store, gateway, path): Promise<void> {
  const guard = beginOpenRequest(store); // 最初のawait前に3値を固定（7I.7）
  let committed;
  try {
    const parsed = await gateway.parseTecsgenOptionsFile(path);
    if (!await waitForReadTurn(store, guard)) return;
    const request = makeOpenPathsRequest(parsed, path); // CDL 0件ならnull
    if (!request) {
      await publishReadOutcomeWhenAllowed(store, guard, { kind: 'no-cdl' });
      return;
    }
    if (store.isDirty()) {
      const proceed = await gateway.confirmDiscardChanges();
      if (!await waitForReadTurn(store, guard) || !proceed) return;
    }
    const result = await gateway.openPaths(request);
    if (!await waitForReadTurn(store, guard)) return;
    if (result.kind !== 'ok') {
      await publishReadOutcomeWhenAllowed(store, guard, result);
      return;
    }
    const next = await resolveAndBuildOpenBatch(result.batch);
    // close中だけなら保留。再開後に同期で再照合・適用・session登録
    committed = await commitOpenWhenAllowed(store, gateway, guard, next);
  } catch (error) {
    await publishReadOutcomeWhenAllowed(store, guard, { kind: 'failed', error });
  } finally {
    finishOpenRequestIfOwner(store, guard.requestGeneration);
  }
  if (committed) await settleCommittedSession(committed); // 採用後の別の照合
}
```

未保存確認は一括処理の前に1回だけ行い、個々のCDLごとには行いません。CDLが0件なら現在の図とセッションを保持し、その旨を通知します。解析・読込・構築の失敗、キャンセルでも現在の図を空にしません。実装では例外経路も既存の読込失敗通知に接続します。

要求世代だけでなく、文書世代と変更revisionも**最初のawait前**に固定します。確認後に取り直す旧例は採用しません。解析・確認・I/O・解決の各await後、失敗通知前、適用直前の検査は7I.7へ統一します。破棄した結果からストア・セッションを更新しません。採用後のセッション保存失敗は、読込失敗と区別して固定したcommit結果で扱います。

起動時も同じ要求作成・一括I/O・解決用コンテキストを使います。mainが一括結果を`app:bootstrap`へ載せ、rendererは同じ主ファイル指定と順序で構築・適用します。監査#5の「CLIから最初の対象ファイル1件を選ぶ」は入口の規則として維持し、選ばれた1件がoptsの場合だけ、その内部のCDL列挙へこの一括処理を使います。

## 7I.5 セッションとの接続

OS関連付けの複数入力は[[TECSCDE-DT-EL内部仕様 - 07K 関連付け入力の収集と一括オープン|7K]]の境界付き要求から変換する（2026-11-08、監査#22）。CLIの先頭1件とは分け、関連付けのパス配列全体を保持して本節の一括処理へ渡す。受信・収集・待機と読み込み開始を区別し、キューから確定要求を開始するときに7I.4の要求世代を発行する。

[[TECSCDE-DT-EL内部仕様 - 07H セッション保存と復元|7H]]の4項目に加え、`sourceOrder`を読み込み順の補助情報として保存します。主ファイル・参照集合だけから元の列挙順を復元すると、上記の`A,B,A`のような場合に順序が変わるためです。ストアの一括適用後に一度だけ保存し、中間状態を書きません。

セッション復元では保存済みの主ファイル・参照集合を正とし、保存済み順序を同じ集合に対して適用します。 新規のスナップショットには`sourceOrder`を必ず含めます。省略を認めるのは7Hの旧設定読み取り互換だけです。指定済み順序の重複・集合不一致を、主ファイル末尾への移動や別の順序へのフォールバックで補正しません。オプションファイルの再解析で保存済みファイル集合を置き換えません。探索パスの再解析優先・保存値へのフォールバックと、Generate時の毎回再解析は7Hの規則を維持します。

## 7I.6 実装時の検証条件

- A・B・CではCを主ファイル、参照をA・B、解析順をA・B・Cとする。A・B・AではAを主ファイル、参照をB、解析順をA・Bとする。
- 重複した正規化済みパスは一度だけ読み、同名セルの先勝ちが主ファイルのための並べ替えで変わらないことを確認する。
- 未保存確認のキャンセル、CDL 0件、任意の明示ファイルの読込失敗、構築失敗、読み込み中の新規編集で旧ストアとセッションを保持する。
- 通常成功時は図と関連メタデータを1回だけ適用・保存し、最初に追加CDLを公開してから主ファイルを開く中間状態がない。
- 古い要求Aがオプション解析待ちの間に新しい要求Bが完了した場合も、後から完了したAを適用・保存しない。未保存確認待ち・I/O待ち・解決待ちの競合も同じ条件で確認する。
- 起動・ファイルブラウザ・復元で、同じ一括要求から同じ順序・役割・import基点を得る。CLIの先頭1件選択は維持する。
- `-I`・`-S`の順序と重複、`systemDirs`、別ソースの編集可否を維持する。
- 保存した`sourceOrder`を復元し、旧設定に順序がない場合の7Hの互換規則も確認する。
- 読取完了順が逆転しても解析順を維持し、同じbasenameの別パスを混同しない。
- 読み取り専用主、文字列キー不存在、生成ソース主指定、明示nullと省略を区別する。保存テンプレートのない主へ別ソースの元情報を代用しない。
- 新規保存の順序必須、旧設定の順序省略互換、指定済み順序の重複・不足・余分なパスの拒否を確認する。
- main・rendererのテストは`tests/main/`・`tests/renderer/`、複数ファイルを開く実機記録は`tests/verification/`に置く。これは受入条件であり、今回アプリの実装テストを行ったという記録ではない。

## 7I.7 非同期結果の採用と所有権（2026-11-09、三者監査#6）

外部05Aの遅延結果保護を具体化する確定契約です。現行`5cf2d85`は`openFromPath`等がawait後に無条件適用するため、**ソース修正が必要**です。

```ts
interface OpenReadGuard {
  readonly requestGeneration: number;
  readonly documentEpoch: DocumentEpoch;
  readonly documentRevision: number;
}
// canAdoptOpenResult: 3値一致かつ終了判定中でない、同期確定時の条件。
// waitForReadTurn: 3値不一致ならfalse、close中だけなら解除まで待って再検査。
```

要求世代はストア／ウィンドウ単位で単調増加させ再利用しません。通常open・opts・手動追加・新規作成／消去・復元・関連付けの処理開始で発行し、後の要求が取消・失敗でも前の要求を有効へ戻しません。関連付けの収集・待機中は発行せず、7Kのキューから開始するときに発行します。再帰importやPlugin型取得は親guardを引き継ぎ、子処理ごとに新要求にしません。

文書世代は文書置換で変え、`documentRevision`は同じ文書内で単調増加させます。有効な編集commit・Undo/Redo、履歴外のソース集合／順序・読み込みコンテキストの変更、SaveAs成功によるパス／sourceKey変更を含めます。Undo/Redoで同じ文書内容へ戻っても旧revisionは再利用しません。履歴長・HistoryNodeId・docオブジェクト参照だけで代用しません。選択・検索・表示・診断、保存先を変えない保存baseline更新、no-opだけでは増やしません。

3値を最初のawait前に固定し、未保存確認前後を含む各非同期段階とcatchの通知前に照合します。確認待ちで文書が変わっても、その後にrevisionを取り直して変更を追認しません。最終照合・一括適用・固定セッションsnapshotと保存要求の登録は、awaitを挟まない一つの確定処理とします。失効した結果は図、メタデータ、診断・成功／失敗表示、セッションへ反映せず、自動で最新文書へ再試行しません。不要になったI/Oの物理中断は必須ではなく、資源の後始末は行います。

初期bootstrapのguardはrenderer初期化時、利用者が操作できる前に確保します。受信時に新しいguardへ作り直して、既に行われた操作を無視しません。セッション復元からsamplesへの失敗時処理も同じguardへ従います。7J.9の終了判定中は適用を保留し、取消後は3値を再照合してから適用します。 `canAdoptOpenResult`がfalseになる理由を区別します。3値不一致なら破棄し、3値一致で終了判定中だけなら`waitForReadTurn`で保留します。終了取消で再開するときも再検査し、終了確定・ウィンドウ破棄なら非採用として後始末します。結果通知も`publishReadOutcomeWhenAllowed`で同じ保留・再検査を行います。`commitOpenWhenAllowed`は待機後、最終照合から適用・session登録までを同期確定し、待機中に一部を適用しません。

**適用前guardと採用後の処理を分けます。** 自分のcommitで文書世代・revisionは変わるため、セッション保存の完了処理に元guardの3値一致を要求しません。採用時のcommit識別と固定snapshotを順序付き保存要求へ登録し、遅い旧保存で後の採用状態を戻しません。保存失敗通知はその採用コンテキストが現在も有効な場合だけ示し、適用済みの図を巻き戻しません。完了時のライブストアからsnapshotを採り直しません。

**busyの解除は要求の所有権で判定します。** 編集によるrevision不一致でAが失効しても、Aが現在のbusy所有者なら自分のbusyを終了できます。Bへ所有権が移っていればAのfinallyで解除しません。採用判定の3値をbusy解除へ流用して表示を残したり、新要求の表示を消したりしません。

受入条件は、A待機中にB開始→B成功／取消／失敗→A完了、解析・確認・I/O・import／Plugin待ち中の編集、Undo→Redo、SaveAs、古い成功／失敗と例外、起動復元・samples競合、終了取消後の適用、セッション応答逆転、busy所有者変更と編集だけによる失効を含めます。現行の通常読込テスト成功を、この未実装契約の検証済み扱いにしません。

## Related

- [[TECSCDE-DT-EL内部仕様]]
- [[TECSCDE-DT-EL内部仕様 - 04B CDLパーサ設計]]
- [[TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計]]
- [[TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合]]
- [[TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧]]

- [[TECSCDE-DT-EL内部仕様 - 監査対応 09-18 読み込みと設定]] — 該当する監査項目の契約補足（2026-11-09）。

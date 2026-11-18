---
date: 2026-11-08
description: "監査#21の内部設計。履歴長に依存せず、ソース別の保存済み文書状態と一意な履歴位置を保持し、Undo分岐・非同期保存・一部失敗でも未保存変更を保持する。"
project: TECS
quarter: Q4-2026
status: active
tags: [work-note, tecs, tecscde, spec, architecture]
---

# 7J. 保存チェックポイントと未保存判定

[[TECSCDE-DT外部仕様 - 05 ファイル操作]]5.4・5.7の未保存判定を具体化します。[[TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計]]が継承していた、TS内部仕様の`past.length !== savedAtHistoryLength`による判定は採用しません。以下は2026-11-08の契約更新である（三者監査#3・#4は段0で実装した、as of 2026-11-12。2026-11-17 に追記）。

## 7J.0 決定状態と責務（2026-11-08、三者監査#3）

本章の振る舞いは外部05の5.4・5.7に対応する**確定契約**です。型・関数の名称を案として記す箇所も、状態比較・成功結果の反映・書込順の保証を任意にする意味ではありません。`status: active`は仕様の有効性を示し、コードの実装完了を示しません。

| 項目 | 確定契約・責務 | 現行コード`5cf2d85`の確認結果（2026-11-09 時点。段0 で実装済み） |
|---|---|---|
| 未保存判定 | rendererでソース別保存状態を比較し、全体へ集約 | `store.ts`の`isDirty()`は`past.length`比較。未反映 |
| 履歴位置 | 文書世代と一意な履歴ノードIDで対応付け | `History`はpast/futureのみ。未反映 |
| 保存開始・完了 | rendererがチケットを保持し、成功ソースの実保存状態だけbaselineへ反映 | `file-actions.ts`は完了時に`markSaved()`。未反映 |
| 書込順 | mainが正規化済み保存先ごとに直列化 | `FileService.writeAtomic()`は固定tmp名で直接write/rename。未反映 |

したがって、仕様の整合修正だけで三者監査#3の実装差が解消したとは扱いません。外部要求を履歴長判定へ戻さず、本章を実装の受入基準とします。終了手順は7J.9（三者監査#4）を正とし、現行コードは保存管理・終了確認の双方に未対応でした（2026-11-09 時点。段0 で実装済み）。

## 7J.1 保存対象の文書状態

`DirtyTracker`は、[[TECSCDE-DT-EL内部仕様 - 04C ファイル別保存契約|4C]]の保存対象ソースごとに、最後に保存成功した**文書状態のスナップショット**を保持します。保存すべき状態の比較を判定の根拠とし、履歴の長さ・操作回数・オブジェクト参照だけでは判定しません。

`SourceSaveState`（案）は、対象ソースに属するセルの作成・削除・名前・属性・所属、位置・寸法、ポート要素と添字・配置、結合代入・保存対象の経路、利用者が編集する用紙や設定等を、ソースの保存契約に沿って表します。元の原文のうち編集・往復保持する内容も対応付けます。他ソースのセルを混ぜません。外部5.1.x・4E.5の可変長配列の個数情報も含め、未結合末尾要素の挿入・削除で結合代入が変わらなくても変更として比較します。保存チケットは開始時点の個数を含み、保存中の追加編集を保存済みにしません。

保存時刻・書き出し時刻等の自動生成注記、診断、選択、検索、可視フィルタ、ズーム・パン、表示用の強調・凡例は含めません。型解決やimport追跡の派生表示だけを、利用者の編集として扱いません。一方、利用者が変更したポート・配列要素・位置・用紙等の保存対象を、派生値として除外しません。シリアライズ時に更新するタイムスタンプをそのまま比較して、常にdirtyになる設計を避けます。

比較は正規化された保存対象データの等価性で行います。ハッシュを高速化に使う場合も、衝突によるclean誤判定を許さない照合を行います。`DirtyTracker`の状態自体はCDLやセッションへ保存しません。

## 7J.2 履歴位置の識別

履歴には、文書世代の`documentEpoch`と一意な`HistoryNodeId`を付けます。`HistoryNodeId`は配列添字ではなく、履歴上の状態を識別する値です。

- 新しい文書の履歴ルートへIDを割り当て、実際の変更をcommitすると新しいIDを割り当てます。
- Undo／Redoでは対応する既存ノードIDへ移動します。Undo後の新規編集は、消えるfutureと同じ深さでも**別ID**にします。IDを再利用しません。
- コマンドの再生で新しいdocオブジェクトができても、対応する履歴ノードIDは変えません。`Command.apply()`の中でIDを発行しません。
- no-opと表示だけの変更で新しい編集ノードを作りません。履歴の剪定で保存時ノードが一覧から外れても、ソース別の保存済み状態は保持します。

履歴ノードIDは保存要求と履歴位置の照合に使いますが、**IDが同じことだけでもcleanと判定しません**。履歴外のソース追加等で状態が変わるためです。最終的には7J.1のソース別文書状態を比較します。別ノードでも保存対象が同じ状態へ戻った場合はcleanにできる契約とします。

## 7J.3 判定と共有

```ts
interface SavedCheckpoint {
  readonly sourceId: SourceId;
  readonly documentEpoch: DocumentEpoch;
  readonly historyNodeId: HistoryNodeId;
  readonly sourceLocationGeneration: number;
  readonly destinationPath?: string;
  readonly state: SourceSaveState;
  readonly successfulWriteSequence: number;
}
// SourceIdは実行中のソースの同一性。名前を付けて保存でパスが変わっても維持する。
// DirtyTracker.dirtySources(currentStates): readonly SourceId[]
// DirtyTracker.isDirty(currentStates): boolean
// DirtyTracker.recordSaved(ticket, successfulSources): DirtyTracker
```

現在の保存対象状態と、そのソースの保存済み状態が異なるソースを未保存とします。全体は、未保存ソースが1つでもあればdirtyです。保存対象の新規セル・削除・結合等もこの比較で検出します。現在の履歴長が保存時と同じでも、比較を省略しません。

タイトルの未保存印、ステータス、操作前の破棄確認、rendererからmainへの`window:setDirty`には、この一つの判定結果を使います。保存完了イベントだけから無条件に`setDirty(false)`を送らず、完了結果を反映した**現在の状態を再評価**します。

## 7J.4 非同期保存の確定

保存開始時に`SaveTicket`（案）を作り、文書世代・履歴ノードID・対象SourceId・現在の保存先世代とパス・出力先・保存するソース状態・出力本文を一組で固定します。4Cの検証とシリアライズもこの状態に対して行います。

```ts
interface SaveTicket {
  readonly ticketId: string;
  readonly sourceId: SourceId;
  readonly documentEpoch: DocumentEpoch;
  readonly historyNodeId: HistoryNodeId;
  readonly sourceLocationGeneration: number;
  readonly expectedCurrentPath: string | null;
  readonly targetPath: string;
  readonly state: SourceSaveState;
  readonly content: string;
}
```

チケットは**1ソース・1回の書き込みごと**に発行し、`state`と`content`を同じ固定した文書から作ります。可変データへの参照を保持して後続編集で内容が変わる形にしません。複数ソースの保存はチケット列として集約し、結果をソースごとに反映します。文書世代・履歴位置は呼び出し元が確定し、`apply()`やmainで新しく作りません。

rendererの保存コーディネータはチケットをIDで保持し、7J.7の要求へ`targetPath`を`path`として渡します。要求・応答を照合してから、チケットの保存先世代・期待する現在パスと現在のソースを確認します。履歴位置が進んだことだけを理由に正当な保存成功を捨てず、書いた状態をbaselineへ反映して最新状態と比較します。

1. 実際に書き込んだ本文に対応する状態だけを、保存成功時のbaselineへ採用します。完了時点の最新docを、書いた内容と見なして記録しません。
2. 保存中に編集が進んだ場合、書いたSをbaseline、現在のTを比較対象にします。TがSと違えばdirtyを維持します。
3. 失敗・キャンセルした対象のbaselineは更新しません。別の文書へ切り替わった場合、旧世代の完了を新しい文書のclean化に使いません。
4. 同じ正規化済み保存先への書き込みはmainで開始順に直列化し、古い保存が新しい保存より後からディスクを上書きしないようにします。結果には書き込み順を関連付け、古い成功応答が遅れて届いても、新しい成功のbaselineを戻しません。
5. 新しい保存が失敗した場合でも、直前の実際の保存成功状態をbaselineとして保持します。「最新要求があった」という理由だけで、それ以前の正当な成功結果を捨てません。
6. 保存先の変更後に届く旧保存先への完了は、現在のソースのcheckpointへ適用しません。SourceIdだけでなく、ticketの保存先世代・期待する現在パスも照合します。`writeSequence`は同じ正規化済み保存先内だけで比較し、別の保存先の順序番号同士は比較しません。

保存先と同じファイルを文書の切替・再読込で読む場合は、先行するアプリ内書き込みの完了と順序を揃えます。書き込み途中の内容を読み、誤ったclean状態を登録しません。外部アプリによるファイル変更の検出・競合処理は別の契約であり、外部変更でbaselineを勝手に更新しません。

保存中は、保存が終わったと見なして未保存表示や終了保護を先に解除しません。終了操作は保留中の保存結果を待ってから現在のdirtyを再評価します。rendererが応答しない場合のmain側の既存の保守的な確認処理にも、保存中の未確定状態をcleanとして渡しません。

## 7J.5 複数ソース・名前を付けて保存

4Cの原子的書き込みは**各ファイル単位**です。A・Bの保存でAだけ成功した場合、Aのbaselineだけを更新し、Bの未保存状態を残します。一部成功を全体の保存完了として扱いません。利用者への結果も成功・失敗したソースを区別し、全体がcleanになったとは表示しません。

「名前を付けて保存」の取消・失敗では、パス、`locale`、baseline、7Hのセッションを変更しません。成功後は同じSourceIdの保存先を更新し、実際に保存した状態へbaselineを関連付けます。パス変更に伴うソースキーの対応は7J.1の比較でも揃え、パスの付け替えだけで同じ内容を別物と誤判定しません。別ソースの未保存変更と、保存中に加わった編集は残します。

成功時の保存先変更では`sourceLocationGeneration`を進め、新しいパスとbaselineを同時に確定します。例えばAへSを保存中に、編集TをBへ名前を付けて保存できた場合、遅れて届いたAの成功で現在BのbaselineをSへ戻しません。その後UndoでSへ戻っても、Bに保存したTと異なればdirtyです。同じソースへの保存先変更操作は一度に1件とし、後続の保存先変更は先行結果の確定後にticketを作ります。保存先選択の前後でも文書世代・SourceId・保存先世代を確認します。

成功後の主ファイルパス・参照集合・`sourceOrder`の変更は、[[TECSCDE-DT-EL内部仕様 - 07H セッション保存と復元|7H]]・[[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約|7I]]へ同じ確定結果から反映します。セッション保存の成否と、CDL本文の保存成功は混同しません。

## 7J.6 読み込み・新規作成・履歴外操作

- 文書を正常に開き直した場合は、解析・初期化を済ませた読み込み状態を各ソースの初期baselineとします。読み込みキャンセル・失敗では現在の判定を変更しません。
- 手動追加・import追跡では新しく取得した通常ソースの初期baselineを登録し、既存ソースの未保存編集をcleanへ戻しません。解析順・型解決・生成型の表示が増えただけで、既存編集ノードを保存済み扱いにしません。
- 新規の空主文書は初期空状態をbaselineとしてcleanで開始し、最初の保存対象変更からdirtyにします。ファイルパスが無いことだけをdirtyの理由にしません。
- 「消去」等で参照ソースを保持する場合、そのソースに残した本文変更とbaselineも保持します。主文書を新しくしたことを、保持した参照の未保存編集まで消去する理由にしません。破棄確認をキャンセルした場合は全状態を保持します。
- Undo／Redo・通常再配置・active最上段配置・配列要素操作等の保存対象変更後は、現在状態から判定し直します。選択・検索・フィルタ・パン・ズーム・凡例・画像出力・読み取り専用ソース表示はbaselineを変更しません。

## 7J.7 保存要求と結果のAPI

文書保存用に、`FileGateway.saveSource(request)` → preloadの`file.saveSource` → mainの`file:saveSource`／`FileService.saveSource`（案）を用意します。既存の原子的書き込みを共用し、要求と完了結果を対応付けます。

```ts
interface SourceSaveRequest {
  readonly ticketId: string;
  readonly sourceId: SourceId;
  readonly documentEpoch: DocumentEpoch;
  readonly sourceLocationGeneration: number;
  readonly path: string;
  readonly content: string;
}
type SourceSaveResult =
  | { kind: 'ok'; ticketId: string; sourceId: SourceId; path: string; writeSequence: number }
  | { kind: 'failed'; ticketId: string; sourceId: SourceId; path: string; detail: string };
```

mainは正規化した保存先単位で書き込みを直列化し、成功時にその保存先の書き込み順を返します。キューへの受付順を固定し、書込失敗・rename失敗でも当該要求の失敗結果を返してから後続要求を処理します。一つのrejectでキュー全体を停止させません。要求ごとに衝突しない一時ファイルを使い、失敗時の後始末で別要求の一時ファイルを削除しません。

同じ保存先へ書き込む旧`save`・`saveAsDialog`を残す場合も、書込部分はこの共通キューを通します。同じ保存先の画像export等も共通キューを迂回させませんが、文書のcheckpointは更新しません。読み直しは、先行して受け付けた当該保存先の書き込みが終わる順序点を待ってから行います。異なる保存先同士の全体直列化は要求しません。

`ticketId`・`sourceId`・保存先の対応が一致する応答だけを採用し、同じ完了の再通知は二重反映しません。rendererは採用済みの当該保存先の成功順より古い成功応答でbaselineを戻さず、失敗応答では最後の成功baselineを維持します。rendererは保持したSaveTicketの状態を使い、完了結果から新たな保存状態を作り直しません。文書世代は保持したticketと現在状態で照合します。

「名前を付けて保存」は、副作用のない保存先選択`chooseSavePath(suggestedName)`（案）で取消を判別してから、同じ保存要求を使います。選択だけでパス・baselineを変更しません。旧`save`・`saveAsDialog`の簡便APIを残す場合も、文書の保存処理では本節の要求・結果管理を通し、`Promise<void>`の完了だけで現在の図をcleanにする旧経路を使いません。画像エクスポートは文書の保存チェックポイントを更新しません。

### 7J.7.1 Ctrl+S ショートカット（2026-11-17 決定、三者相違一覧 2-10）

`AppShell`のキー処理（`ctrlKey || metaKey`、`key.toLowerCase() === 's'`）が、ツールバー「保存」（`data-action="save"`）と**同じ保存関数**を呼ぶ。外部 [[TECSCDE-DT外部仕様 - 05 ファイル操作|05]] 5.4 の規定どおり、`TEXT_INPUT_TAGS` の要素にフォーカスがあるときは処理しない。保存の失敗・拒否・一部失敗は、ツールバー経路と同じく`reportActionError`（または画面通知）へ回し、ショートカット側で握りつぶさない（`void save(...)` だけで例外を捨てない。実装修正は V0.2.6 段4、2-10・4-1・4-3）。名前を付けて保存にはキーを割り当てない。

## 7J.8 実装時の検証条件

| 操作列・条件 | 期待する判定 |
|---|---|
| 履歴Nで保存→Undo→別内容の編集で再び履歴N | 保存内容と異なるのでdirty。別ノードIDを持つ |
| 保存済み状態へUndo／Redoで戻る | 現在の保存対象がbaselineと同じならclean |
| 違う操作列でも保存対象が同じ状態へ戻る | 履歴長やノードIDだけでdirtyとせず、状態比較に従う |
| 保存Sの待機中に編集してT→Sの保存成功 | baselineはS、現在Tが異なればdirty |
| 同じ保存先への複数保存・成功応答の到着逆転 | ディスクの書込順と最後の成功baselineが一致 |
| 同じ保存先の先行保存失敗→後続保存成功 | キューが継続し、後続の実保存状態だけを成功baselineへ反映 |
| 新旧保存API・同じ保存先への読み直し | 共通キューを迂回せず、読取は先行書込後。別保存先とは順序番号を比較しない |
| 不一致ticket・重複応答・no-op | 別ソースをcleanにせず、baselineや履歴を重複更新しない |
| AへSを保存待ち→編集TをBへ名前を付けて保存成功→古いAの成功→UndoでS | BのbaselineをTから戻さず、現在Sはdirty |
| A成功・B失敗 | Aだけ保存済み。Bが異なるので全体dirty |
| 名前を付けて保存を取消・失敗 | パス・baseline・セッション・dirtyを維持 |
| 名前を付けて保存成功、別ソースに未保存編集あり | 保存先だけ更新し、別ソースのdirtyを維持 |
| 新規空図→編集→初期空状態へUndo | 初期空状態へ戻ればclean |
| 手動追加・型解決・診断更新・表示操作 | 既存ソースの未保存編集を消さず、表示だけでdirty化しない |
| 履歴剪定・文書切替・古い保存完了 | baselineを失ったり別文書をclean化したりしない |
| 部分失敗・保存中新編集がある状態で終了／新規／開く | 最新判定に従って未保存確認が働く |

`SourceSaveState`の比較、HistoryNodeId、保存結果反映、UI・mainへのdirty通知のテストは`tests/renderer/`、同一保存先の書込順は`tests/main/`、終了確認を含む実機記録は`tests/verification/`へ置きます。今回の作業は仕様の更新であり、アプリの実装テストを実行したという記録ではありません。

## 7J.9 終了確認と保存中の待機（2026-11-09、三者監査#4）

[[TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07M 終了確認と保存中の待機|7J.9 本文]]へ逐語で分離した（2026-11-17、25KB閾値。7J.9.1 終了トランザクション・7J.9.2 応答不能と取消・7J.9.3 IPCと通知・7J.9.4 実装時の受入条件）。

## Related

- [[TECSCDE-DT-EL内部仕様]]
- [[TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計]]
- [[TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計]]
- [[TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧]]

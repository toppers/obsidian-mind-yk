---
date: 2026-11-08
description: "監査#22の入口設計。CLIの先頭1件とOS関連付けの複数入力を区別し、要求境界付きキュー、既起動instanceへの順序保持転送、7Iへの一括要求と起動優先順位を定める。"
project: TECS
quarter: Q4-2026
status: proposed
tags: [work-note, tecs, tecscde, spec, architecture]
---

# 7K. 関連付け入力の収集と一括オープン

[[TECSCDE-DT外部仕様 - 05A 開く（読み込み）]]5.3の「ファイル関連付けの複数入力は最後を主ファイル、残りを追加」と、CLIの「先頭の対象1件」を、別の入口として具体化します。[[TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計]]7.4の単数変数による受信例を置き換える、2026-11-08の内部設計です。実装済みを意味しません。

## 7K.1 明示的な起動コンテキスト

```ts
interface LaunchOpenRequest {
  readonly requestId: string;
  readonly kind: 'cli' | 'association';
  readonly paths: readonly string[];
  readonly cwd: string;
}
const isStartupFile = (path: string): boolean => /\.(?:cde|cdl|tecsgen-opts)$/i.test(path);
```

型と補助関数名は契約案です。起動コンテキストはmainの入口で確定し、引数の個数やパスの形だけで入力元を推測しません。

requestIdは別プロセス・別の起動要求でも衝突しない値を受信元で発行し、転送・再配送でも同じ値を維持します。パスやプロセス内だけの連番を要求全体のIDにしません。

| 入力元 | 要求への変換 |
|---|---|
| 通常のCLI | 対象拡張子の最初の1件だけを`paths`へ格納。2件目以降を追加CDLにしない |
| Windows/Linuxの関連付けランチャー | 関連付け専用モードと、1回の受信バッチのパス列を明示して起動。列挙順を保った`association`要求にする |
| macOSの関連付け受信 | OSが渡したファイル配列と要求境界をアダプタから受け、配列順のまま`association`要求にする |

Windows/Linuxの登録起動コマンドには内部モード識別子`--tecs-open-associated`（案）とパス列の区切り`--`を用い、このモードでは区切り以後を関連付け入力として解析します。通常CLIはこのモードを使いません。OSやランチャーが複数回の起動へ分割する場合、それらをタイマーで同じ操作と推測せず、明示された要求ID・境界がある場合だけ同じバッチにします。登録側が一括パス列を渡す設定も本機能の実装範囲です。

パスは元の表記を保持して受け、相対値は**送信元のcwd**で絶対パス化します。大小文字非区別は対象拡張子の識別規則であり、実パスの小文字化ではありません。

## 7K.2 macOSの配列通知と受信境界

Electronの標準`open-file`は1つの`path`を通知し、起動初期にも発生します。そのイベント列だけに同一操作のバッチIDや終端があるとは仮定しません。単数の`pendingOpenPath`へ代入して前のパスを失う処理を廃止します。

**内部設計として`MacAssociationOpenAdapter`を追加**し、AppKitの`NSApplicationDelegate`のファイル配列通知を要求単位でmainへ渡します。`application:openFiles:`等の配列単位を受けるネイティブ連携を用い、次の入口契約へ変換します。これは新しいアダプタの設計であり、Electronに同名のJSイベントが既存実装されているという意味ではありません。

```ts
// アダプタ → mainのLaunchOpenInbox。1つのOS要求の境界を明示する。
inbox.begin(requestId, { kind: 'association', cwd });
inbox.append(requestId, orderedPaths);
inbox.end(requestId);
// または、同じ値をinbox.acceptClosed(request)で1回渡す。
```

ネイティブ側が同一要求のパス配列を把握した時点で終端を通知し、JS側の一定時間待ちでは確定しません。標準の分割通知と配列通知を無条件に二重処理せず、同じOS通知の受信責務をアダプタへ一本化します。単一ファイルのネイティブ通知も、明示された1件バッチとして扱います。

アダプタのネイティブ連携・配布組み込みは実装とmacOS実機検証が必要です。標準`open-file`のリスナを追加しただけで複数バッチ対応を完了したとはしません。要求境界を取得できない受信経路ではパスを保留し、境界付き通知が必要という状態を明示します。先頭・末尾1件だけを成功扱いにしたり、タイマーを代替の確定規則にしたりしません。

## 7K.3 収集キューと役割の確定

`LaunchOpenInbox`（案）はrequestIdごとにパス列を保持し、次の状態を区別します。

- **収集中**: begin後、end前。追加入力は同じ配列へappendし、上書きしない。
- **確定済み**: 全パスとcwdが揃った要求。一括読み込み開始まで順序付きキューに保持する。
- **処理済み／取消／失敗**: 同じrequestIdの重複配送を再適用しない。別requestIdで同じパスを開き直す操作は抑止しない。

収集開始した要求はendまたはabortで終端を通知します。収集失敗や中断時はバッチ全体を失敗として通知し、途中のパスを開きません。待機の時間制限を設ける場合も、期限をバッチ正常確定の根拠にはせず、受付失敗として扱います。

バッチ内の通常CDLは、最後の対象パスから主ファイルを決め、その後に同一正規化済みパスの重複を除きます。[[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約|7I]]と同じく、初出順の`sourceOrder`と、主ファイルを除く`referencePaths`を作ります。`A B A`なら主ファイルA、sourceOrderはA・B、参照はBです。主ファイルを配列末尾へ移しません。

CLI要求はこの「関連付けの最後を主ファイル」規則へ流しません。CLIの先頭1件が通常CDLなら単一要求、optsならその**ファイル内**のCDL列挙を7Iで処理します。単独optsの関連付け入力も既存のopts経路へ渡せます。複数opts、またはoptsと通常CDLが混在する関連付けバッチの設定合成はTBCとし、この版ではバッチ全体を未対応として通知し、勝手に最後の入力だけを開きません。

## 7K.4 Windows/Linuxの既起動instanceへの受け渡し

関連付け由来かどうかとパスの順序は、**受信したプロセスで**確定します。既起動instanceへは、順序付き`LaunchOpenRequest`を`requestSingleInstanceLock`の`additionalData`等の値として渡します。primary側の`second-instance`で受けるargvを再解析して主ファイルや入力元を決め直しません。転送サイズの上限等で完全な要求を渡せない場合は、成功として先頭だけを送らず、失敗通知または完全なバッチを渡せる別の配送方式を用意します。

main初期化の概略は次のとおりです。OS受信アダプタはreadyより前に登録します。

```ts
const inbox = new LaunchOpenInbox();
installAssociationReceivers(inbox); // 独自アダプタ。macOSの配列受信を含む
app.on('second-instance', (_event, _argv, _cwd, data) => {
  const envelope = decodeLaunchOpenEnvelope(data); // unknownを検査。open/focus/invalid
  if (envelope.kind === 'open') inbox.acceptClosed(envelope.request);
  else if (envelope.kind === 'focus') focusPrimaryWindow();
  else notifyInvalidLaunchRequest();
});
const invocation = parseLaunchOpenRequest(applicationArgs, process.cwd());
const primary = app.requestSingleInstanceLock({ launchOpen: invocation });
if (!primary) {
  app.quit();
} else {
  if (invocation) inbox.acceptClosed(invocation);
  startPrimaryWindow(inbox); // 初期受付確定・renderer準備を待つ。7K.5
}
```

`applicationArgs`は実行環境の起動用引数を除いたアプリ引数です。内部関連付けモードか通常CLIかを`parseLaunchOpenRequest`で分岐し、通常CLIにだけfindによる先頭選択を使います。不正な転送値は文書を変更せず拒否し、引数が無い二重起動は既存ウィンドウの前面化だけとします。

## 7K.5 起動時と実行中の一括適用

初回は、CLIまたは関連付けの**明示入力** ＞ [[TECSCDE-DT-EL内部仕様 - 07H セッション保存と復元|7H]]のlastSession ＞ samplesの優先順位を維持します。初期のOS受信アダプタは受付確定を通知し、収集中バッチが残る状態を「明示入力なし」としてfallbackへ進めません。readyやrenderer準備だけをバッチ終端にはしません。

最初の確定要求を7Iの一括要求へ変換して初期文書を組み立て、`app:bootstrap`は起動時に一度だけ供給します。複数の独立した要求が待機している場合、受信順のキューを保持し、初期適用後に後続要求として処理します。初期の明示要求が不正・失敗した場合は、入力なしと取り違えて別ファイルを成功表示せず、空の初期文書に読込失敗を示します。7Hのセッション復元失敗時のsamples規則は別の経路として維持します。

既起動instanceへの要求は`app:openRequest`（案）でrendererへ渡し、bootstrapを再送しません。確定要求をキューから取り出して読み込みを開始するとき、最初のawait前に7Iの要求世代を発行します。受信・収集・待機自体と、読み込み開始を区別します。主ファイルと入力順、送信元cwdを同じ要求で渡します。

現在の図を置き換える前に[[TECSCDE-DT-EL内部仕様 - 07J 保存チェックポイントと未保存判定|7J]]の最新dirtyに基づく確認を1回だけ行います。取消・失敗では図とセッションを維持します。全CDLの読込・import解決・構築成功後に1回適用し、7HのsourceOrderを含むセッションを1回保存します。途中の個別ファイルをストアへ逐次公開しません。

処理中の新たな関連付け要求は待機キューへ保持し、未確定の同一バッチを新しい読み込みとして分割開始しません。別の読み込み操作で要求が無効になった場合は7Iの世代検査へ従います。終了判定中は7J.9の編集・結果適用停止を尊重し、取消で再開、終了確定なら後続要求を現在文書へ適用しません。

## 7K.6 実装時の検証条件

- 通常CLIのA・BはAだけ、関連付けのA・BはBを主ファイル・Aを参照として読み込むこと。3拡張子の大小文字非区別と元のパス表記も維持すること。
- 関連付けのA・B・C、A・B・Aで7Iの役割・sourceOrderを得ること。複数引数という理由でCLIを関連付けへ変えないこと。
- macOSの同一要求の複数通知、異なる要求の連続受信、ready前後、renderer準備前後でパスを失わず、明示された境界だけで1バッチにすること。
- macOSの配列アダプタと標準通知を二重処理せず、ネイティブ連携がない状態を対応済みとしないこと。一定時間待ちで同時操作を推測しないこと。
- 既起動instanceでadditionalDataの順序・cwd・requestIdを維持し、second-instanceのargvの順序へ依存しないこと。重複配送と同じパスの別要求を区別すること。
- 収集中はlastSession／samplesを先に適用せず、初期bootstrapが1回、後続要求はopenRequestとなること。
- 取消・読込失敗・混在opts未対応、終了判定中でも、途中の図・設定・セッションを適用しないこと。成功時は一括適用と1回のセッション保存を確認すること。
- 受信キュー・変換・IPCのテストは`tests/main/`、適用・確認は`tests/renderer/`、各OSの関連付けから開く実機記録は`tests/verification/`へ置くこと。今回は仕様の更新であり、これらの実装・実機検証を行った記録ではありません。

## API資料と実装上の区別

- [Electron app：open-file](https://www.electronjs.org/docs/latest/api/app#event-open-file-macos)は単一パスの通知と起動初期の受信を説明する。本節の配列受信アダプタは追加設計である。
- [Electron app：second-instance](https://www.electronjs.org/docs/latest/api/app#event-second-instance)では転送argvの順序変更に注意が必要なため、本節はadditionalDataで確定済み要求を渡す。
- [Apple NSApplicationDelegate：application:openFiles:](https://developer.apple.com/documentation/appkit/nsapplicationdelegate/application%28_%3Aopenfiles%3A%29?language=objc)の配列通知をmacOSアダプタの受信単位とする。Electronへのネイティブ連携と配布への組み込みは本契約を実装・検証する対象である。

読み込み開始時のguardと結果適用は[[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約|7I.7]]を正とする。受信requestIdは配送の識別であり、rendererの要求世代・文書revisionの代わりにはしない。終了取消後の保留結果も再検査する（三者監査#6、2026-11-09）。

## Related

- [[TECSCDE-DT-EL内部仕様]]
- [[TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧]]

- [[TECSCDE-DT-EL内部仕様 - 監査対応 09-18 読み込みと設定]] — 該当する監査項目の契約補足（2026-11-09）。

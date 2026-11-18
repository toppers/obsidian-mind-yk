---
date: 2026-11-17
description: "TECSCDE-DT-EL内部仕様 7J.9（終了確認と保存中の待機、三者監査#4）。第7J章から25KB閾値で逐語分離（2026-11-17）。終了トランザクション・応答不能と取消・IPCと通知・受入条件。"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note [[TECSCDE-DT-EL内部仕様 - 07J 保存チェックポイントと未保存判定]]（2026-11-17、25KB閾値で7J.9節を逐語分離。見出しの番号は元のまま）。

## 7J.9 終了確認と保存中の待機（2026-11-09、三者監査#4）

外部05の5.7に対応する**確定契約**です（当時は実装未反映。三者監査#4は段0で実装済み、as of 2026-11-12）。現行`5cf2d85`の`CloseGuard`はcached dirtyがfalseなら即closeし、IPCも`window:setDirty`だけです。旧7.9の例は従来実装の記録であり、以下へ置き換えます。

### 7J.9.1 終了トランザクション

ウィンドウごとに`idle → checking → confirming / closing`を管理します。通常closeは、キャッシュ値に関係なく同期的に`preventDefault()`してから進めます。

1. mainが一意な`queryId`を発行し、当該`webContents`へ`window:requestCloseState`を送ります。checking/confirming中の連続closeは同じ処理へ集約し、問い合わせ・確認を重ねません。
2. rendererは新規編集・保存要求と、非同期読み込み等の文書変更結果の適用を停止します。ただし、**開始済み保存の成功・失敗通知とcheckpoint反映は進めます**。7J.4・7J.7の保留保存を結果反映まで待ち、現在の文書世代・履歴位置・dirtyを求め、保留保存なしの`ready`を返します。
3. mainは送信元ウィンドウ／`webContents`・queryId・応答型を照合します。当該ウィンドウからの新規書込受付を閉じ、受理済み保存のキュー完了も確認します。rendererの停止・反映完了の応答と組み合わせ、問い合わせ開始時のキュー一覧だけで完了判定しません。受付停止後の新規要求は失敗として返します。
4. 有効な最新回答がcleanなら閉じ、dirtyなら既存の「保存せずに終了」「キャンセル」を出し、キャンセルを既定にします。閉じる許可はこのトランザクションの再入closeに**一度だけ**使います。

### 7J.9.2 応答不能と取消

renderer応答待ちのタイムアウトは、mainの受理済み書込キューの待機打切り理由にしません。応答不能・クラッシュ・世代不一致でも新規書込受付を閉じ、受理済み保存の完了を待ちます。その後も最新の結果反映・dirtyを確認できなければ**dirty不明**として「保存状態を確認できません」と示し、同じ2択で確認します。最後の通知がfalse、通知なし、不正応答をcleanへ変換しません。通常終了のために未確定書込を破棄・成功扱いにしません。

取消ではqueryIdと閉じる許可を無効にし、`window:cancelCloseState`でrendererの停止を解除してmainの書込受付を再開します。**取消による文書・checkpointの巻き戻しは行わず、待機中に正常完了した保存のbaselineは維持します**。保留した非同期結果は、再開後に元の文書世代・要求世代を検査してから適用します。取消後の遅延応答は無効です。確認処理自体の失敗でも閉じる許可を出さず、可能な範囲で停止を解除します。

### 7J.9.3 IPCと通知

```ts
interface CloseStateRequest { readonly queryId: string }
type CloseStateResponse =
  | { readonly kind: 'ready'; readonly queryId: string;
      readonly documentEpoch: DocumentEpoch; readonly historyNodeId: HistoryNodeId;
      readonly dirty: boolean; readonly pendingSaves: 0 }
  | { readonly kind: 'unavailable'; readonly queryId: string };
// main → renderer: window:requestCloseState (CloseStateRequest)
// renderer → main: window:closeState (CloseStateResponse)
// main → renderer: window:cancelCloseState (CloseStateRequest)
```

型名は案ですが待機・照合の条件は必須です。sharedの型をpreloadの購読・解除／返信、rendererの`WindowGateway`・保存コーディネータ、mainの`CloseGuard`・書込キューへ接続します。`ready`は保存結果反映まで完了した意味です。ウィンドウ破棄時に購読を解除します。

`window:setDirty`は通常通知として維持しますが、close時の問い合わせ・保存待機の代用にしません。閉じるボタン・アプリ終了・メニュー等の通常終了経路で共通化し、`beforeunload`は再導入しません。アプリが止められないOS終了は外部仕様の対象外です。

### 7J.9.4 実装時の受入条件

- cached false・通知なしでも最初のcloseを中断し、最新問い合わせと保存待機を行う。
- 保存中closeで書込・checkpoint反映を待ち、失敗・新編集・SaveAs後の古い成功を最新dirtyへ反映する。
- 停止中も開始済み保存結果を処理し、待機との循環を起こさない。rendererタイムアウト後もmainの受理済み保存を待つ。
- 別ウィンドウ、不正queryId・型、取消後の回答、連続closeで誤許可・重複確認をしない。
- 取消で操作・受付を再開し、保存成功を巻き戻さず、古い非同期結果を適用しない。

テストは`tests/main/`・`tests/renderer/`、実機記録は`tests/verification/`へ置きます。既存のキャッシュ方式のテスト成功を、新契約の適合証明にしません。

## Related

- [[TECSCDE-DT-EL内部仕様 - 07J 保存チェックポイントと未保存判定]] — 分離元（保存チェックポイントと未保存判定）
- [[TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計]] — 7.9節（終了確認と保存待機の外側の設計）
- [[TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧]] — 10.8節（保存結果と未保存状態の契約）

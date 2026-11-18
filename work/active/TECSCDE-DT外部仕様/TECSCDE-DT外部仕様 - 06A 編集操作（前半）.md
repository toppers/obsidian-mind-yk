---
date: 2026-09-05
description: "TECSCDE-DT外部仕様書 第6章前半（編集操作 6.1–6.4）— TECSCDE外部仕様と同一、変更なし。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note [[TECSCDE-DT外部仕様 - 06 編集操作]].

## 6. 編集操作（前半）

要素の追加（6.1）、選択・移動（6.2）、削除（6.3）、結合の作成・削除（6.4）は、実行環境（ブラウザかデスクトップか）に依存しないUI操作・アンドゥ単位の設計であるため、[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 06A 編集操作（前半）|TECSCDE外部仕様第6章前半]]と**完全に同一、変更なし**。

キーボードイベントの判定（`KeyboardEvent.key`の名前付き値を用い、現行版Ruby/GTK版のビットマスク方式に起因するキー衝突が構造的に発生しない）についても、Electron・TauriいずれもWebViewが標準の`KeyboardEvent`を発火するため、[[TECSCDE外部仕様]]6.1.2・6.2.2の規定がそのまま成り立つ。

### 6.3.2 差分: Backspace でも削除する（2026-11-17 決定、三者相違一覧 6-22）

削除操作は、親の規定（Delete キー）に加え、**Backspace キーでも Delete キーと同じ操作として行える**（`KeyboardEvent.key` が `Delete` または `Backspace`）。デスクトップ版では Mac のキーボードに Delete キーが無いため、同じ動作を Backspace に割り当てる。選択の扱い・結合解除の優先・確認ダイアログを設けないこと・アンドゥの単位は Delete と同一とする。テキスト入力中・IME 変換中の Backspace は、入力欄の編集であり、図の削除として扱わない。実装は `gesture-controller.ts` が従来から両キーを受けており、本項で仕様に追いつかせた（ソース変更なし。入力欄・IME 中の除外は V0.2.6 で実機確認する）。

詳細は[[TECSCDE外部仕様]]該当節を参照。

## Related

- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 06A 編集操作（前半）|TECSCDE外部仕様 第6章前半（一次情報源、本章はこれと同一）]]
- [[TECSCDE-DT外部仕様 - 06 編集操作]]

- [[TECSCDE-DT外部仕様 - 監査対応 19-28 配列と配置]] — 該当する監査項目の契約補足（2026-11-09）。

- [[TECSCDE-DT外部仕様 - 監査対応 29-38 保存と画面]] — 該当する監査項目の契約補足（2026-11-09）。

---
date: 2026-11-06
description: "V0.2.0の_CDL_FILES.txtと_ROOT_CDL_FILES.txtの生成設計。再帰探索、書式、mainでの書き込み、IPC、結果と失敗の返却を定める。"
project: TECS
quarter: Q4-2026
status: proposed
tags: [work-note, tecs, tecscde, spec, architecture]
---

# 7G. V0.2.0 CDLファイル一覧生成

[[TECSCDE-DT-EL内部仕様]]第7章の追加設計です。根拠は[[TECSCDE-DT外部仕様 - 05B CDLファイル一覧の作成と自動配置]]5.3.y、[[TECSCDE-DT外部仕様 - 03 画面構成]]3.8.2、[[TECSCDE-DT外部仕様 - 02 動作環境]]2.5です。新しい識別子と失敗時の契約は内部設計案であり、実装済みを意味しません。

## 7G.1 責務と設定

rendererの情報ダイアログから`FileGateway`を通し、mainの`CdlFileListService`（案）を呼びます。対象ディレクトリ選択は既存のネイティブディレクトリ選択処理を利用します。`cdlFilesRoot`を`settings.json`に文字列として保存し、次回表示時の初期値にします。ファイルブラウザの`fileBrowserRoot`とは別の設定です。

mainがパスの正規化・ディレクトリの実在確認・再帰探索・書き込みを担当します。rendererに`fs`やNodeのパス操作を持ち込まず、ディレクトリ選択のキャンセルは設定変更なしとして扱います。一覧生成はドキュメントの編集コマンドではなく、履歴・dirty・セッションの開いているファイル集合を変えません。

## 7G.2 探索と生成

1. 対象ルート自身を含め、その配下を深さによらず探索し、拡張子`.cdl`の通常ファイルを集めます。CDLファイルを含まない中間ディレクトリにも降ります。
2. 親ディレクトリごとに分類し、その直下にあるCDLの**ファイル名だけ**を1行に1個持つ`_CDL_FILES.txt`を作成する計画を組み立てます。孫ディレクトリのCDLを親の一覧へ直接入れません。
3. ルート直下に`_ROOT_CDL_FILES.txt`を作成します。内容は今回作る全`_CDL_FILES.txt`の絶対パスを1行に1個とし、OSのパス表記でUTF-8にします。子一覧も既存の書式に合わせてUTF-8とします。
4. CDLが0件ならファイルを作成・置換せず、`empty`を返します。以前の一覧を削除する処理は追加しません。
5. 対象ルートにもCDLがあれば、ルート自身の`_CDL_FILES.txt`も生成し、ルート一覧に含めます。結果の件数はCDLの数ではなく、生成した子一覧ファイルの数です。

外部仕様5.3.y項目7〜10で2026-11-08に決定された規則の内部設計は次のとおりです。

1. **計画と適用の分離**: `planCdlFileLists(root)`（案）は、mainが探索して生成計画を組み、各一覧について`status: 'new' | 'same' | 'differs'`を返します。計画は書き込まず、`planId`と、既存内容のハッシュを持ちます。
2. **確認**: rendererは、計画に`differs`が1件以上あるときだけ確認ダイアログを出します（`FileGateway`経由）。置き換えるパスは最大10件と残り件数を示します。確認なしの経路は`new`と`same`のみです。`same`は書き込まず、`skippedSame`として数えます。
3. **並べ替え**: `compareCdlNames(a, b)`と`compareCdlPaths(a, b)`を、mainの純粋関数として1か所に置きます。名前は大文字小文字を区別せず比べ、同じなら元の文字列のコードポイント順にします。パスはディレクトリ区切りで分割し、要素ごとに名前の規則で比べます。`localeCompare`は使いません。子一覧とルート一覧の両方が同じ関数を使います。
4. **探索**: 拡張子`.cdl`は大文字小文字を区別せず判定します。リンクは`lstat`で判定し、ディレクトリのシンボリックリンク／ジャンクションは辿りません（循環の防止）。ファイルのシンボリックリンクは通常ファイルとして扱います。
5. **書式**: UTF-8（BOMなし）、改行はLF、末尾に改行を1つ置きます。読み込み側（7Eの`_CDL_FILES.txt`の探索）がLFの一覧を問題なく読めることを、実装時に確認します。

## 7G.3 書き込みと失敗（内部設計案）

探索完了後に生成計画を確定してから書き込みを始めます。mainの既存の原子的ファイル書き込み方式を再利用し、**各ファイル単位**で一時ファイルから置き換えます。全ディレクトリをまたぐ一括トランザクションを保証するものではありません。

子一覧を先に書き、すべて成功したあとにルート一覧を最後に書きます。途中で失敗した場合、新しいルート一覧を成功結果として公開せず、失敗パスと既に書いたパスを返します。既存ルート一覧がある場合は保持しますが、既に置き換えた子一覧まで巻き戻せるとは表示しません。探索中のアクセス拒否は、全CDLを列挙できていないため正常完了にしません。

## 7G.4 IPC契約案

```ts
type CdlFileListPlan =
  | { kind: 'planned'; planId: string; items: { path: string; status: 'new' | 'same' | 'differs' }[] }
  | { kind: 'empty' }
  | { kind: 'failed'; path: string; detail: string };

type CdlFileListResult =
  | { kind: 'ok'; rootListPath: string; listCount: number; skippedSame: number }
  | { kind: 'empty' }
  | { kind: 'changed'; path: string } // 計画後に既存の一覧が変わった。何も書き込まない
  | { kind: 'failed'; path: string; detail: string; writtenPaths: string[] };

// shared/ipc-types.ts → main/ipc.ts → preload/index.mts
// → renderer/gateways/file-gateway.ts
planCdlFileLists(root: string): Promise<CdlFileListPlan>;
applyCdlFileLists(planId: string): Promise<CdlFileListResult>;
```

チャネル案は`file:planCdlFileLists`と`file:applyCdlFileLists`です。`applyCdlFileLists`は、書き込み前に既存内容のハッシュが計画時と同じか再検査し、変わっていれば`changed`を返して何も書き込みません（確認から書き込みまでの間の変更への対策）。`planId`はmainが保持する短命の値で、検証できないIDは拒否します。main側でも入力が空でない文字列か、ディレクトリとして利用できるかを確認します。同じ生成処理の二重開始を抑止し、処理中はボタンを無効にします。成功時だけフルパスと件数を結果欄へ入れ、0件と失敗は個別に説明します。設定の取得・保存は9Dの設定APIで共用します。

`_ROOT_CDL_FILES.txt`はこの版では**作成のみ**です。importの探索、セッション復元、ファイルを開く動作に新しい読み込み経路を追加しません。

## 7G.5 実装時の受入確認

- ルート直下・複数階層・CDLなしの中間階層・空白や日本語のパスで、子一覧の名前とルート一覧のフルパスが一致します。
- CDLなしなら既存一覧を含め変更がありません。成功時の子一覧件数が正しく、生成した一覧が再探索でCDLとして扱われません。
- 存在しないルート、アクセス拒否、子一覧書き込み失敗、ルート一覧書き込み失敗を正常完了にしません。途中書き込みの結果を検証します。
- 上書き確認（2026-11-08追加）: 内容が同一の一覧は書き込まれず`skippedSame`に数えられること、内容が異なる既存の一覧がある場合のみ確認が必要になること、キャンセルで何も変わらないこと、計画後に既存の一覧が変わったら`changed`で中止すること。
- 並び順（同追加）: 大文字小文字、日本語、深さの異なるパスで、子一覧とルート一覧の並びがOSとロケールに依存せず一定であること。ディレクトリのリンクを辿らず循環しないこと。
- 既存設定の未知項目と`fileBrowserRoot`を保持し、対象ディレクトリの変更が即時反映されます。
- mainの一時ディレクトリを使うテストは`tests/main/`、ダイアログ表示は`tests/renderer/`、実機記録は`tests/verification/`に置きます。TBCの試験期待値は確定後に補います。

## Related

- [[TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計]]
- [[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]
- [[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理]]
- [[TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧]]

- [[TECSCDE-DT-EL内部仕様 - 監査対応 09-18 読み込みと設定]] — 該当する監査項目の契約補足（2026-11-09）。

---
date: 2026-10-19
description: "Ruby版tecsgen V1.7.0→V1.8.0 の新機能・仕様変更・削除・不具合修正の一覧。出典はSVN tags/tecsgen-1.8.0 の doc/changes.txt"
tags:
  - reference
  - tecs
  - tecsgen
---

# tecsgen V1.7.0 → V1.8.0 新機能

- 出典: `https://dev.toppers.jp/svn/tecs/toppers/tecsgen/tags/tecsgen-1.8.0/doc/changes.txt`（1.8.0RC13 〜 1.7.0RC1 直前の範囲、取得 2026-10-19）
- 対象リビジョン: 1.7.0 = r3087（2019-06-14）、1.8.0 = r3252（2022-01-22）。リビジョンの対応は [[tecsgen-VCS]]、ログ取得コマンドは [[svn-diff]] を参照
- `#` は公式の変更管理番号。番号なしの項目は公式に番号がない
- `changes.txt` の記述に基づく一覧で、ソース差分での検証は未実施 (unverified)

## 新機能・仕様変更

- **FMP3・HRMP3（マルチプロセッサ版）対応**
  - FMP3 用セルタイププラグイン `FMPObjectPlugin`・`FMPHandlerPlugin`・`FMPPlugin` を新設
  - HRMP3 向けに `HRMPPlugin`・`HRMPDomainPlugin`・`HRMPClassPlugin`・`HRMPKernelObjectPlugin` を追加（#1196、#1197）
  - `NotifierPlugin` を FMP クラスに対応
  - `__tool_info__( "HRMP_class_def" )` でクラス定義（RC6）
  - ATT_MOD をクラスごとに出力（RC7）。出力コードは HRP3 と共通化
  - 新設の `ClassPlugin` が V1.7.0 から 1.8.0 までに加わった（`changes.txt` には個別記述なし、SVN の差分で追加を確認）
  - HRMP3 でどのクラスにも属さないものの既定を `global` から `root` に変更（#1208）
- **リージョンの class 指定子**に対応（#1176）
- **WSL 対応**（#1175）。WSL2 でのテストビルドエラーは RC13 で修正（#1216）
- **拡張サービスコールのローダブルモジュール対応**（#1198）
  - `HRPSVCPlugin` を `HRPSVCThroughPlugin` に変更し、`HRPSVCBodyCellPlugin` と `HRPSVCSignaturePlugin` に分解
  - `HRPSVCPlugin.rb` は 1.8.0 で消える（[[tecsgen-VCS]] の記録と一致）
- **受け口の `through` 指定子**（#1193）
- **リージョン間の `from_through`**（#1192）
- `SignaturePlugin` が、スルーするセルを生成（受け口から呼び口を呼び出す、#1194）。`ThroughPlugin` はこれを利用する実装に変更（#1195）
- スループラグインの `set_through_info` 後のフック `set_through_info_hook` を新設
- セルタイプの **`pseudo_active` 指定子**（#1191）。`active` と同じ扱いで、受け口への結合がない警告を抑制
- `struct` の初期化子に **`C_EXP`** を指定可能（#1209）
- **コメント記法**（実験的仕様）: 行頭の `+---` から行頭の `---+` までをコメントにする（#1190）
- **mruby 3.0 対応**（#1199）
  - `tMruby.cdl` の factory が生成する依存関係を `tecs.timestamp` から `$(GEN_DIR)/tecsgen.timestamp` に変更
  - TLSF と mruby VM のヒープの統計情報を取得可能（`tTLSFMalloc`、`tMruby`）
- RPC の ASP3 対応
  - `tDataqueueOWChannel.cdl`・`tMessageBufferChannel.cdl` を ASP3 対応
  - `RPCPlugin` が生成する `tSemaphore`・`tTask` の属性名を ASP3 用に変更
- **`import_C` の強化**
  - 構文解釈の対象を `typedef`・`struct`・`union`・`enum` に限定（#1211）
  - `struct` 末尾の添字なし配列に対応（#1212）
  - ビットフィールドは無視して読み込む（#1212）
  - 取り込むヘッダの `typedef` 内の `sizeof` をエラーにしない（#1212）
  - `enum` の enumerator list が `,` で終わる場合の構文エラーを修正（#1181）
- **TECSInfo** が、構造体の不完全型・添字なしメンバー・関数型に対応（#1213）

## 互換性が失われる変更（★）

- `linkUnit` や `node` を指定したリージョンは `OutOfDomain` でなければエラー（#1206）

## 取りやめ・削除

- `__location_information__`（古い tecscde のデータ記述）を削除
- 次の項目は RC の途中で追加したが、最終的に取りやめ
  - `restrict_class` 指定子
  - `class_free` 指定子
  - `SelectiveJoinPlugin` 系
  - クラス名指定子としての `global`

## 主な不具合修正

- `~0` を unsigned にキャストしても -1 になる問題。`import_C` の `int32_t`・`uint32_t` が int 扱いになる問題
- ドメイン外ノードの `TECS_COBJS` などが出力されない問題
- `node` 指定リージョンが、親のドメインやクラスをルートとして扱う問題
- `RPCPlugin` が複数のチャンネルセルに対応できない問題（#1182）
- HRMP3 で `tCelltype_tecsgen.o` がリンク対象に入らないことがある問題（#1207）
- Ruby 3.0 対応（#1186、#1187）。racc の引数順の誤りも修正（#1188）
- 全角文字で tecsgen が Ruby 例外になる問題（#1205）
- `void` の `const`・`volatile` 修飾で Ruby 例外になる問題（#1210）
- `composite` 内の `C_EXP` で `$id$` などの置換が `global_name` にならない問題（#1184）

## 内部変更（抜粋）

- `Struct#get_members_decl` が不完全型で `nil` ではなく空の `NamedList` を返す（#1214）。TECS CDL は不完全型の構造体を許さないが、`import_C` は許す
- 式の評価を一度だけにして警告の多重表示を避ける（#1215）

## Related

- [[tecsgen V1.8.0-V1.9.0 新機能]] — 次の版の差分
- [[tecsgen-VCS]] — バージョンとリビジョンの対応、`HRPSVCPlugin.rb` 消滅の記録
- [[svn-diff]] — タグ間のログ取得コマンド控え
- [[tecsgen-inner-spec]] — tecsgen 内部仕様

---
date: 2026-08-15
description: "tecsgen 標準付属プラグイン DataPumpHolderPlugin・TransparentMarshalerPluginの仕様書。trunk r3301更新で新規に出現した2ファイル。DataPumpHolderPluginが生成するCDLが参照するTransparentRPCSignaturePluginというクラス名が現行コードベースのどこにも存在しないという未解決の参照切れを発見"
project: TECS
quarter: Q3-2026
status: active
tags: [work-note, tecs, tecsgen, spec, plugin]
---

# DataPumpHolderPlugin / TransparentMarshalerPlugin 仕様書

> [!info] 文書状態
> ユーザー指示「tecsgenのtrunkの最新の状態を元に、tecsgen プラグイン仕様書を更新して」を受けて、`E:\Crepo\ykominami-svn-2\tecsgen\`のSVN作業コピーを確認した結果、**リビジョン3301（2026-01-13、これまでの調査で見た最新の`$Id`より新しい）**に更新されていた。[[work/active/tecsgen-plugins/PluginCoverageAudit|プラグインカバレッジ監査]]（2026-08-15実施）時点の83ファイルから**85ファイルへ増加**しており、`DataPumpHolderPlugin.rb`（845行、`$Id`リビジョン3300・2026-01-04）・`TransparentMarshalerPlugin.rb`（85行、`$Id`リビジョン2952・2018-05-07）の2ファイルが新規に出現していた。本ノートはこの2ファイルを対象とする。

## 1. DataPumpHolderPlugin: データ生成側/消費側を疎結合にする2セルタイプ＋2シグニチャの合成生成

`DataPumpHolderPlugin < CelltypePlugin`。この調査シリーズで唯一、**ソースファイル自身に`=begin...=end`の長大な設計ドキュメントが埋め込まれている**プラグイン——他のほぼ全プラグインが一次資料ゼロだったのと対照的。

### 1.1 目的と分類

属性（読み取り専用データ）・変数（読み書き可能データ）を持つセルタイプに`[generate(DataPumpHolderPlugin,"")]`を付与すると、そのデータを「生成する側」と「消費する側」の間で受け渡すための、以下2シグニチャ・複数セルタイプの一式が自動生成される。

| シグニチャ | 用途 |
|---|---|
| Get シグニチャ | データを消費する側が生成側からデータを受け取る |
| Set シグニチャ | データを生成する側が消費側へデータを送出する |
| SetAsync シグニチャ | RPCバッファリングを介する非同期版のSet |

ソースコード内のドキュメントコメントが、生成側・消費側それぞれの口タイプ（呼び口/受け口）の組み合わせから4分類（CI〜CIV型）を定義し、必要な中間構造（直接結合／データポンプ＋データホルダ／データホルダのみ／データポンプのみ）を規定している——**セルタイプの属性/変数宣言という「データの形」の情報だけから、生産者・消費者間の結合トポロジーに応じた複数の実装パターンを自動選択して展開する**、この調査で見た中でも最も複雑な合成生成プラグイン。

### 1.2 生成されるセルタイプ群

`gen_pump_holder_celltype`（280〜579行）が1回の呼び出しで生成する内容:

- `<name>DataPump` / `<name>DataHolder` — 基本のポンプ・ホルダセルタイプ
- `<name>SyncAdaptor` / `<name>AsyncAdaptor` — Set呼び出しの同期/非同期変換アダプタ
- `<name>DataPumpHolder`（composite） — ポンプ＋ホルダを組み合わせた複合セルタイプ
- `<name>DataHolderSync`・`<name>DataPumpHolderSync`（composite） — Eventflagによる同期制御を追加した版
- `<name>DataPumpBuffered`・`<name>DataHolderBuffered`・`<name>DataPumpHolderBuffered`（composite、`[active]`） — RPCチャンネル経由でSet呼び出しをバッファリングする専用タスクを持つ版
- 同じくBuffered＋Sync両方を組み合わせた版

——1つの`[generate(DataPumpHolderPlugin,"")]`から、同期・非同期・バッファリングの組み合わせだけで10種類近いセルタイプ/合成セルタイプが自動生成される。

### 1.3 RPCマーシャリング機構との統合

Bufferedバリアントは`tRPCPluginDPH_tTDR_tDataqueueOWChannel_<SetAsyncシグニチャ名>`という命名規則のセルタイプを使う——`DPH`（DataPumpHolder）という接頭辞から、RPCチャンネルインフラがこのプラグイン専用に自動命名されて生成されると分かる。生成されるCDLの中で以下の呼び出しが埋め込まれている：

```cdl
generate(TransparentRPCSignaturePlugin, #{@set_signature_async}, "PPAllocatorSize=128,DataPumpHolder=true");
```

——`DataPumpHolder=true`という専用オプションを付けて、[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]]系のマーシャラ生成機構を呼び出している（2節・3節参照）。

### 1.4 発見: `mikan`コメント・軽微なタイポ

`gen_ep_func_body`（582〜809行）に、この調査シリーズで繰り返し見てきた「mikan」（未完成）系コメントが再び現れる：

```ruby
// mikan: need error check
cPubSide_waitForNewData();
cSubSide_waitForReadDone();
...
/// mikan: need error check
cPubSide_dataReadDone();
cSubSide_newDataReady();
```

——生成される受け口関数の中で、Sync/Async制御呼び出しのエラーチェックが省略されていることを著者自身が把握している。加えて、`gen_pump_holder_celltype`のコメント文字列中に`@datholder_celltype`という綴りミス（正しくは`@dataholder_celltype`、286行のコメントのみで実際のコード変数参照ではないため実害はない）も見つかった——[[work/active/tecsgen-plugins/TracePlugin|TracePlugin]]の`@b_diplayTime`ほど深刻ではない、コメント内タイポ。

## 2. TransparentMarshalerPlugin: TransparentRPC用マーシャラ／アンマーシャラ生成

`TransparentMarshalerPlugin < SignaturePlugin`。`GenTransparentMarshaler`・`GenParamCopy`という共有モジュールを`include`し、[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]]（Transparent方式RPC）が使うマーシャラ/アンマーシャラセルタイプの生成本体を担う——ファイル自体は`$Id`リビジョン2952（2018年）と古く、[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]]執筆時（2026-08-14）には把握されていなかった、実装の裏側を担う補助プラグインだった。

## 3. 発見: 存在しないクラス名`TransparentRPCSignaturePlugin`への参照——2箇所で共有される未解決の参照切れ

`DataPumpHolderPlugin`が生成するCDL（1.3節）と、[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin.rb]]自身の`gen_marshaler_celltype_`メソッド（195〜201行）が、**どちらも`generate(TransparentRPCSignaturePlugin, ...)`という同一のクラス名を呼び出している**：

```ruby
# RPCPlugin.rb 内
def gen_marshaler_celltype_ file
  file.print <<EOT
generate( TransparentRPCSignaturePlugin, #{@signature.get_namespace_path}, "#{@plugin_arg_str}");
import( "#{@marshaler_celltype_file_name}" );
EOT
end
```

しかし`tecslib/plugin/`全85ファイルおよびリポジトリ全体を`TransparentRPCSignaturePlugin`で検索しても、**この名前のクラス定義もエイリアス代入も一切存在しない**（実際に定義されているのは`TransparentMarshalerPlugin`という別名のクラス）。つまり——

- `RPCPlugin`のTransparent方式マーシャラ生成が実行された場合
- `DataPumpHolderPlugin`のBuffered系合成セルタイプが実際にコンパイルされた場合

のいずれも、`TransparentRPCSignaturePlugin`というプラグインをロードしようとして失敗するはずのコードパスが、**2箇所独立に埋め込まれている**。単発の見落としではなく、同じ誤ったクラス名が複数箇所で共有されている——`TransparentMarshalerPlugin`がかつて`TransparentRPCSignaturePlugin`という名前だった時期にリネームされ、生成コード側の文字列リテラルだけ追随できなかった、という説明が最も自然だが、確証はない。この調査シリーズで見つけてきた「$Id不一致」のような静的なメタデータの矛盾ではなく、**実行時に初めて顕在化する可能性のある参照切れ**という点で、これまでの発見とは性質が異なる。

## 4. 制約・注意点

- 3節の参照切れが実際にtecsgenの実行時エラーとして発現するかは、実際にコンパイルを走らせて確認していない——ソースの静的な突き合わせのみに基づく指摘。
- DataPumpHolderPluginのCDL実例はリポジトリ内に見つからず、ドキュメントコメント中の使用例からの理解にとどまる。
- `GenTransparentMarshaler`・`GenParamCopy`（`TransparentMarshalerPlugin`がincludeする共有モジュール）自体の中身は未読。
- SVN作業コピーはリビジョン3301（2026-01-13）時点。今後さらにtrunkが進んだ場合は、本ノートの前例に倣い`svn info`でリビジョンを確認し、ファイル数の差分を突き合わせてから着手する。

## Related

- [[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]] — Transparent方式RPCの本体、3節の参照切れを共有する既存ノート（要追記）
- [[work/active/tecsgen-plugins/PluginCoverageAudit|プラグインカバレッジ監査]] — 83ファイル時点の完全ファイル一覧、本ノートが更新する基準点
- [[tecsgen外部仕様]] — 6.3 標準付属プラグイン一覧
- [[North Star]] — プラグイン仕様書化の進捗管理

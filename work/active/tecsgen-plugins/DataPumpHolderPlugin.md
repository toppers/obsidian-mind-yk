---
date: 2026-08-15
description: "tecsgen 標準付属プラグイン DataPumpHolderPlugin・TransparentMarshalerPlugin・TransparentRPCSignaturePluginの仕様書。前2者は trunk に r3302（release 1.9.1）で追加。TransparentRPCSignaturePlugin は r3306 まで trunk に無く参照切れに見えたが、r3307（2026-10-21）で追加され解消（SVN履歴調査、2026-10-22）"
project: TECS
quarter: Q3-2026
status: active
tags: [work-note, tecs, tecsgen, spec, plugin]
---

# DataPumpHolderPlugin / TransparentMarshalerPlugin 仕様書

> [!info] 文書状態
> ユーザー指示「tecsgenのtrunkの最新の状態を元に、tecsgen プラグイン仕様書を更新して」を受けて、`E:\Crepo\ykominami-svn-2\tecsgen\`のSVN作業コピーを確認した結果、**trunk r3302（2026-06-07）以降の状態**に更新されていた（当初は「リビジョン3301（2026-01-13）」と記録したが、r3301 は trunk のリビジョンではなく`branches/DataPumpHolder`のコミット。作業コピーの実際のリビジョンは不明 (TBC)。2026-10-22 訂正）。[[PluginCoverageAudit(AIが説明用に利用)|プラグインカバレッジ監査]]（2026-08-15実施）時点の83ファイルから**85ファイルへ増加**しており、`DataPumpHolderPlugin.rb`（845行、`$Id`リビジョン3300・2026-01-04）・`TransparentMarshalerPlugin.rb`（85行）の2ファイルが新規に出現していた（trunk への追加は r3302。`TransparentMarshalerPlugin.rb` 内の`$Id`は「2952・2018-05-07」だが、これはこのファイル自身のコミットを指さない——2節の履歴参照）。本ノートはこの2ファイルを対象とし、3節で、のちに trunk へ追加された`TransparentRPCSignaturePlugin.rb`（r3307）も扱う。

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

`TransparentMarshalerPlugin < SignaturePlugin`。`GenTransparentMarshaler`・`GenParamCopy`という共有モジュールを`include`し、[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]]（Transparent方式RPC）が使うマーシャラ/アンマーシャラセルタイプの生成本体を担う——[[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]]執筆時（2026-08-14）には把握されていなかった、実装の裏側を担う補助プラグイン。マーシャラ／アンマーシャラのセルタイプだけを生成し、RPCチャンネルのセルタイプは生成しない（チャンネル側は3節の`TransparentRPCSignaturePlugin`）。

**SVN履歴**（2026-10-22 調査、`E:\Crepo\ykominami-svn-2\tecsgen`）: このファイルのコミットは次の2件のみ。

| rev | 日付 | 場所 | 操作 |
|---|---|---|---|
| r3145 | 2020-05-04 | `branches/tecsgen-fmp3-hrmp3` | 追加（release 1.D.4。`FMPRPCPlugin.rb`・`lib/FMPClassManager.rb` と同時） |
| r3302 | 2026-06-07 | `trunk` | 追加（release 1.9.1。`DataPumpHolderPlugin.rb` と同時） |

ファイル内の`$Id: ... 2952 2018-05-07`は、このファイルのコミットを指さない（r2952 で変更されたのは`lib/GenTransparentMarshaler.rb`のみ）。追加時に古い展開済みの文字列が残ったものと考えられる（推測）。「2018年の古いファイル」ではない。

## 3. TransparentRPCSignaturePlugin: 参照されていたが r3306 まで trunk に無かったクラス（r3307 で解消）

> [!warning] 訂正（2026-10-22）
> 本節は当初「`TransparentRPCSignaturePlugin`はコードベースのどこにも存在しない参照切れ」「`TransparentMarshalerPlugin`の旧名で、リネーム時に生成コード側が追随しなかった」と記述していた。**どちらも誤り**。実際は svn への追加漏れで、**trunk r3307（2026-10-21、release 1.10.A1）で`TransparentRPCSignaturePlugin.rb`が追加され解消**した（`doc/changes.txt`: 「MANIFEST登録済みで、パッケージには含まれていた」）。`TransparentMarshalerPlugin`は旧名ではなく、別クラスとして併存する。以下の記述は、r3306 時点で見えていた状況の記録として残す。

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

**（r3306 時点）** `tecslib/plugin/`全85ファイルおよび作業コピー全体を`TransparentRPCSignaturePlugin`で検索しても、この名前のクラス定義もエイリアス代入も存在しなかった。つまり——

- `RPCPlugin`のTransparent方式マーシャラ生成が実行された場合
- `DataPumpHolderPlugin`のBuffered系合成セルタイプが実際にコンパイルされた場合

のいずれも、`TransparentRPCSignaturePlugin`というプラグインをロードしようとして失敗するはずのコードパスが、2箇所独立に埋め込まれているように見えた（当時の推測）。

### 3.1 実際の経緯（SVN履歴、2026-10-22 調査）

`TransparentRPCSignaturePlugin.rb`は`branches/DataPumpHolder`で開発されていた。

| rev | 日付 | 場所 | 内容 |
|---|---|---|---|
| r3287 | 2025-08-09 | `branches/DataPumpHolder` | 追加（`lib/GenTransparentMarshaler.rb`も変更） |
| r3289 | 2025-08-13 | 同上 | 変更 |
| r3300 | 2026-01-04 | 同上 | 変更（`$Id`はこのリビジョン） |
| r3307 | 2026-10-21 | `trunk` | 追加（release 1.10.A1） |

- 役割: RPCチャンネルのセルタイプ（`tRPCPlugin[DPH]_..._ClientSide`／`_ServerSide`等の composite）を生成する`SignaturePlugin`。オプション`noClientSemaphore`・`semaphoreCelltype`・`DataPumpHolder`を持ち、`DataPumpHolder=true`のとき名前に`DPH`が付く。マーシャラ生成（`gen_marshaler_celltype`）は`GenTransparentMarshaler`に任せる。
- `TransparentMarshalerPlugin`とは別クラス。r3302（trunk に`DataPumpHolderPlugin`と同時に追加）の時点では`TransparentRPCSignaturePlugin.rb`だけが trunk に入っていなかった。
- 未確認: r3307 のファイルの全体（`RPCPlugin`との責務分担の詳細）は読み切っていない。

## 4. 制約・注意点

- 3節の参照切れ（r3306 時点）が実際にtecsgenの実行時エラーとして発現するかは、コンパイルを走らせて確認していない。r3307 で解消済みのため、今後は確認不要。
- DataPumpHolderPluginのCDL実例はリポジトリ内に見つからず、ドキュメントコメント中の使用例からの理解にとどまる。
- `GenTransparentMarshaler`・`GenParamCopy`（`TransparentMarshalerPlugin`がincludeする共有モジュール）自体の中身は未読。
- 本文の調査は SVN作業コピーが trunk r3302〜r3306 だった時点（当初「3301」と記録、r3301 は trunk のリビジョンではないため訂正）。2026-10-22 に r3307 へ更新済み。今後さらにtrunkが進んだ場合は、本ノートの前例に倣い`svn info`でリビジョンを確認し、ファイル数の差分を突き合わせてから着手する。

## Related

- [[work/active/tecsgen-plugins/RPCPlugin|RPCPlugin]] — Transparent方式RPCの本体、3節の参照切れを共有する既存ノート（要追記）
- [[PluginCoverageAudit(AIが説明用に利用)|プラグインカバレッジ監査]] — 83ファイル時点の完全ファイル一覧、本ノートが更新する基準点
- [[tecsgen外部仕様]] — 6.3 標準付属プラグイン一覧
- [[North Star]] — プラグイン仕様書化の進捗管理

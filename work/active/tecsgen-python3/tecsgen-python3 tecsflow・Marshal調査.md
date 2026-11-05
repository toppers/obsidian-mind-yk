---
date: 2026-10-09
description: "Ruby版tecsgenでMarshalを使う箇所(tecsgen.rbdmp・tcflow.rbdmp)の調査と、tecsflow.rb:452の無駄なload_funclistをWSLで実行確認した結果。tecsflow移植(2026-10-14完了)の前提資料と設計メモ"
project: tecsgen-python3
status: active
quarter: Q4-2026
tags:
  - work-note
  - reference
---

# tecsgen-python3 tecsflow・Marshal調査

[[tecsgen-python3]] の周辺調査です。Ruby 版 tecsgen の `Marshal` 利用箇所と、`tecsflow.rb:452` の不要な呼び出しを調べました。対象は SVN 作業コピー `E:\Crepo\ykominami-svn-2\tecsgen\trunk\tecsgen`(リビジョン未確認)です。

## 位置づけ

- **2026-10-14 に方針を変更しました**: `tecsflow` を移植し、`tecsgen.rbdmp`(Marshal)は書かない代わりに、tecsgen が `gen/tecsgen.pickle` を書きます(ユーザー決定)。`tcflow` は 2026-10-13 に移植済みです(下の「tcflow の保存形式」)。実装(`tecsgen/tecsflow.py`・`core/unjoin_plugin.py`)は Python リポジトリの PR #3(マージコミット `85731c2`)で `main` にマージ済み。TECS の test/ 8ケースで Ruby 版と出力が一致、WSL で全件 pass(1101 passed)。→ 状況の単一ソースは [[tecsgen-python3移植計画]]。関連: [[tecsgen-python3外部仕様 - 04 出力]]・[[tecsgen-python3外部仕様 - 08 制約・制限]]
- 下の「pickle 形式で dump する場合」の設計は、`__getstate__` ではなく `pickle.Pickler` の `reducer_override` で実装しました(モデルクラスを変更しないため)。`Plugin` の残存は例外ではなく `None` に置換します。`_pluginClass` も併せて消します。

## Marshal の使用箇所(trunk)

標準の `Marshal` を使うのは次の3系統だけです。`YAML` と `PStore` は使っていません。

| 用途 | 場所 | 内容 |
|---|---|---|
| tecsgen 本体が出力 | `tecslib/core/tecsgen.rb:499`(`dump_tecsgen_rbdmp`、呼び出し元 `tecsgen.rb:599`) | `Marshal.dump(Namespace.get_root)` を `$gen/tecsgen.rbdmp` に書く |
| tcflow の関数リスト | `flowlib/classes.rb:392-402`(`dump_funclist`・`load_funclist`) | `@@Function_list` を `tcflow.rbdmp` に書き、読み戻す。呼び出し元は `tcflow.rb:92`(load)・`tcflow.rb:129`(dump) |
| tecsflow が読み込み | `tecsflow.rb:454` | `$root_namespace = Marshal.load(mar_in)` で `tecsgen.rbdmp` を読む。`tecsflow.rb:467` の同様の行はコメントアウト済み |

- **Marshal 対策:** `tecslib/core/unjoin_plugin.rb:44-49` で `Proc#_dump_data` を `nil` を返す形で再定義しています。`Proc` は標準では `Marshal.dump` できないためです。同ファイルには Plugin 関係のオブジェクトを消す処理もあります(tecsflow 側に `Plugin` クラスがないため)。
- **ファイル受け渡し:** Makefile 生成(`tecslib/core/generate.rb:517-525`)で `tecsgen.rbdmp`・`tcflow.rbdmp` を依存ファイルにしており、tecsgen・tcflow・tecsflow の間の受け渡しが `Marshal` です。
- **branches:** `branches/TECS-flow`・`branches/DataPumpHolder` にも同じコードがあります。

## tecsflow.rb:452 の load_funclist

`TCFlow::Function.load_funclist $tecsgen_dump_file_name`(`tecsflow.rb:452`)は無駄な呼び出しです。

- `tecsgen.rbdmp` の中身は Namespace であり、`Hash` ではありません。それが `@@Function_list` に代入されます。
- 戻り値は捨てられ、`@@Function_list` は `tecsflow.rb:468` の `load_funclist $tcflow_dump_file_name` で上書きされます。その間に `@@Function_list` を使う処理は走りません。
- 同じファイルを3回(`File.read`・`load_funclist` 内の `File.read`・`Marshal.load`)読んでいます。
- 原因は、旧コード(`tecsflow.rb:465-467` にコメントアウトで残存)を `load_funclist` に置き換えた際の混入と見られます (inferred)。

### 実行による確認(2026-10-09)

- 環境: WSL Ubuntu、Ruby 3.2.3、gcc 13.3。
- 対象: trunk の `samples/SimpleSample` 1ケース。作業コピーは触らず `/tmp/tf/` に2組コピーし、片方だけ452行を削除。
- 手順: 両方で `make tecs` → `make tecsflow` を実行して比較。

| 比較対象 | 結果 |
|---|---|
| 終了コード | どちらも 0 |
| `tecsflow` の標準出力(80行) | 一致(違いは作業ディレクトリのパスのみ。置換して正規化すると完全一致) |
| 標準エラー出力(5行) | 完全一致 |
| `tecsgen.rbdmp`・`tcflow.rbdmp` | `cmp` で完全一致 |

- **結論:** 452行を消しても出力は変わりません。tecsflow を移植する場合、この呼び出しは再現しなくて構いません。
- **限界:** 確認は1ケースのみで、複数リージョンなどは未確認です。ただし 452 行の効果は 468 行で必ず上書きされるため、構成に依存する経路は見当たりません。

### 副次的な観察

- `tcflow` が gcc 13 の `stddef.h`(214行目)で `syntax error near 'typedef'` を出します。C パーサがこのヘッダを解釈できないためで、452行の有無とは無関係です。

## tecsflow を移植する場合の前提

- `tecsgen.rbdmp`(Namespace)と `tcflow.rbdmp`(関数リスト)の2種類があり、前者を tecsgen が書き、後者を tcflow が書きます。tecsflow は両方を読みます。
- `Marshal` 形式は Ruby 固有で、`pickle` へ直接は置き換えられません。形式を決めて、tecsflow 側もまとめて移植する必要があります。
- `flowlib/C_parser.tab.rb` は racc 生成物です。[[tecsgen-python3 構文解析方式決定]] と同じく表駆動の移植が要ります。

## tcflow の保存形式(2026-10-13、決定)

`tcflow` を移植した際、関数リスト(`tcflow.rbdmp`、Marshal 形式)は **JSON(`gen/tcflow.json`)** に置き換えると決めました(ユーザー決定。pickle・Ruby Marshal 互換の自前実装は採りません)。言語に依存せず、Ruby オラクルが書き出した JSON とそのまま突き合わせられるためです。

- 構造: `{関数名: {"param_var": [...], "local_var": [...], "global_var": {名前: [読み取り回数, 書き込み回数]}, "call_func": {名前: 名前 または 0}, "b_ref": bool, "locale": [ファイル, 行, 桁]} または 0}`。キーは挿入順で、`0` は「呼ばれたが定義が無い」関数です。
- tecsflow を移植するときは、この JSON を読む側を足します。`tecsgen.rbdmp`(Namespace)は引き続き書きません。下の pickle の設計は、tecsgen 本体の dump が必要になった場合の備えで、tcflow の決定とは別です。
- 実装と差分テストは Python リポジトリの `src/tecsgen/flowlib/`・`tests/test_p7_tcflow.py`・`tests/golden/tcflow/`。

## pickle 形式で dump する場合の `unjoin_plugin` 相当の設計(2026-10-14、実装済み)

2026-10-14 に tecsflow を移植して pickle で受け渡すと決めたため、実装しました(下の注記参照)。`unjoin_plugin.rb`(r3304 trunk)を読んで検討した結果です。

- **必要性:** Python の `pickle` も lambda・ローカル関数・ファイルハンドル・ジェネレータ・ロックを dump できません。Plugin が `generate` などに持っていれば同じ問題が起きます。一方「tecsflow に Plugin クラスが無い」という Ruby 側の理由は、同じパッケージを import できるので弱まります。ただし Plugin 配下の巨大なオブジェクトを dump に含めたくない点は変わりません。
- **方式の違い:** Ruby の `unjoin_plugin` は生きたオブジェクトを破壊的に書き換えるため、`dump_tecsgen_rbdmp` を最後に呼ぶ必要がありました。Python では `__getstate__` で dump 用の dict コピーだけを差し替えれば、元のオブジェクトを壊さず、呼び出し順の制約もありません。
- **対応表:**

| Ruby | Python |
|---|---|
| `Signature`・`Celltype`・`CompositeCelltype`・`Cell`・`DomainType` の `@generate = nil`・`@generate_list = []`・`@plugin = nil` | `UnjoinMixin` の宣言表 `_UNJOIN_RESET`(属性名 → 置換値の生成関数)を `__getstate__` が適用 |
| `Join`・`Region` の Plugin オブジェクト → `Join::ThroughPluginProxy` | 各クラスの `__getstate__` で、`get_cell_namespace_path`・`get_through_entry_port_name`・`get_through_entry_port_subscript` の値だけを持つ `ThroughPluginProxy`(frozen dataclass、モジュール直下)へ変換 |
| `Namespace#unjoin_plugin` の再帰、`Join#unjoin_plugin2` | 不要(`pickle` がオブジェクトグラフを辿り、各要素の `__getstate__` を呼ぶ) |
| `Proc#_dump_data` を nil にする | `pickle.Pickler` のサブクラスの `reducer_override` で、lambda・`<locals>` 内関数を `None` を返す関数に置換 |
| `Object#find_plugin_1`(残存 Plugin の探索。呼び出しはコメントアウト済み) | 同 Pickler の `persistent_id` で `Plugin` インスタンスを検出したら例外にする |

- **注意:** 深いグラフでは `RecursionError` になりうるため `sys.setrecursionlimit` を検討します。`ThroughPluginProxy` は pickle から参照できるようモジュール直下に置きます。pickle できない属性の洗い出しは、移植後に Pickler で例外を出して実測します(`_UNJOIN_RESET` に入れる属性は実測で確定する (unverified))。
- 関連: [[tecsgen-python3 パッケージ構成決定]]・[[tecsgen-python3 Mixin粒度決定]](`unjoin_plugin.py` は機能別 Mixin の1つ)。

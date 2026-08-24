---
date: 2026-08-15
description: "tecsgen 標準付属プラグイン RepeatCellPlugin・RepeatJoinPluginの仕様書。セル名末尾の数字を自動インクリメントしてN個の複製を生成する繰り返し生成機構。同じ目的をCDLテキスト再生成と直接モデル操作という異なる手段で実現する対比が判明"
project: TECS
quarter: Q3-2026
status: active
tags: [work-note, tecs, tecsgen, spec, plugin]
---

# RepeatCellPlugin / RepeatJoinPlugin 仕様書

> [!info] 文書状態
> [[work/active/tecsgen-plugins/TECSInfoPlugin|TECSInfoPlugin]]（2026-08-15）に続き、[[work/active/tecsgen-plugins/PluginCoverageAudit|プラグインカバレッジ監査]]で見つけた最後の候補に着手。両プラグインは[[tecsgen外部仕様]] 6.3表に最初から名前が載っていたが、個別の詳細仕様化は一度もされていなかった（「カタログには載せたが本文を書き忘れていた」ギャップ）。一次資料は`tecslib/plugin/RepeatCellPlugin.rb`（169行）・`RepeatJoinPlugin.rb`（131行）の計2ファイル。**これで[[work/active/tecsgen-plugins/PluginCoverageAudit|カバレッジ監査]]が挙げた4候補すべてが完了する**。

## 1. 共通する目的: セル名末尾の数字を自動インクリメントして複製する

両プラグインとも`< CellPlugin`で、セルに`[generate(RepeatCellPlugin, "count=N")]`のように付与して使う。**セル名が数字で終わっていることを前提**に、その数字部分をカウントアップしながら`count`個の複製を作る、という共通の設計思想を持つ。ただし実現手段がまったく異なる（2・3節）。

`count`オプションの解析（`set_count`）は両ファイルで完全に同一のコード——数値リテラルならそのまま、そうでなければCDL上の定数識別子として`Expression.create_single_identifier`＋`eval_const`で評価する：

```ruby
def set_count rhs
  if rhs =~ /\A\d+\z/
    @count = rhs.to_i
  else
    nsp = NamespacePath.new( rhs.to_sym, true )
    expr = Expression.create_single_identifier( nsp, nil )
    res = expr.eval_const( nil )
    @count = ( res == nil ) ? 0 : res
  end
end
```

——`count=8`のような即値だけでなく、`count=N_WORKERS`のようにCDL上で定義された定数を使うこともできる。

## 2. RepeatCellPlugin: CDLテキストを新規生成して再取り込みする方式

`gen_cdl_file`（66〜150行）が、**繰り返し生成したセルの定義をCDLソーステキストとして書き出す**。付与元のセル名（例: `Worker0`）の末尾の連番を基準に、`Worker1`・`Worker2`…と`count`個分のセル定義を`cell <celltype名> <新セル名>{ ... };`という完全なCDL構文で出力する。

各セルが持つ結合（join）の右辺も追随して書き換える——右辺のセル名が数字で終わっていれば、その数字も同じオフセットだけインクリメントする：

```ruby
# 右辺のセル名 (末尾の数字をカウントアップ)
nsp.get_name.to_s =~ /(.*[^0-9])([0-9]+)\z/
if $2 then
  rhs_tail_num = $2
  rhs_name_count = count + rhs_tail_num.to_i
  ...
  nsp = nsp.change_name_clone rhs_cname
end
```

つまり`Worker0.cCall = Resource0.eEntry;`という結合を持つセルを`count=3`で複製すると、`Worker1.cCall = Resource1.eEntry; Worker2.cCall = Resource2.eEntry;`が自動生成される——**セルと、それが参照する相手セルの両方の命名規則が「同じ連番」で揃っている前提の、ペアでの連番展開機構**。配列受け口への結合（`nsp.port[subscript]`）の場合は添字もオフセットぶんインクリメントする。

### 2.1 著者自身が明記する既知の未対応事項

ファイル冒頭のコメントに、この調査シリーズで見てきた「mikan」コメント（HRP2SVCPlugin/HRP2RPCPlugin）や[[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenCellPlugin]]の粒度制限コメントと同種の、著者自身による明記された制約がある：

```ruby
#== cell を count 個繰り返すセルプラグイン
# 不完全点：
#    指定子に対応していない
#       cell の指定子 (allocator, id)
#       結合の指定子 (through)
```

——複製されるセルには`allocator`・`id`といったセル指定子、複製される結合には`through`指定子が**引き継がれない**、と作者自身が把握して書き残している。実運用でこれらの指定子を使うセルにRepeatCellPluginを適用すると、複製後のセルではその指定が失われる。

### 2.2 前提条件エラー: セル名が数字で終わっていない場合

```ruby
@cell.get_name.to_s =~ /.*[^0-9]([0-9]+)\z/
if $1 then
  ...
else
  cdl_error( "#{self.class}: #{@cell.get_name}'s name ends without '0-9'")
  return
end
```

——命名規約（末尾が数字）を満たさないセルに付与すると、汎用の`cdl_error`（専用エラーコードなし）で即座に失敗する。宣言的な「N個生成する」構文ではなく、**命名パターンに依存した規約ベースの繰り返し機構**である点が、CDL言語仕様としてはやや特異。

## 3. RepeatJoinPlugin: CDLテキストを介さず、結合モデルを直接操作する方式

`RepeatJoinPlugin < CellPlugin`。名前は似ているが、RepeatCellPluginとは**実現方式が根本的に異なる**——`gen_cdl_file`を一切持たず、代わりに`initialize`（47〜112行）の中で**`Join`オブジェクトを直接生成しモデルに追加する**：

```ruby
rhs = Expression.create_cell_join_expression( rhs_nsp2, rhs_subscript, rhs_port_name )
j2 = Join.new( j.get_name, count, rhs )
cell.new_join j2
```

対象は「呼び口配列（array port）の添字が`0`である結合」のみ（`if j.get_subscript == 0`）——**配列呼び口の先頭要素として書かれた結合を「種」として、その添字と（結合先セル名の末尾数字があれば）その数字を同時にインクリメントしながら`count`個の結合を複製し、直接`cell.new_join`でセルの結合リストに追加する**。RepeatCellPluginが「CDLソースコードとしてテキスト生成し、それが（他のプラグインの`generate(...)`文と同じ経路で）再度取り込まれる」のに対し、RepeatJoinPluginは**CDLテキストの往復を経ず、意味解析後のモデルオブジェクトを直接組み立てる**——同じ「count回繰り返す」という目的に対し、この調査シリーズで両方の実現方式（テキスト生成＋再取り込み／直接モデル操作）が存在することを初めて1組の対で確認できた。

RepeatCellPluginにあった「不完全点」コメントブロックはRepeatJoinPluginには無いが、同じ「セル名末尾の数字に依存する」規約や、結合の指定子を引き継げるかどうかの検証はコード上に見当たらず、同種の制約を暗黙に抱えている可能性がある（未検証）。

## 4. `$Id`は両ファイルとも正しく自分自身を指す——この調査シリーズでは珍しいクリーンな例

[[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin]]・[[work/active/tecsgen-plugins/CppIfGenPlugin|CppIfGenPlugin]]・[[work/active/tecsgen-plugins/TECSInfoPlugin|TECSInfoCompoPlugin]]で繰り返し見つけてきた「`$Id`が自分以外のファイル名を指す」複製痕跡は、このファミリーには**存在しない**——`RepeatCellPlugin.rb`の`$Id`は`RepeatCellPlugin.rb`を、`RepeatJoinPlugin.rb`の`$Id`は`RepeatJoinPlugin.rb`を正しく指している。ただし両者ともリビジョン番号（2952）・日付（2018-05-07）・作者名が完全に一致しており、**同じコミットで同時に追加された**ことは分かる——単なる偶然の一致ではなく、"count オプションの解析"というコードが両ファイルで一字一句同一であることとも整合する、正常な「同時期に姉妹プラグインとして書かれた」形跡。すべての複製がずさんな`$Id`更新漏れを伴うわけではない、という良い対照例になった。

## 5. 制約・注意点

- CDL実例はリポジトリ内に見つからず、`[generate(RepeatCellPlugin, "count=N")]`/`[generate(RepeatJoinPlugin, "count=N")]`の具体的な記述例はソースからの逆算・未検証。
- RepeatCellPluginが生成したCDLテキストが実際にどの経路で再取り込みされるか（[[work/active/tecsgen-plugins/TECSInfoPlugin|TECSInfoPlugin]]の`Import.new`のような動的インポートか、それとも`gen_cdl_file`という別の汎用フックが自動的に処理するのか）はソースの追加調査が必要——本ノートでは`CellPlugin`のライフサイクルフックとしての存在のみ確認した。
- RepeatJoinPluginの「著者未記載の制約」（4節末尾）は推測にとどまる。
- これで[[work/active/tecsgen-plugins/PluginCoverageAudit|プラグインカバレッジ監査]]が挙げた4候補（CIfGenPlugin・CppIfGenPlugin・TECSInfoPlugin・RepeatCellPlugin/RepeatJoinPlugin）がすべて完了。残る既知の未確認事項はTLVTracePlugin（実体不明、対応不要と確認済み）のみ。

## Related

- [[work/active/tecsgen-plugins/PluginCoverageAudit|プラグインカバレッジ監査]] — 本ファミリー発見の経緯、4候補完了の到達点
- [[work/active/tecsgen-plugins/CIfGenPlugin|CIfGenPlugin]] — セル単位付与の粒度制限コメントの対比元
- [[work/active/tecsgen-plugins/TECSInfoPlugin|TECSInfoPlugin]] — CDLテキストの動的生成・再取り込みという実現方式の対比元
- [[tecsgen外部仕様]] — 6.3 標準付属プラグイン一覧
- [[North Star]] — プラグイン仕様書化の進捗管理

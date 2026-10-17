 Ruby版tecsgenでの namespace の使い方を教えて

  Ran 5 shell commands

namespace は CDL で名前の衝突を避けるための入れ物です。C++ の namespace とほぼ同じ使い方です。

書き方

tecs-cdl
namespace nMruby {
    signature sInitializeBridge {
        void initializeBridge( [in]const mrb_state *mrb );
    };
    celltype tFoo { entry sInitializeBridge eEntry; };
    cell tFoo Foo { };
};                       // 末尾の ; が必要

文法は bnf.y.rb:890 の namespace : NAMESPACE namespace_NAME '{' statement_list '}' ';' です。実例は tecs/mruby/mrubyInitializer.cdl:36 にあり、namespace nMruby{ ... } で sInitializeBridge などを囲んでいます。

中に書けるもの

statement(bnf.y.rb:730-745)に挙がるものは、すべて namespace の中に書けます。

- typedef / const / enum / struct
- signature / celltype / composite celltype / cell
- region
- import / import_C
- generate 文
- 入れ子の namespace

namespace の外に出す命名規約はありません。ただし TECS の標準ライブラリは、n 始まりの namespace、s 始まりの signature、t 始まりの celltype、e 始まりの受け口、c 始まりの呼び口という慣習で書かれています。

参照の仕方(NamespacePath)

┌────────────────┬─────────────────────────────────────────────────────┐
│     書き方     │                        意味                         │
├────────────────┼─────────────────────────────────────────────────────┤
│ sSig           │ 相対。現在の namespace から探し、無ければ親へたどる │
├────────────────┼─────────────────────────────────────────────────────┤
│ nMruby::sSig   │ 相対。第1要素を相対で探した後、:: で下へたどる      │
├────────────────┼─────────────────────────────────────────────────────┤
│ ::nMruby::sSig │ 絶対。ルート namespace から探す                     │
└────────────────┴─────────────────────────────────────────────────────┘

- 探索(namespace.rb):単名の探索は find_one(namespace.rb:309)です。現在の namespace → 親 → ルートの順に探し、最初に見つかったものを返します。複数要素のパスは、最初の要素を探した後、find(namespace.rb:304)で下へたどります。途中が namespace でなければ not found になります。
- 命名:ファイル出力時のグローバル名は namespacepath.rb:172 の get_global_name が作り、名前が nMruby_sInitializeBridge のような形になります。
- region との関係:Region も Namespace を継承しています。region の中のセルも、同じ解決規則で参照されます。
- タグ名の例外:struct のタグ名は namespace に対応せず、ルートにあるものとして扱われます(namespace.rb:332 のコメントと、bnf.y.rb:390 の mikan)。

プラグインとの関係

statement 形式の generate(Plugin, nMruby::sInitializeBridge, "opts"); の第2引数が namespace_identifier です。この引数は、signature・celltype・composite celltype・cell を名前空間パスで指します(generate.rb)。

確認の範囲は、文法規則、Namespace.find と find_one、new_namespace、NamespacePath のメソッド一覧です。tecsgen を実行しての挙動確認はしていません。

✻ Cooked for 37s · done 7:40 AM

※ recap: Goal: document and catalog tecsgen's plugin system (CDL generate catalog, plugin list, class hierarchy), all pushed. Current task was answering your question on how namespace works in Ruby tecsgen, which is done; the new class-hierarchy file is uncommitted, so commit it next if you want.

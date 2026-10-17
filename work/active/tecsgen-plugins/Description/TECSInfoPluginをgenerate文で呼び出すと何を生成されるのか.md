TECSInfoPluginをgenerate文で呼び出すと何が生成されるのか

  Ran 3 shell commands

generate(TECSInfoPlugin, nTECSInfo::tTECSInfo, ""); と書いても、生成されるものは指定子で付けた場合と同じです。apply_plugin が同じなので、書き方による差はありません。実行はしておらず、tecslib/plugin/TECSInfoPlugin.rb、tecslib/core/tecsinfo.rb、tecs/TECSInfo/TECSInfo.cdl を読んだ範囲での説明です。

生成されるもの

TECSInfoPlugin は CelltypePlugin で、対象は tTECSInfo セルタイプです。対象のセルタイプを適用すると、次の4種類が生成されます。

1. initialize での副作用:--unoptimize-entry を強制的に有効にします(cdl_info の TIF0001 を出します)。

2. セルが作られるたびに(new_cell)
- $gen/tmp_<リージョン名>_TECSInfoSub.cdl を書き出して Import します。内容は、セルのリージョン内に [in_through()] region rTECSInfo { cell nTECSInfo::tTECSInfoSub TECSInfoSub; }; というプロトタイプ宣言を置くものです。
- そのセルに cTECSInfo の結合が無ければ、cTECSInfo = rTECSInfo::TECSInfoSub.eTECSInfo; を自動追加します。ユーザーは tTECSInfo のセルを置くだけで済みます。

3. ファクトリコード(gen_factory)
- include_all_signature_header.h:全シグニチャの _tecsgen.h を include します。
- nTECSInfo_tVarDeclInfo_factory.h
- nTECSInfo_tCelltypeInfo_factory.h
- nTECSInfo_tCallInfo_factory.h
- nTECSInfo_tEntryInfo_factory.h
- nTECSInfo_tCellInfo_factory.h
- nTECSInfo_tRawEntryDescriptorInfo_factory.h

  これらには、属性・変数のオフセットや、セルタイプ・呼び口・受け口・セルの定義マクロが入ります。

4. 後ろの CDL コード(gen_post_code、優先度は SIGNATURE_PLUGIN_POST_CODE_PRIORITY + 1000)
- tecsgen.rb の後処理で、TECSInfo.print_info(tecsinfo.rb:43)が呼ばれます。出力内容は次のとおりです。
  - 名前空間ごとのシグニチャ・セルタイプ・名前空間の情報セル
  - 型情報セル
  - 全体の TECS 情報セル
- これらは、tTECSInfo セルのあるリージョンの中に生成される CDL です。実行時に、CDL のモデル全体をたどれるようにするためのものです。
- 先にエラーが出ている場合は、I9999 を出して生成しません。

generate 文で呼ぶときの注意

tTECSInfo には、標準ライブラリの tecs/TECSInfo/TECSInfo.cdl:299 で既に generate(TECSInfoPlugin, "") の指定子が付いています。同じセルタイプに generate 文でもう一度付けると、指定子とは別に @generate_list へ追加され、プラグインが2回適用されます。そうなると new_cell が2回呼ばれ、同じ名前の tmp_..._TECSInfoSub.cdl が重複して Import される可能性があります。この点は、実行して確かめていません。

通常は、TECSInfo.cdl を import して tTECSInfo のセルを1つ置く使い方で足ります。generate 文で呼ぶ必要はありません。

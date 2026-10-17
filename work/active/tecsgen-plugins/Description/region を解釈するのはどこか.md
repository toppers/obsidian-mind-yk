region を解釈するのは Region クラス(tecslib/core/componentobj/region.rb:48)で、Region < Namespace < Node です。Region は Plugin 系のクラスではなく、構文木のモデルクラスです。

解釈の流れ

1. 構文解析:bnf.y.rb:1403-1456 の文法規則が region 名 { ... }; を認識します。
   - region_NAME を読んだ時点で Region.new(名前) が呼ばれ、リージョンが生成されます。
   - 閉じ括弧では Region.end_of_parse が呼ばれます。
   - ネストした region や cell は、このリージョンの名前空間の中に登録されます。
2. 指定子の保持:[...] 内の指定子は、region_specifier 規則から Region のクラスメソッド(region.rb:201-247)に渡されます。いずれもクラス変数に溜められ、次に生成される Region が受け取ります。

| 指定子                                               | クラスメソッド                                                       |
|------------------------------------------------------|----------------------------------------------------------------------|
| in_through / out_through / to_through / from_through | new_in_through / new_out_through / new_to_through / new_from_through |
| node / linkunit                                      | set_type                                                             |
| domain(...)                                          | set_domain                                                           |
| class(...)                                           | set_class                                                            |
   domain と class を同じリージョンに指定すると、どちらを先に書いても S9999 エラーになります。
3. プラグインの生成:Region.end_of_parse(region.rb:195)が create_domain_plugin と create_class_plugin を呼びます。ここで DomainType と ClassType(いずれも Node を継承)がプラグインクラスをロードします。
   - domain(HRP2, "trusted") なら HRP2Plugin を DomainPlugin としてロードします。
   - class(FMP, ...) なら FMPPlugin を ClassPlugin としてロードします。
   - through 系の指定子が指すプラグインは、結合の解析時に join.rb:744 が ThroughPlugin としてロードします。
4. 親リージョンへの伝播:set_domain_type / set_class_type(region.rb:310、328)が、子のドメイン・クラスを親へ伝えます。親に指定がなければ OutOfDomain や OutOfClass 相当を設定します。node リージョンが複数のドメインにまたがるとエラーになります。

確認の範囲:bnf.y.rb、region.rb の該当部分、domaintype.rb と classtype.rb のクラス定義だけを読みました。Region#initialize の中身(region.rb:84)や、ルートリージョン周りは読んでいません。

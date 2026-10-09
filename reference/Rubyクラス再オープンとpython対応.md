---
date: 2026-09-26
description: "Rubyのクラス再オープン（複数ファイルにまたがるclass定義の自動統合）とPythonの挙動差（class定義は常に新規オブジェクト）を整理。Python側の代替手段（Mixin・モンキーパッチ）も併記"
tags:
  - reference
---

# Rubyクラス再オープンとpython対応

## Context
[[tecsgen]]（Ruby実装）のようなRubyコードベースをPython移植する際、クラス定義が複数ファイルにまたがっている場合の挙動差を把握しておく必要がある。[[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]]検討時に参照する。

## Rubyの挙動: 「クラスの再オープン（reopening）」

Rubyでは`class Foo`は**新しいクラスを作る宣言ではなく、既存の同名定数を開いてメソッドを追記する操作**。同じ名前で複数回`class Foo`と書くと、全て同一のクラスオブジェクトに追記されていく。

```ruby
# file_a.rb
class Foo
  def method_a
    "a"
  end
end
```

```ruby
# file_b.rb
class Foo
  def method_b
    "b"
  end
end
```

```ruby
require_relative 'file_a'
require_relative 'file_b'

Foo.new.method_a  # "a"
Foo.new.method_b  # "b" ← 別ファイルなのに同じクラスに統合される
```

**特徴**:
- `require`/`require_relative`の読み込み順に依存——ただしメソッド追加自体は順不同でも成立する（`superclass`指定や`include`は最初の定義時にしか効かない点に注意）
- **同名メソッドが複数ファイルで定義されていた場合、後から読み込まれた方が黙って上書きする**（`-w`オプションで警告は出るが、デフォルトではエラーにならない）
- この機構により「1つの巨大クラスを複数ファイルに分割する」設計（Railsの`ActiveRecord`の`concerns`パターン等）や、「既存クラス/gemへのモンキーパッチ」がRubyでは言語機能として自然にできる

## Pythonの挙動: クラス定義は常に「新規作成」

Pythonの`class Foo:`は**その都度、新しいクラスオブジェクトを作り、現在のモジュール名前空間の`Foo`という名前に束縛する**操作。再オープンという概念自体が存在しない。

```python
# file_a.py
class Foo:
    def method_a(self):
        return "a"
```

```python
# file_b.py
class Foo:
    def method_b(self):
        return "b"
```

```python
from file_a import Foo as FooA
from file_b import Foo as FooB

FooA().method_a()  # "a"
FooB().method_b()  # AttributeError — FooAとFooBは完全に別のクラスオブジェクト
```

`file_a.Foo`と`file_b.Foo`は**同名なだけの無関係な2つのクラス**。Rubyのように自動的に統合されることはない。

## Pythonで同等のことをしたい場合の代替手段

| Rubyの用途 | Python対応 |
|---|---|
| 巨大クラスの機能を複数ファイルに分割 | **Mixin＋多重継承**（[[reference/Ruby Mixinとpython多重継承対応|関連ノート]]）。各ファイルでmixinクラスを定義し、本体クラスで`class Foo(MixinA, MixinB): ...`と合成する |
| 既存クラスへのモンキーパッチ | 明示的に`setattr`する（可能だが非推奨・実務では稀）: `import file_a; file_a.Foo.method_b = lambda self: "b"` |
| gemの挙動を後から拡張 | Pythonでは`__init_subclass__`やデコレータで「拡張ポイント」を明示的に設計するのが一般的（暗黙の再オープンには頼らない） |

## tecsgen移植への含意（2026-09-26調査結果: 広範に使用されている）

Ruby版tecsgen（`E:\Crepo\toppers-tecs-svn\toppers\tecsgen\branches\ykominami_r3033\tecsgen`）を`RubyVM::AbstractSyntaxTree`ベースで機械的に全数調査した結果、**再オープンパターンが中核クラスで広範に使われていることを確認**。実測データは[[reference/tecsgen_ruby_class_reopen.csv|tecsgen_ruby_class_reopen.csv]]。

**手法**: 全157個の`.rb`ファイルをASTでパースし、`class`/`module`宣言ノードを`CONST`/`COLON2`から完全修飾名で抽出、同名が複数ファイルにまたがるものを集計（構文解析エラー0件）。

**代表的な結果**:
- **`Namespace`（tecsgenの中核オブジェクト）— 7ファイルにまたがって再オープン**: `componentobj/namespace.rb`（本体定義、`< NSBDNode`）に加え、`generate.rb`（`generate`メソッド群・クラス変数`@@domain_gen_factory_list`等）、`optimize.rb`（`set_cell_id_and_domain`等）、`gen_xml.rb`（XML生成メソッド）、`tecsinfo.rb`、`unjoin_plugin.rb`、`tecsflow.rb`にそれぞれ機能別にメソッドが追記されている。目視確認済み——単なる同名クラスの偶然の一致ではなく、実際に同一`Namespace`クラスへの機能追加
- 同様のパターンが`Celltype`（6ファイル）、`Cell`（5ファイル）、`Signature`（5ファイル）、`TECSMsg`（5ファイル、メッセージ言語ごとに再オープン）、`Region`（4ファイル）、`TECSGEN`（4ファイル）等、コアの`componentobj`系クラス全般に及ぶ
- **設計の型**: 各クラスの「本体定義」は`tecslib/core/componentobj/<name>.rb`に集約されており（`< NSBDNode`等の継承・インスタンス変数群）、機能別の処理（意味解析`optimize.rb`／コード生成`generate.rb`・`gen_xml.rb`／診断情報`tecsinfo.rb`／unjoin処理`unjoin_plugin.rb`）はそれぞれ専用ファイルで**同じクラスに再オープンしてメソッドを追加**する構成。つまりRubyの「関心事ごとにファイルを分けつつ同一クラスに束ねる」設計が意図的に採用されている
- `TECSMsg`は用途が異なり、メッセージの言語・出力先（console/file × en_US/ja_JP）ごとに定数群を追加する再オープン
- ネストしたクラス（`TECSCDE::CellPluginDialog`、`TECSGEN::Cell_location`等）でも同様の再オープンパターンが見られる

**Python移植への影響**: これだけ広範に使われているため、単純な「1クラス=1ファイル」への機械的な書き換えでは移植できない。[[reference/Ruby Mixinとpython多重継承対応|Mixin方式]]（各関心事を`XxxOptimizeMixin`/`XxxGenerateMixin`等の別クラスにし、本体クラスで多重継承合成）への設計変更が必要。**Mixin化の粒度は[[work/active/tecsgen-python3/tecsgen-python3 Mixin粒度決定|Decision Record（2026-09-26）]]で決定済み**——「クラス」ではなく「関心事（Rubyの元ファイル）」を軸にMixinをまとめ、Ruby版のファイル構成をPythonモジュールとして1対1で踏襲する方針。

## Related
- [[tecsgen]] — Ruby実装版
- [[reference/tecsgen_ruby_class_reopen.csv|tecsgen_ruby_class_reopen.csv]] — 実測データ（24クラス/モジュールが2ファイル以上にまたがって再オープンされている）
- [[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]] — Python3移植の親ノート
- [[reference/Ruby Mixinとpython多重継承対応|Ruby Mixinとpython多重継承対応]] — 同シリーズ（mixin/多重継承編、本ノートの代替手段の詳細）
- [[reference/Rubyネストクラスとpython対応|Rubyネストクラスとpython対応]] — 同シリーズ（ネストクラス編）
- [[Patterns - 検証と調査]] — 同じくASTベースの機械的調査手法（トップレベルメソッド調査）を踏襲
- [[reference/Ruby1ファイル複数クラスとpython対応|Ruby1ファイル複数クラスとpython対応]] — 本ノードの裏返しの現象（ファイルが名前空間かどうかの違い）

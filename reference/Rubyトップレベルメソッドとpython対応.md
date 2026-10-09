---
date: 2026-09-26
description: "Rubyのトップレベルメソッド（Objectのprivateインスタンスメソッドとして定義される仕組み）の挙動と、Pythonでの対応（モジュールレベル関数、builtinsへの注入は非推奨）を整理したリファレンス"
tags:
  - reference
---

# Rubyトップレベルメソッドとpython対応

## Context
[[tecsgen]]（Ruby実装）のトップレベルメソッド全数調査（[[reference/tecsgen_ruby_toplevel_methods.csv|実測CSV]]、[[Patterns - 検証と調査 Archive#Ruby構造解析は正規表現の行走査でなくAST（`RubyVM::AbstractSyntaxTree`）を使う（2026-09-24）|AST調査の経緯]]）に関連して、Rubyのトップレベルメソッドの仕組みと、[[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]]でのPython対応を整理する。

## Rubyのトップレベルメソッドの仕組み

Rubyのトップレベルで定義したメソッドは、実際には**Objectクラスのprivateインスタンスメソッド**として定義される。

### 1. どこからでも直接呼び出せる

```ruby
def greet
  "hello"
end

greet          # => "hello"（トップレベルから）

class Foo
  def bar
    greet      # => "hello"（クラス内からも呼べる）
  end
end
```

すべてのオブジェクトが`Object`を継承しているため、レシーバなしで呼び出せる場所ならどこでも使える。

### 2. privateなのでレシーバ付き呼び出しはできない

```ruby
"str".greet       # NoMethodError（private method）
obj.send(:greet)  # send経由なら呼べる
```

### 3. `Object#method`などで参照は可能

```ruby
method(:greet).call
```

### 4. requireした別ファイルからも呼べる

トップレベルメソッドは`Object`に生えるグローバルな性質を持つため、`require`しただけで他ファイルからも同様に呼び出せる（名前空間の衝突リスクがある点は注意）。

## Pythonでの対応

Pythonにはトップレベル関数がそのまま存在し、Rubyの「暗黙的に`Object`のprivateメソッドになる」という特殊な仕組みは不要。ただし挙動の違いに注意が必要。

### 1. モジュールレベル関数（最も素直な対応）

```python
# utils.py
def greet():
    return "hello"
```

```python
import utils
utils.greet()          # 通常はモジュール修飾が必要

from utils import greet
greet()                # これでRubyのグローバル感覚に近い
```

**Rubyとの違い**: Rubyのトップレベルメソッドは`require`するだけで全ファイルから無条件に呼べるが、Pythonは`import`または`from ... import`で明示的に取り込む必要がある。暗黙のグローバル汚染がない代わりに、呼び出し側で毎回importが要る。

### 2. どのオブジェクトからでも呼べるようにしたい場合

Rubyの「レシーバなしでどこでも呼べる」を再現するには、`builtins`モジュールに注入する方法がある（**非推奨だが可能**）。

```python
import builtins
builtins.greet = lambda: "hello"

# 別ファイルでimportなしで使える
greet()
```

ただしこれはPythonのコミュニティでは強く避けられるパターン（暗黙的なグローバル汚染、IDE補完が効かない、mypy等の型チェッカーが追えない）。

### 3. tecsgen-python3移植の文脈での結論

実務的にはモジュール関数として素直に定義し、必要な場所でimportするのがPythonic。Ruby版のトップレベルメソッドが「グローバルユーティリティ関数」として使われている箇所は、Pythonでは`utils.py`のような共通モジュールに集約し、`from tecsgen.utils import xxx`の形にするのが自然な対応になる。

## tecsgen（Ruby版）の実測

[[Patterns - 検証と調査 Archive#Ruby構造解析は正規表現の行走査でなくAST（`RubyVM::AbstractSyntaxTree`）を使う（2026-09-24）|AST（`RubyVM::AbstractSyntaxTree`）ベースの調査]]により、Ruby版tecsgenのトップレベルメソッドは**23種類・定義25箇所・呼び出し623件**（合計648レコード）と確定。結果は[[reference/tecsgen_ruby_toplevel_methods.csv|tecsgen_ruby_toplevel_methods.csv]]に格納（`method`/`kind`/`file`/`line`/`code`列、`kind=definition|call`）。正規表現ベースの初期試作では`bnf.tab.rb`内の`module_eval`ヒアドキュメント文字列を誤検出し374件と過大に出ていたが、ASTベースでは文字列リテラル扱いとなり正しく除外された（詳細は上記Patternsノート参照）。

Python移植時はこの23メソッドをモジュール関数として`tecsgen-python3`側の共通モジュールへ集約する候補リストとして使える（TBC・仕分け未着手）。

## Related
- [[tecsgen]] — Ruby実装版
- [[reference/tecsgen_ruby_toplevel_methods.csv|tecsgen_ruby_toplevel_methods.csv]] — 実測データ（定義25箇所・呼び出し623件）
- [[Patterns - 検証と調査]] — AST調査の経緯（正規表現の誤検出→AST修正の教訓）
- [[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]] — Python3移植の親ノート
- [[reference/Ruby動的ロードとPython対応|Ruby動的ロードとPython対応]] — 同シリーズ（require/load/eval編）

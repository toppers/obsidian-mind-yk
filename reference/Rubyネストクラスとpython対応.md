---
date: 2026-09-26
description: "Rubyのネストしたクラス定義（Outer::Inner、レキシカル定数探索）をPythonでどう実現するか整理。Python側は名前空間化は同様だが、外側クラスの定数への修飾なしアクセスができない点が最大の違い"
tags:
  - reference
---

# Rubyネストクラスとpython対応

## Context
[[tecsgen]]（Ruby実装）や[[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]]で`Namespace`のようなクラスがネスト構造を持つ場合の設計判断材料として、Rubyのネストしたクラス定義とPythonでの対応を整理する。

## 1. 単純な名前空間化（最も一般的な用途）

Rubyでネストの主目的は「名前空間の整理」であることが多く、これはPythonでもそのまま素直に書ける。

```ruby
class Outer
  class Inner
    def greet
      "hello"
    end
  end
end

Outer::Inner.new.greet
```

```python
class Outer:
    class Inner:
        def greet(self):
            return "hello"

Outer.Inner().greet()
```

`::`が`.`になるだけで、構造としてはほぼ1対1対応。

## 2. 重要な違い: Rubyのレキシカル定数探索 vs Pythonの明示参照

Rubyでは、ネストしたクラス/モジュールの内部から**外側で定義された定数を修飾なしで直接参照**できる（レキシカルスコープによる`Module.nesting`ベースの解決）。

```ruby
class Outer
  CONST = "outer const"

  class Inner
    def show
      CONST  # 修飾なしで参照できる（レキシカルスコープ）
    end
  end
end
```

**Pythonにはこの機構がない。** Pythonのクラス本体（class body）が持つ名前空間は、そのクラス本体の直下でしか有効でなく、**ネストしたクラスやメソッドの本体には伝播しない**（関数のクロージャと同じ制限がクラスにも適用されるためで、Python公式の実行モデルにも明記されている）。

```python
class Outer:
    CONST = "outer const"

    class Inner:
        def show(self):
            return CONST  # NameError: name 'CONST' is not defined
```

`Inner.show`の中で`CONST`は見えない。**明示的に`Outer.CONST`と書く必要がある**（この時点では`Outer`はモジュールレベルの名前として存在しているので参照可能）。

```python
class Outer:
    CONST = "outer const"

    class Inner:
        def show(self):
            return Outer.CONST  # OK（実行時にOuterが解決される）
```

ただし`Inner`クラス本体そのものの直下（メソッドの外）でも、`Outer`自身の定義がまだ完了していない実行途中なので`Outer.CONST`とは書けず、この場合だけは同一クラス本体内の直前の代入を素の名前で参照できる（クラス本体トップレベルの逐次実行なので）:

```python
class Outer:
    CONST = "outer const"

    class Inner:
        pass

    print(CONST)  # OK — Outer自身のクラス本体トップレベルなので見える
```

## 3. Outer↔Inner間に自動的な関係はない（Ruby/Python共通）

どちらの言語でも、ネストは**単なる名前空間**であり、`Inner`のインスタンスが自動的に`Outer`のインスタンス状態にアクセスできるわけではない。関連付けたい場合は明示的に渡す設計が必要（言語差ではなく共通の設計上の注意点）。

```python
class Outer:
    def __init__(self, value):
        self.value = value

    class Inner:
        def __init__(self, outer):
            self.outer = outer  # 明示的に外側インスタンスを保持

        def show(self):
            return self.outer.value

o = Outer(42)
inner = Outer.Inner(o)
inner.show()  # 42
```

## まとめ

| Ruby | Python |
|---|---|
| `Outer::Inner`（名前空間アクセス） | `Outer.Inner` |
| レキシカルスコープで外側の定数を修飾なしで参照可 | 不可。`Outer.CONST`と明示する必要あり（メソッド内・ネストしたクラス内どちらも） |
| インスタンス間の関係は自動付与されない | 同左（明示的に参照を渡す） |

## Related
- [[tecsgen]] — Ruby実装版
- [[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]] — Python3移植の親ノート
- [[reference/Ruby Mixinとpython多重継承対応|Ruby Mixinとpython多重継承対応]] — 同シリーズ（クラス機構の対応、mixin/多重継承編）
- [[reference/Pythonのグローバル変数の使い方|Pythonのグローバル変数の使い方]] — 同シリーズ（スコープ関連）

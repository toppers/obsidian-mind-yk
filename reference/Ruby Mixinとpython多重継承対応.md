---
date: 2026-09-26
description: "Rubyのmixin（module/include/extend）に対応するPythonの多重継承＋MRO（C3線形化）・協調的super()・Protocolを整理したリファレンス"
tags:
  - reference
---

# Ruby Mixinとpython多重継承対応

## Context
Rubyのmixin（`include`/`extend`でモジュールをクラスに取り込む仕組み）は、Pythonでは多重継承と**MRO（C3線形化）**で実現する。仕組みは異なるが目的（コードの再利用・機能の合成）は同じ。[[tecsgen]]はRubyで書かれており、[[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]]（Python3移植）検討時に参照する。

## 基本パターン

```python
class Flyable:
    def fly(self):
        print(f"{self.name} is flying")

class Swimmable:
    def swim(self):
        print(f"{self.name} is swimming")

class Duck(Flyable, Swimmable):
    def __init__(self, name):
        self.name = name

d = Duck("Donald")
d.fly()   # Donald is flying
d.swim()  # Donald is swimming
```

Rubyだと:

```ruby
module Flyable
  def fly
    puts "#{name} is flying"
  end
end

class Duck
  include Flyable
end
```

## RubyのMRO（メソッド探索順）とPythonの違い

Rubyは`include`したモジュールを継承チェーンに挿入する（`ancestors`で確認可）。Pythonは多重継承そのものがmixinの機構で、`__mro__`（C3線形化）で解決順序が決まる。

```python
print(Duck.__mro__)
# (<class 'Duck'>, <class 'Flyable'>, <class 'Swimmable'>, <class 'object'>)
```

継承順（左が優先）でメソッド解決される点は、Rubyの`include`順（後から`include`したほうが優先）と似た直感で扱える。

## Mixin設計の実践ルール

Pythonでmixinを書くときの慣習:

- 単独では使わないクラスとして設計する（ABCにはしなくてよい。Rubyの`module`と同じ感覚）
- 状態（インスタンス変数）を極力持たせない — 持たせる場合は`__init__`で明示的に`super().__init__()`を呼ぶ協調的設計にする
- 命名規則でMixinサフィックスを付ける（`SerializableMixin`など）— Pythonには`module`のような別概念がないため、命名で意図を明示するのが実質的な標準
- MRO順は「Mixinを先、基底クラスを後」に書く

```python
class SerializableMixin:
    def to_dict(self):
        return self.__dict__

class LoggableMixin:
    def log(self, msg):
        print(f"[{self.__class__.__name__}] {msg}")

class User(SerializableMixin, LoggableMixin):
    def __init__(self, name):
        self.name = name

u = User("Alice")
u.log("created")
print(u.to_dict())
```

## super()で協調的に呼ぶパターン（Rubyのsuperと対応）

Rubyの`super`はモジュールを含む継承チェーン全体を辿る。Pythonの`super()`も同様にMRO全体を辿るので、mixin間で`__init__`をチェーンさせたいときは次のように書く:

```python
class Mixin1:
    def __init__(self, **kwargs):
        print("Mixin1 init")
        super().__init__(**kwargs)

class Mixin2:
    def __init__(self, **kwargs):
        print("Mixin2 init")
        super().__init__(**kwargs)

class Base:
    def __init__(self, **kwargs):
        print("Base init")

class Combined(Mixin1, Mixin2, Base):
    pass

Combined()
# Mixin1 init
# Mixin2 init
# Base init
```

これはRubyの`include`チェーンで各モジュールが`super`を呼んで連鎖する挙動とほぼ同じ発想。ポイントは**すべてのmixinが`**kwargs`を受け取って`super().__init__(**kwargs)`を呼ぶ協調的コンストラクタパターンを守ること**。守らないとチェーンが途中で切れる。

## Rubyのextend（特異メソッド化）に相当するもの

Rubyの`extend`はインスタンス単位でモジュールのメソッドを生やせるが、Pythonでは動的にインスタンスへメソッドを生やすのは非推奨気味。どうしても必要なら:

```python
import types

class ExtraBehavior:
    def greet(self):
        print("hello!")

obj = User("Bob")
obj.greet = types.MethodType(ExtraBehavior.greet, obj)
obj.greet()
```

ただしこれは実務ではほぼ使わず、代わりにデコレータや**Protocol（構造的部分型）**で同等の柔軟性を出すのがPythonic。

## typingでの「mixinのインターフェース契約」明示（型安全にしたい場合）

```python
from typing import Protocol

class HasName(Protocol):
    name: str

class Flyable:
    def fly(self: HasName) -> None:
        print(f"{self.name} is flying")
```

mypyでmixinが前提とする属性を型チェックできる。Rubyにはない恩恵。

## まとめ

| Ruby | Python |
|------|--------|
| `module` + `include` | 多重継承 + 協調的`super()` |
| `extend`（特異メソッド化） | 基本的にやらない。Protocolやデコレータで代替 |

実務では`abc.ABC`や`dataclass`と組み合わせるケースが多い。

## Related
- [[tecsgen]] — Ruby実装版
- [[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]] — Python3移植の親ノート
- [[reference/Ruby動的ロードとPython対応|Ruby動的ロードとPython対応]] — 同じくtecsgen-python3移植検討で作成したRuby→Python対応リファレンス（require/load/eval編）
- [[reference/Rubyネストクラスとpython対応|Rubyネストクラスとpython対応]] — 同シリーズ（ネストクラス/レキシカルスコープ編）
- [[reference/Rubyクラス再オープンとpython対応|Rubyクラス再オープンとpython対応]] — 同シリーズ（複数ファイルにまたがるクラス定義編、本ノートのMixin手法が代替策）

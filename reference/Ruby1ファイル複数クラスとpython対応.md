---
date: 2026-09-26
description: "Rubyで1ファイルに複数クラスを定義した場合の挙動（ファイルは名前空間でない）と、Pythonでの違い（ファイル=モジュール=名前空間）を整理。クラス再オープンが起きる/起きない理由の裏返しの説明"
tags:
  - reference
---

# Ruby1ファイル複数クラスとpython対応

## Context
[[work/active/tecsgen-python3/tecsgen-python3 Mixin粒度決定|tecsgen-python3のMixin粒度決定]]では「関心事ファイル1つに複数クラス向けMixinを並べる」構成を採用した。その前提となる、Rubyで1ファイルに複数クラスを定義した場合の挙動とPythonとの違いを整理する。

## Rubyで1ファイルに複数クラスを定義した場合

Rubyでは「ファイル」はロード単位であって**名前空間ではない**。1ファイルに何個クラスを書いても、各クラスは（明示的にモジュールでラップしない限り）**そのままトップレベルの`Object`直下の定数**として登録される。

```ruby
# shapes.rb
class Circle
  def initialize(r); @r = r; end
end

class Square
  def initialize(s); @s = s; end
end
```

```ruby
require_relative 'shapes'
Circle.new(1)
Square.new(2)  # requireするだけで両方とも無条件に使える
```

**ポイント**: ファイルは単なる「実行される文の並び」に過ぎず、`require`はそのファイルの中身を評価するだけ。ファイル境界とクラスの所属（どの名前空間に属するか）は**無関係**——これが[[reference/Rubyクラス再オープンとpython対応|クラス再オープン]]が起きる根本原因でもある（同名クラスをどのファイルで書いても同じ定数を指すため、意図せず衝突/合流しうる）。

## Pythonでの違い

Pythonでは**ファイル（モジュール）自体が名前空間**。1ファイルに複数クラスを書くのは普通だが、それらは**そのファイル（モジュール）のスコープに属する属性**として登録される。

```python
# shapes.py
class Circle:
    def __init__(self, r):
        self.r = r

class Square:
    def __init__(self, s):
        self.s = s
```

```python
import shapes
shapes.Circle(1)
shapes.Square(2)

# または
from shapes import Circle, Square
Circle(1)
Square(2)
```

**Rubyとの違い**: `import`しただけでは`Circle`/`Square`という名前は現在のスコープに現れない。`shapes.Circle`と修飾するか、`from shapes import Circle`で明示的に取り込む必要がある。ファイルが名前空間そのものなので、**別ファイルで同名クラスを定義しても衝突しない**（`shapes.Circle`と`other.Circle`は無関係な別クラス）——これは[[reference/Rubyクラス再オープンとpython対応|クラス再オープン]]の議論の裏返しで、Pythonでは「複数ファイルにまたがる再オープン」自体が起こり得ない理由そのもの。

## 同一ファイル内でのクラス間参照

どちらの言語でも、**メソッド本体の中**からなら定義順を気にせず他クラスを参照できる（呼び出し時点で存在していればよい）。ただし**クラス本体の直下（トップレベル評価される部分）**で他クラスを継承・参照する場合は、両言語とも**定義順が重要**（言語差ではなく共通の制約）。

```ruby
# Ruby: Bを先に定義する必要がある
class B; end
class A < B; end
```

```python
# Python: 同じくBを先に定義する必要がある
class B: pass
class A(B): pass
```

## まとめ

| 観点 | Ruby | Python |
|---|---|---|
| ファイル＝名前空間か | いいえ（単なるロード単位） | はい（モジュール＝名前空間） |
| `require`/`import`だけで無修飾使用可か | 可（`require`だけで全部使える） | 不可（`from x import Y`が必要） |
| 別ファイルの同名クラスが衝突するか | する（同じ定数を指すため再オープン） | しない（別モジュールの別クラス） |
| クラス継承の定義順制約 | あり | あり（共通） |

## Related
- [[tecsgen]] — Ruby実装版
- [[reference/Rubyクラス再オープンとpython対応|Rubyクラス再オープンとpython対応]] — 本ノートの裏返しの現象（同名クラスの衝突/合流）
- [[work/active/tecsgen-python3/tecsgen-python3 Mixin粒度決定|tecsgen-python3 Mixin粒度決定]] — 「1関心事ファイルに複数クラス向けMixin」構成の前提知識
- [[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]] — Python3移植の親ノート

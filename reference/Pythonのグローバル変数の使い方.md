---
date: 2026-09-26
description: "Pythonのグローバル変数（globalキーワード・スコープ規則・アンチパターンと代替策）を整理したリファレンス。tecsgen（Ruby、$グローバル変数多用）のPython移植検討時に参照"
tags:
  - reference
---

# Pythonのグローバル変数の使い方

## Context
[[tecsgen]]（Ruby実装）はグローバル変数（`$`プレフィックス）を多用しており、実測調査結果が[[reference/tecsgen_ruby_global_variables.csv|tecsgen_ruby_global_variables.csv]]にある。[[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]]（Python3移植）でこれらをどう扱うか検討する際、Python側のグローバル変数の仕様・慣習・代替策を先に整理しておく。

## 基本構文

```python
counter = 0  # モジュールレベルで定義 = グローバル変数

def increment():
    global counter  # この関数内でグローバルスコープの counter を使うと宣言
    counter += 1

def read_only():
    print(counter)  # 読むだけなら global 宣言は不要

increment()
increment()
print(counter)  # 2
```

**重要な仕様**: 関数内で変数に代入する行が1つでもあると、Pythonはその変数を「ローカル変数」とみなす。`global`宣言がないと`UnboundLocalError`になる。

```python
x = 10

def broken():
    print(x)      # ここでエラーになる
    x = 20        # この代入があるせいで x はローカル扱いされる

broken()  # UnboundLocalError: local variable 'x' referenced before assignment
```

## ミュータブルなオブジェクトなら global 不要

リストや辞書は「中身を書き換える」だけなら`global`は要らない（再代入ではないため）。

```python
items = []

def add_item(x):
    items.append(x)  # 中身の変更なので global 不要

def replace_items(new_list):
    global items
    items = new_list  # 再代入なので global 必須
```

## 実践的な使い方のパターン

### 1. モジュールレベルの設定・定数（推奨される用途）

```python
# config.py
DEBUG = False
MAX_RETRIES = 3
```

```python
import config
if config.DEBUG:
    ...
```

定数や設定値なら`global`キーワードを使わず、`モジュール名.変数名`でアクセスするのが素直。書き換えたい場合のみ:

```python
import config
config.DEBUG = True
```

### 2. キャッシュ・シングルトン的な状態管理

```python
_cache = {}

def get_data(key):
    global _cache
    if key not in _cache:
        _cache[key] = expensive_computation(key)
    return _cache[key]
```

先頭にアンダースコアを付けるのは「モジュール外から直接触らないでほしい」という慣習的な意図表示（強制力はない）。

### 3. globals() / locals() で動的にアクセス

```python
def set_global(name, value):
    globals()[name] = value

set_global("my_var", 42)
print(my_var)  # 42
```

動的コード生成やプラグイン機構以外ではほぼ使わない。

## 避けるべきアンチパターンと代替策

グローバル変数はテストしにくい・並行処理で壊れやすい・依存関係が見えなくなるという欠点がある。

| よくある誤用 | 代替策 |
|---|---|
| 関数間で状態を共有するためにグローバル変数を乱用 | クラスのインスタンス変数にまとめる |
| 設定値をあちこちの関数で`global`宣言して書き換え | `dataclass`や`NamedTuple`で設定オブジェクト化し、引数で渡す |
| キャッシュをグローバル辞書で自前実装 | `functools.lru_cache` / `functools.cache`を使う |

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def expensive_computation(key):
    ...
```

クラスでの置き換え例:

```python
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1

c = Counter()
c.increment()
```

`global`を使わずに済み、複数インスタンスを独立して持てるので、テストやマルチスレッド環境でも安全。

## 結論
- 読むだけなら`global`不要、書き換える（再代入する）なら必須
- ミュータブルオブジェクトの中身操作なら`global`不要
- 設定・定数レベルの用途は許容範囲、状態管理が絡むなら基本的にクラスか`functools.lru_cache`に寄せた方が保守性が上がる

## tecsgen移植への適用（TBC・未検討）
[[tecsgen_ruby_global_variables.csv|Ruby版のグローバル変数実測]]をこの分類（設定・定数／キャッシュ・シングルトン／状態共有）に当てはめて仕分け、状態共有系はクラスのインスタンス変数へ、設定・定数系はモジュール属性へ移す方針が考えられるが、実際の仕分けは未着手。

## Related
- [[tecsgen]] — Ruby実装版
- [[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]] — Python3移植の親ノート
- [[reference/Ruby動的ロードとPython対応|Ruby動的ロードとPython対応]] — 同シリーズ（require/load/eval編）
- [[reference/Ruby Mixinとpython多重継承対応|Ruby Mixinとpython多重継承対応]] — 同シリーズ（mixin/多重継承編）

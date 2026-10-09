---
date: 2026-09-26
description: "Rubyのrequire/require_relative/load/evalに対応するPythonの動的ロード手段（importlib.util, exec, pkgutil, メソッド内import）を用途別に整理したリファレンス"
tags:
  - reference
---

# Ruby動的ロードとPython対応

## Context
Rubyの `require` / `require_relative` / `load` / `eval` は意味が微妙に異なる。Pythonで同等の動作を実現する手段を用途別に整理する。[[tecsgen]]はRubyで書かれており、[[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]]（Python3移植）検討時、特に[[work/active/tecsgen-plugins-python3/tecsgen-plugins-python3|プラグイン機構の移植]]（Ruby版`plugin.rb`/`pluginModule.rb`による動的ロード→Python importベースへの置き換え）で参照する。

## 対応表

| Ruby | Python |
|------|--------|
| `require` / `require_relative` | `import`、またはパス指定時は `importlib.util.spec_from_file_location` + `sys.modules`登録 |
| `load` | `spec_from_file_location` + `exec_module`（`sys.modules`未登録＝毎回フル実行） |
| `eval(code)` | `exec(code_str, namespace)` |
| `Dir.glob("plugins/*.rb").each { require f }` | `pathlib.Path.glob` + 動的import、またはパッケージ構造なら `pkgutil.iter_modules` |

## 1. require_relative相当（1回だけ読み込み、キャッシュされる）

```python
# 同じパッケージ内なら通常のimportでOK
from . import mymodule

# パスを指定してファイルから直接読み込みたい場合
import importlib.util
import sys

def load_module_from_path(path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # importlib.reloadやpickle対応のため登録推奨
    spec.loader.exec_module(module)
    return module

mod = load_module_from_path("/path/to/foo.py", "foo")
mod.some_function()
```

`sys.modules`に登録しない場合は再度呼んでも毎回新規実行（`load`相当）になる。

## 2. load相当（毎回再実行、キャッシュしない）

```python
def reload_module_from_path(path, module_name="reloaded_mod"):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # sys.modulesに登録しない=毎回フル実行
    return module
```

既存の`import`済みモジュールを再実行したいだけなら:

```python
import importlib
importlib.reload(mod)  # Rubyのload相当（既存importモジュールの再実行）
```

## 3. eval相当（文字列やコードを動的実行）

```python
code_str = open("script.py").read()
namespace = {}
exec(code_str, namespace)
namespace["some_function"]()
```

`exec`は任意コードを実行するため、外部入力やユーザー生成コードには要注意（信頼できるファイルのみに使う）。

## 4. プラグイン的にディレクトリ内スクリプトを全部動的ロード

Rubyの`Dir.glob + require`パターン相当:

```python
import pkgutil
import importlib
from pathlib import Path

def load_plugins(plugin_dir: str):
    plugins = {}
    for py_file in Path(plugin_dir).glob("*.py"):
        if py_file.stem.startswith("_"):
            continue
        mod = load_module_from_path(str(py_file), py_file.stem)
        plugins[py_file.stem] = mod
    return plugins

plugins = load_plugins("./plugins")
for name, mod in plugins.items():
    if hasattr(mod, "register"):
        mod.register()
```

パッケージ配下（`__init__.py`あり）で構造化されている場合は`pkgutil.iter_modules`の方が素直:

```python
import pkgutil
import importlib
import myplugins  # __init__.py がある通常のパッケージ

for _, name, _ in pkgutil.iter_modules(myplugins.__path__):
    importlib.import_module(f"myplugins.{name}")
```

## 使い分けの指針
用途（1回だけ読みたいか、ホットリロードしたいか、プラグイン機構を作りたいか）によって選択する。

## 5. メソッド内での動的import（Rubyの`require`をメソッド実行中に呼ぶ相当）

Rubyの`require`をインスタンスメソッド実行中に呼べるのと同様、Pythonの`import`文もトップレベル限定ではなくどこでも書ける（関数内・メソッド内・`if`文の中・`try`節の中）。

```python
class DataProcessor:
    def process(self, use_advanced=False):
        if use_advanced:
            import numpy as np  # メソッド実行時に初めてロードされる
            return np.array([1, 2, 3]).sum()
        else:
            return sum([1, 2, 3])
```

`require`と同じく2回目以降は`sys.modules`にキャッシュされ再ロードされない（importの本体コストは初回のみ）。

### ユースケース（Rubyと共通）

| ユースケース | 説明 |
|---|---|
| 重い依存の遅延ロード | `pandas`や`torch`など起動コストの高いライブラリを、実際に使うメソッドが呼ばれるまで読み込まない |
| 循環importの回避 | モジュールA↔Bが互いを参照する場合、トップレベルimportだと循環エラーになるが、メソッド内なら実行時点で解決済みなので通る |
| オプショナル依存 | そのメソッドを使うユーザーだけが該当ライブラリをインストールしていればよい設計 |
| 条件付き機能切り替え | プラットフォームやフラグに応じて別実装をロード |

循環import回避の具体例（Rubyでも`require_relative`を遅延させて対応するパターンと同じ）:

```python
# models/user.py
class User:
    def get_posts(self):
        from models.post import Post  # トップレベルだと循環importでエラーになるケース
        return Post.find_by_user(self.id)
```

```python
# models/post.py
class Post:
    def get_author(self):
        from models.user import User
        return User.find(self.user_id)
```

`importlib.util.spec_from_file_location`パターン（本ノート1節）もそのままメソッド内に書ける（キャッシュ判定込み）:

```python
import importlib.util
import sys

class PluginRunner:
    def run_plugin(self, plugin_path: str):
        module_name = f"plugin_{hash(plugin_path)}"
        if module_name not in sys.modules:
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        return sys.modules[module_name].run()
```

### Rubyとの違いで注意すべき点：スコープ

メソッド内で`import foo`すると、`foo`はそのメソッドの**ローカル変数**として束縛される。Rubyの`require`は「モジュール定数をグローバルに定義する」動きだが、Pythonの`import`は「名前をそのスコープにバインドする」動きなので、他のメソッドから直接`foo`を参照できない（各メソッドで都度importが必要）。

クラス全体で使い回したいなら、`__init__`や外側のimportにするか、インスタンス属性として保持する設計が自然:

```python
class DataProcessor:
    def __init__(self, use_advanced=False):
        if use_advanced:
            import numpy as np
            self._np = np  # インスタンス属性として保持
        else:
            self._np = None

    def process(self):
        if self._np:
            return self._np.array([1, 2, 3]).sum()
        return sum([1, 2, 3])
```

Rubyの「実行フローの中で`require`を呼ぶ」という発想はPythonでもそのまま（むしろより自由度高く）書けるが、名前がローカルスコープに閉じる点だけ設計上意識する。

## Related
- [[Patterns - 検証と調査]] — Ruby構造解析はASTを使う（`RubyVM::AbstractSyntaxTree`）等、Ruby関連の検証パターン
- [[ghrepo]] — yklibpy基盤のPython CLIパターン
- [[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]] — tecsgen Python3移植の親ノート
- [[work/active/tecsgen-plugins-python3/tecsgen-plugins-python3|tecsgen-plugins-python3]] — プラグイン動的ロード機構の移植先（本ノートの直接の適用対象）
- [[reference/Ruby Mixinとpython多重継承対応|Ruby Mixinとpython多重継承対応]] — 同じくtecsgen-python3移植検討で作成したRuby→Python対応リファレンス（mixin/多重継承編）
- [[reference/Pythonのグローバル変数の使い方|Pythonのグローバル変数の使い方]] — 同シリーズ（グローバル変数編）
- [[reference/Rubyとpythonのカレントディレクトリ変更の影響|Rubyとpythonのカレントディレクトリ変更の影響]] — 同シリーズ（chdir編、相対パスでの動的ロードに関連）
- [[reference/Rubyトップレベルメソッドとpython対応|Rubyトップレベルメソッドとpython対応]] — 同シリーズ（トップレベルメソッド編）

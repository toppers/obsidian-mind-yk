---
date: 2026-09-26
description: "Ruby（Dir.chdir）とPython（os.chdir）でスクリプト実行中にカレントディレクトリを変更した場合の影響を比較。プロセス全体で共有される単一状態であること、相対パス解決・サブプロセス・動的ロードへの影響、ブロックスコープの有無を整理"
tags:
  - reference
---

# Rubyとpythonのカレントディレクトリ変更の影響

## Context
スクリプト実行中に`Dir.chdir`（Ruby）/`os.chdir`（Python）でカレントディレクトリを変更した場合の影響を整理。tecsgen/[[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]]のようなファイルI/O・相対パス解決を扱うCLIツールの設計判断材料。

## 共通する性質
どちらも**OSプロセス全体で共有される単一の状態**（`chdir(2)`システムコール）を操作するため、根本的な性質は同じ。プロセス内の全スレッド・全ライブラリに影響し、スレッドごとの独立性はない。

### 影響を受けるもの

| 影響を受けるもの | 理由 |
|---|---|
| 相対パスでのファイルオープン | `open("foo.txt")`のような相対パス解決は、呼び出し時点のカレントディレクトリを基準にする |
| サブプロセス起動時のcwd | `subprocess.Popen`/`Kernel#spawn`はデフォルトで親プロセスの現在のカレントディレクトリを継承する |
| 相対パスでの動的ロード | Rubyの`require_relative`は呼び出し元スクリプトのファイルパス基準（`chdir`の影響を受けない）だが、`require`に相対パスを渡した場合や`Dir.glob("./plugins/*")`は影響を受ける。Pythonの`importlib.util.spec_from_file_location`に相対パスを渡した場合も同様（[[reference/Ruby動的ロードとPython対応|関連: Ruby動的ロードとPython対応]]） |

### 影響を受けないもの（すでに絶対パス解決済み）

- 既にオープン済みのファイルディスクリプタ — OSはinode/ファイルハンドルを保持しており、パス文字列を再解決しない
- `__FILE__`（Ruby）や`__file__`（Python）— スクリプトロード時点で決まる文字列
- `File.expand_path(__dir__)`（Ruby）や`os.path.dirname(os.path.abspath(__file__))`（Python）で事前に絶対パス化した変数

## Ruby固有

```ruby
Dir.chdir("/tmp") do
  # ブロック内だけ一時的に変更、ブロック終了で自動的に元へ戻る
  File.read("foo.txt")  # /tmp/foo.txt を読む
end
# ここでは元のディレクトリに復帰済み
```

- ブロック付き`Dir.chdir`はスコープが明確で、例外が起きても`ensure`相当で復帰する（安全）
- ブロックなし`Dir.chdir(path)`はプロセスの状態を恒久的に変える（呼び出し元が明示的に戻す必要がある）
- **マルチスレッドで`Dir.chdir`にブロックを渡すと衝突しうる**（Ruby 2.x以降、カレントディレクトリはプロセス共有なので、複数スレッドが同時にブロック付き`chdir`をすると`RuntimeError: conflicting chdir during another chdir block`が起きうる）

## Python固有

```python
import os

os.chdir("/tmp")
# ブロックスコープの概念がない。戻すのは自己責任
with open("foo.txt") as f:  # /tmp/foo.txt を読む
    ...
```

- ブロック付きの自動復帰機構は標準にない。同等のことをしたい場合は`contextlib.chdir`（**Python 3.11+で追加**）を使う:

```python
import contextlib, os

with contextlib.chdir("/tmp"):
    ...  # ブロック内だけ変更、抜けると自動復帰
```

- `os.getcwd()`は呼び出し時点の値を都度取得する（キャッシュされない）
- `pathlib.Path.cwd()`も同様に毎回OSへ問い合わせる。一方で`Path(".")`のような相対`Path`オブジェクトは解決を遅延しており、`.resolve()`を呼んだ時点のカレントディレクトリを基準に絶対化される点に注意（生成時ではなく使用時）

## 実務上の注意（両言語共通）

- **ライブラリ内で`chdir`するのは避けるべきアンチパターン**——呼び出し元の状態を暗黙に破壊するグローバル副作用。ファイルI/O・`import_C`の相対パス解決を扱う設計では、`chdir`せずに**絶対パスを都度組み立てて渡す**設計の方が安全
- テスト・並行処理下では`chdir`はプロセスグローバルなので**テスト間の汚染源**になりやすい

## tecsgenでの関連事例
[[Patterns - 検証と調査]]に記録済みの「`.tecsgen-opts`ファイル中のCDLパスは相対パス想定だが、`.tecsgen-opts`自身のディレクトリを基点に解決する処理が欠けていた」不具合（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|第7C章]]#8/#10実装時に発覚）は、本ノートの「相対パス解決はカレントディレクトリではなく明示的な基点から絶対パス化すべき」という原則と同種の落とし穴。

## Related
- [[tecsgen]] — Ruby実装版
- [[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]] — Python3移植の親ノート
- [[reference/Ruby動的ロードとPython対応|Ruby動的ロードとPython対応]] — 同シリーズ（require/load/eval編、相対パスでの動的ロードに関連）
- [[Patterns - 検証と調査]] — `.tecsgen-opts`相対パス解決不備の実例

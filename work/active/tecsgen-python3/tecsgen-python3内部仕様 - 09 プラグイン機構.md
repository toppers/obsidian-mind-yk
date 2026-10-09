---
date: 2026-10-01
description: "tecsgen-python3 内部仕様9章（プラグイン機構）のうち、プラグインのロードと -L による利用者プラグインの探索。Ruby の require を Python の import に置き換えた部分と、Ruby 版との差異"
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
project: tecsgen-python3
quarter: Q4-2026
status: active
---

# tecsgen-python3 内部仕様 - 09 プラグイン機構（ロードと `-L` 探索）

Ruby 版 [[work/active/tecsgen/tecsgen内部仕様 - 09 プラグイン機構|9章]] の対応章。本書は **ロード部分**（`core/plugin_module.py`、`host.py`）だけを書く。`MultiPlugin` のディスパッチ・ポストコードの優先順位・プラグイン引数のパースは Ruby 版と同じ作りなので、Ruby 版の章を参照する。決定の経緯は [[tecsgen-python3 -L ユーザプラグイン探索設計]]。

## 9.2 プラグインのロード（Ruby 版との差異）

Ruby 版の `require_tecsgen_lib( "#{name}.rb", false )` + `Object.const_get( name )` を、`core/plugin_module.py` の `_import_plugin_class( name )` が置き換える。探索順は次のとおり。

1. **利用者プラグインのレジストリ**（`_user_plugin_classes`）に `name` があればそれを返す
2. **組み込み** `tecsgen.plugin.<name>` を import する
3. **`-L` のディレクトリ**（`ctx.library_path` の先頭から）。各ディレクトリで `<name>.py`、続いて `tecslib/plugin/<name>.py` を探し、最初に見つかったものを読む

見つからなければ `None`（呼び出し元の `load_plugin` が P2001）。Ruby 版との違い:

| 項目 | Ruby 版 | Python 版 |
|---|---|---|
| ファイル | `<name>.rb` | `<name>.py`（`.rb` は探さない） |
| 探す場所 | `$library_path + $LOAD_PATH` × `""`・`tecslib/plugin/` | 組み込み → `ctx.library_path` × `""`・`tecslib/plugin/`。`sys.path` は探さない |
| 環境変数 `RUBYLIB` | `-L` と同等 | 対応しない（代わりの環境変数も無い） |
| 組み込みと同名の利用者プラグイン | `-L` の指定順で最初に見つかったもの | 組み込みが先に見つかるので上書きできない |
| 基底クラス（`ThroughPlugin` など） | グローバル名として見える | 利用者プラグインが `from tecsgen.plugin.ThroughPlugin import ThroughPlugin` と明示的に import する |
| ロード時の副作用（`@@x = {}` など） | プロセスごとに1回 | 実行ごとに1回（ファイルを実行回ごとに読み直す） |

### 利用者プラグインの読み込み（`_import_user_plugin_class`）

- `importlib.util.spec_from_file_location` でファイルパスから読む。`sys.path` は変えない（標準ライブラリと同名のファイル、例えば `types.py` を隠さないため）。モジュール名はパスのハッシュ（`tecsgen_user_plugin_<hash>`）。別のケースに同名で内容の違うプラグインがある（`through/Plugin1` と `region/Plugin1`、`generate/RTMBridgePlugin` と `signaturePlugin/RTMBridgePlugin`）ので、名前だけでキャッシュしない
- 読んだクラスは `sys.modules` ではなく、実行回ごとのレジストリ `_user_plugin_classes` に入れる。`PluginModule.reset()` が空にする。ロードに失敗した名前は `None` を入れ、同じ実行の中では読み直さない。組み込みは従来どおり `sys.modules` から引く（`_lookup_loaded_plugin_class`）
- ロード中の例外（構文エラー・import の失敗・クラス本体の例外）は `print_exception` で表示して再送出する。`load_plugin` の `except` が **P2003** にする（Ruby の `require` の失敗と同じ経路）。ファイルはあるのに `<name>` クラスが無い場合も P2003（Ruby の `uninitialized constant`）。基底クラスが期待と違えば P2002
- 利用者プラグインは `-L` で指したディレクトリのコードをそのまま実行する。Ruby 版と同じ信頼モデル

### `Host.resolve_plugin_file( directory, fname )`

`-L` のディレクトリにあるファイルの実パスを返す（無ければ `None`）。Ruby の `File.exist?( File.expand_path( directory ) + '/' + fname )` に当たる。Python のコードは記録から再生できないので、既定の `Host` は実ファイルシステムを見る。差分テストの `RecordedHost` は、P3 オラクルの記録に `.py` の問い合わせが無く、`-L .` の `.` も仮想の作業ディレクトリ（`@WORK@/test/<ケース>`）なので、記録を引かずに **採取時の作業ディレクトリ → `tests/user_plugins/<ケースID>/`** と対応付けて答える。

## 差分テストでの扱い

テストケースに同梱された Ruby 製の利用者プラグイン（`test/<ケース>/*.rb`）の Python 版を `tests/user_plugins/<ケースID>/<クラス名>.py` に置く（`tests/golden/cases/` には置かない。正解データの採り直しで消えるのを避けるため）。同梱のうち、組み込みと同名のもの（`generate` の `ATK1TaskPlugin`）は組み込みが先に使われるので移植していない。`MyTracePlugin` は Ruby 版が `TracePlugin.rb` の複製なので、`TracePlugin` の子クラスにして `gen_ep_func_body` だけを上書きしている。

## パーサの reuse フラグ（Import の W1008）

`Generator.is_reuse?` は、現在のパーサの `@b_reuse` を返す。Ruby 版のパーサは `@b_reuse` を初期化せず、`set_reuse` されないと nil のままなので、`is_reuse?` も `false` ではなく nil を返す。`Import` は `b_reuse || Generator.is_reuse?` を保存し、同じファイルの2回目の import で前回の値と `!=` で比べて W1008 を出すので、`false` と nil の違いが警告の有無になる（`TECSInfoPlugin#new_cell` が同じ tmp ファイルを2回 import する）。Python 版も `CdlParser._b_reuse` を `None` で始め、`is_reuse()` が `bool | None` を返す。

## Related

- [[tecsgen-python3内部仕様]] — 目次
- [[tecsgen-python3 -L ユーザプラグイン探索設計]] — 決定
- [[tecsgen-python3 パッケージ構成決定]] — クラス名＝ファイル名
- [[tecsgen-python3移植計画 — P5 進捗ログ#P5q（2026-10-01）|P5q]] — 実装と検証
- [[tecsgen-plugins-python3]]

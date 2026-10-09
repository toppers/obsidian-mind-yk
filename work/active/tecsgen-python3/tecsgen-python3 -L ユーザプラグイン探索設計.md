---
date: 2026-10-01
description: "tecsgen-python3 の -L によるユーザプラグイン探索の設計案（accepted）：探索順はRuby版と同じ、利用者プラグインは<クラス名>.py、ファイルパスからロード、実行回ごとにレジストリで管理、テスト用は Host 経由でパスを対応付ける"
status: accepted
project: tecsgen-python3
quarter: Q4-2026
tags:
  - decision
  - tecs
  - tecsgen
---

# Decision: tecsgen-python3 -L ユーザプラグイン探索設計

## Context

[[tecsgen-python3移植計画]] P5 の持ち越し。`-L` は引数を保存するだけで、探索には使われていない（`cli.py` の `library_path` ハンドラが `ctx.library_path` に足すのみ。探索は `core/plugin_module.py` の `_import_plugin_class` が `tecsgen.plugin.<名前>` だけを見る）。`-L` を使う正解データのケースのうち、プラグイン使用で未一致の8件（CPPBridge・SWIGBridge・domainPlugin・ErrorCase/domainPlugin-err・generate・region・restrict・through）はこれ待ち（[[tecsgen-python3移植計画 — P5 進捗ログ — P5j–P5k]]）。方針の元は [[tecsgen-python3 P0基本方針決定]]（`-L` はプラグインの探索パスへ追加）と [[tecsgen-python3 パッケージ構成決定]]（クラス名＝ファイル名）。

Ruby 版の挙動（`tecsgen.rb` `require_tecsgen_lib`、2026-10-01 に直接確認）:

- `($library_path + $LOAD_PATH)` の各ディレクトリについて、`""` と `"tecslib/plugin/"` の2つの下位パスを順に試す。`File.expand_path(path) + '/' + lp + fname` が存在すれば `require` し、**最初に見つかったものだけ**で打ち切る
- `require` で例外が出たら `print_exception` して打ち切る。見つからなければ警告のみ（`b_fatal = false` なら黙る）。呼び出し元の `load_plugin` が `P2001`（ファイル無し）・`P2002`（基底クラス不一致）・`P2003`（その他のロード失敗）を出す（[[work/active/tecsgen/tecsgen内部仕様 - 09 プラグイン機構|Ruby版 内部仕様9章]]）
- `cli.py:74` は `ctx.library_path = [ctx.tecsgen_base_path]` で始まるので、組み込みプラグインが `-L` より先に見つかる。Ruby 版も `tecsgen.rb:295` で `$library_path = [ $tecsgen_base_path ]` と初期化し、`-L` は `:364` で `<<` により後ろへ追加する。先頭が同じで、組み込みが先に見つかる点も一致（2026-10-03 確認、TBC 解消）

テストに同梱された利用者プラグインは Ruby 製（`test/through/Plugin1.rb` など）で、Python 版では書き直しが要る。基底クラス（`ThroughPlugin` など）は Ruby ではグローバル名として見える。`through/Plugin1.rb` はクラス本体で `@@generated_celltype = {}` を実行し、ロード時に同系統で共有する辞書を空にする（P5j で判明した副作用）。

## Decision

2026-10-01 ユーザー承認: RUBYLIB 非対応（代わりの環境変数も作らない）、組み込みと同名のプラグインを -L で上書きできない仕様、同梱プラグインの Python 版は tests/user_plugins/ に置く。

### 1. 探索順 — Ruby 版と同じにする

`ctx.library_path` を先頭から、各ディレクトリで `<dir>/<名前>.py`、続いて `<dir>/tecslib/plugin/<名前>.py` を試す。最初に見つかったものを使う。組み込み（`tecsgen.plugin.<名前>`）は、現在の `ctx.library_path[0]`（`tecsgen_base_path`）の位置に当たるものとして**最初に**試す。したがって利用者は組み込みと同名のプラグインを上書きできない（仕様として確定。Ruby 版の `$library_path` 先頭との一致は 2026-10-03 に確認済み）。`$LOAD_PATH` に当たるもの（`sys.path`）は探さない。

### 2. 利用者プラグインのファイル — `<クラス名>.py`

- Ruby の `.rb` は実行できないので探さない。`.rb` だけがあって `.py` が無い場合も `P2001`（メッセージは `$1.rb` のまま。Ruby 版と一致させる）
- 基底クラスは**明示的に import する**（`from tecsgen.plugin.ThroughPlugin import ThroughPlugin`）。グローバル名の注入はしない。`tecsgen.plugin.*` を利用者向けの公開 API とし、外部仕様に書く
- 組み込みの N999 除外（[[tecsgen-python3 パッケージ構成決定]]）と同様、利用者プラグインのファイル名も Ruby と同名のクラス名を許す

### 3. ロード方式 — ファイルパスから直接読む

- `importlib.util.spec_from_file_location` でファイルから読み、`sys.path` は触らない（標準ライブラリと同名のファイル、例えば `types.py` を隠さないため）
- モジュール名はパスから決める（`tecsgen_user_plugin_<パスのハッシュ>`）。`generate/RTMBridgePlugin` と `signaturePlugin/RTMBridgePlugin`、`through/Plugin1` と `region/Plugin1` のように**同名で内容の違うプラグインが別ケースにある**ため、名前だけでキャッシュしてはいけない
- ロード済みクラスは `sys.modules` ではなく **`PluginModule` が持つ実行回ごとのレジストリ**（`reset()` で空にする）に置く。現在の `_lookup_loaded_plugin_class` は `sys.modules` を引くので、組み込みも含めてレジストリ経由に直す。実行ごとに必ず再実行する（同一プロセスで複数回走るテストでも、Ruby の「実行ごとに1回 require」と一致する。`@@generated_celltype = {}` 相当の副作用も再現できる）

### 4. エラー — 既存の P2001・P2002・P2003 をそのまま使う

- ファイルが無い → `P2001`
- ロード中の例外（構文エラー・import 失敗・クラス本体の例外）→ `print_exception` してから `P2003`（Ruby の `require` 失敗と同じ経路）
- ファイルはあるがクラス名が無い → `P2003`（`uninitialized constant`）
- 基底クラスが期待と違う → `P2002`

### 5. テストでの対応付け — Host を通す

記録（P3 オラクル）には Ruby が出した `File.exist?` の問い合わせしか無く、`.py` を探す問い合わせは `HostMiss` になる。また `-L .` の `.` は仮想の作業ディレクトリ（`@WORK@/test/through`）で、実在のパスではない。そこで:

- `Host` に `resolve_plugin_file(dir, fname) -> Path | None` を足す。既定は実ファイルシステムを見る。`RecordedHost` は「仮想ディレクトリ → 実ディレクトリ」の対応表（ケースごと）で答え、記録は引かない
- 同梱プラグインの Python 版は `tests/user_plugins/<ケースID>/<名前>.py` に置く。`tests/golden/cases/` には置かない（正解データの採り直しで消えうるのと、「Ruby 版が出したもの」だけを置く場所という区別を保つため）

### 6. `RUBYLIB` は対応しない（確定）

外部仕様5章は `RUBYLIB` を `-L` と同等とするが、Python 版では意味が無い。[[tecsgen-python3 P0基本方針決定]] で「5章の執筆時に決める」（当時は TBC）とされていた件。決定: 対応しない。代わりの環境変数も作らない。

## 実装の順序

1. `Host.resolve_plugin_file`・`RecordedHost` の対応表・`PluginModule` のレジストリ化と探索（組み込みの探索は従来どおり通ること＝既存の一致が落ちないこと）
2. 縦の一本通し: `through`（`Plugin1.py`・`Plugin2.py`）。`@@generated_celltype` の副作用による import 行の差が消えるのを確認
3. `domainPlugin`・`ErrorCase/domainPlugin-err`・`region`・`restrict`・`generate`
4. `CPPBridge`・`SWIGBridge`（基底プラグインの移植状況を先に確認）
5. 外部仕様（5章・プラグイン章）と内部仕様（9章相当）を更新

## Consequences

- 利用者は Ruby で書いたプラグインを Python に書き直す必要がある（クラス名・メソッド名は Ruby と同じ。ブロックや `@@` 変数などの Ruby 固有部分だけ置き換え）
- `-L` で指したディレクトリのコードをそのまま実行する。Ruby 版と同じ信頼モデルで、外部仕様に明記する

## 実装結果

2026-10-01、手順1〜5を実施済み（実装は外部リポジトリのブランチ `ykominami/tecsgen-python3-Loption`、コミット `f78de87`・`f18c6ae`）。`-L` 待ちの8ケースがすべて一致した。一致状況・経緯は [[tecsgen-python3移植計画 — P5 進捗ログ#P5q（2026-10-01）|P5q]]、仕様は [[tecsgen-python3内部仕様 - 09 プラグイン機構]]。`generate` は、テスト同梱の `ATK1TaskPlugin.rb`（標準版と大きく違う）を移植しなくても組み込み版で一致した。組み込み優先の探索順と矛盾しないが、Ruby 版が標準版を読んだことは、探索順から言える（2026-10-03、`require_tecsgen_lib` のコード読み。実行での確認ではない）。`$library_path` の先頭は `$tecsgen_base_path` で、`tecslib/plugin/<名前>.rb` が存在すれば `require` して打ち切るため、`-L` のディレクトリにある同名ファイルには到達しない。

## Related

- [[tecsgen-python3移植計画]] — P5 の持ち越し
- [[tecsgen-python3 パッケージ構成決定]] — クラス名＝ファイル名
- [[tecsgen-python3 P0基本方針決定]] — `-L`・`RUBYLIB` の方針
- [[tecsgen-python3外部仕様]]
- [[tecsgen-python3内部仕様 - 12 グローバル変数一覧]]
- [[tecsgen-python3]]

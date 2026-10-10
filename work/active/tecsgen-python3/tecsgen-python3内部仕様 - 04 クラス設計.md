---
date: 2026-09-27
description: "tecsgen-python3内部仕様4章（P3範囲）。型・値・式・コンポーネントモデルのモジュール対応、mixinの写し方、Ruby互換の仕組み（Symbolクラス・dualmethod・未代入ivarのnil化・クラス変数とreset）、再現したRuby版の癖"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

# tecsgen-python3 内部仕様 4章 クラス設計

[[tecsgen-python3内部仕様]] の4章。移植元は [[work/active/tecsgen/tecsgen内部仕様 - 04 クラス設計|Ruby版 4章]]。P3（2026-09-27）で移植したモデルクラスの範囲を記述する。最適化・生成の再オープン部分（`optimize.rb`・`generate.rb`）は P4、プラグインは P5 で追記する。

## 4.1 モジュール対応

[[tecsgen-python3 パッケージ構成決定]] のとおり、Ruby と1ファイル対1モジュール（`src/tecsgen/core/`）。名前を変えたものだけ挙げる。

| Ruby | Python | 理由 |
|---|---|---|
| `types.rb` | `cdl_types.py` | 標準ライブラリ `types` との衝突回避 |
| `ctypes.rb` | `c_types.py` | 標準ライブラリ `ctypes` との衝突回避 |
| `import.rb` | `componentobj/import_cdl.py` | `import` は予約語 |
| `celltypeModule.rb` | `componentobj/celltype_module.py` | snake_case |
| `pluginModule.rb` | `plugin_module.py` | 同上 |

- `syntaxobj/`: `decl`・`paramdecl`・`paramlist`・`funchead`・`typedef`・`cdlstring`・`cdlinitializer`（`node`・`namedlist` は P1）
- `componentobj/`: `namespace`・`region`・`namespacepath`・`signature`・`celltype`・`celltype_module`・`port`・`cell`・`join`・`reversejoin`・`compositecelltype`・`compositecelltypejoin`・`factory`・`domaintype`・`classtype`・`importable`・`import_cdl`・`import_c`・`generate`
- `value.py`（`IntegerVal` など）・`expression.py`（`Expression`・`C_EXP`）
- 文法アクションが参照するクラスは `syntax/_model.py` にまとめて import する（アクションのモジュールから循環 import を避けるため）

## 4.2 mixin の写し方

[[tecsgen-python3 Mixin粒度決定]] に従い、Ruby の `include` は多重継承にし、MRO は include を書いた順の逆に並べる。

- 型検査のときだけ mixin を本体クラスの子として見せる（`if TYPE_CHECKING:` で基底を切り替える）。実行時の基底は `object`。`CType`（`c_types.py`）と `CelltypePluginModule`（`celltype_module.py`）がこの形
- `Celltype` と `CompositeCelltype` の基底はどちらも `(CelltypePluginModule, PluginModule, NSBDNode)`。2つの mixin に同名のメソッドは無いので、この順序は実行時の挙動に影響しない（ty の MRO 検査を通すための並び）
- `generate.rb` の再オープン部分のうち、意味解析から呼ばれるものだけを P3 で移した（`core/generate.py` の `NamespaceGenerate` の `travers_all_*`、`Celltype` のクラス変数）。残りは P4

## 4.3 Ruby 互換の仕組み

[[tecsgen-python3内部仕様 - 12 グローバル変数一覧#12.3 Ruby 互換の書き方規約（`ruby_compat.py`）|12.3 の規約]]に、P3 で次を加えた。

### Symbol

P1・P2 では Ruby の Symbol を `str` で表していたが、P3 で **`Symbol` クラス**（`ruby_compat.py`、`str` の派生）を導入した。

- 等値比較とハッシュ値だけを `str` と区別する。Ruby では `:abc == "abc"` が偽で、Hash のキーとしても別物になる。tecsgen には識別子（Symbol）と連結結果（String）を比べたり、Hash を引いたりする箇所があり、意図せず一致しないものもある。それを再現しないとモデルが Ruby 版と一致しない
- 連結や書式化の結果は `str`（Ruby の String）になる
- リテラルは `Y.NAME`（Ruby の `:NAME`）、変換は `sym(x)`（`to_sym`・`intern`）
- 字句解析器は識別子・キーワードの `Token.val` を `Symbol` で作る。`NamedList` は名前が `Symbol` でなければ `RubyRuntimeError` にする

### 同名のクラスメソッドとインスタンスメソッド（`dualmethod`）

Ruby では `Namespace.find(path)` と `ns.find(name)` が別メソッドとして共存する。`dualmethod` デスクリプタで、クラスから引いたかインスタンスから引いたかによって呼び分ける。`StructType` の `set_define`・`new_member`・`end_of_parse`、`DescriptorType.check_signature` なども同じ形。

### 未代入のインスタンス変数

Ruby は代入前の `@x` を nil として読める。`Node.__getattr__` が、通常の探索で見つからない `_x` を `None` として返す。既定値をクラス属性で与えないのは、モデルのダンプでクラス変数と混ざるため。

### クラス変数

- Ruby の `@@x` はクラス属性（`ClassVar`）にし、**クラス名を明示して**読み書きする（`Namespace._x`）。`cls._x` や `self._x` への代入は子クラスやインスタンスに別の値を作ってしまい、Ruby の「継承階層で1つ」と食い違う
- 同じ名前のクラス変数とインスタンス変数を両方持つクラス（`Cell` の `_cell_list` など）は、インスタンス側を `self.__dict__["_x"]` で読み書きする
- 各クラスが `reset()` を持ち、`state.reset_model_state()` がまとめて初期値に戻す（Ruby 版は1プロセス1回の実行なので不要な処理。pytest で1プロセス内に何度も実行するため）

### その他

- `class_name(cls)`: Ruby のクラス名。入れ子クラスは `RUBY_NAME`（`"TECSGEN::Makefile"`）で与える
- 文字列の数値変換（`String#to_i`・`oct`・`hex`・`to_f`）、整数変換（`Integer()`）、シフトなどは `ruby_compat.py` の関数（`str_to_i`・`rb_integer`・`rb_lshift` など）で Ruby の結果に合わせる
- 未定義メソッドの呼び出しなど、Ruby 版が例外になる箇所は `RubyNoMethodError` などを送出して同じ所で止まるようにした

## 4.4 再現した Ruby 版の癖

モデルとエラー出力を Ruby 版と一致させるため、意図と違うと思われる挙動もそのまま移した。移植元のコメントを付けてある。

- `! x.instance_of? Port || ...` は、括弧の無いメソッド呼び出しの引数が `Port || ...` 全体になるので、`!x.instance_of?(Port || ...)` と解釈される。`Port` は真なので後半は評価されず、結果は `!x.instance_of?(Port)`。Ruby の実際の解釈どおりに書いた
- `elements_check_dir_for_param` の `when ..., :PARENTHESES,` の末尾カンマにより、次の行の呼び出しが `when` の候補の一部になっている
- `callable_from?` は真偽値ではなく配列を返す
- `ParamList#to_str` は型オブジェクトを String に足すので、パラメータが1つでもあると TypeError（`RubyTypeError`）
- `Makefile.add_var` は未定義のクラス変数、`add_pre_tecsgen_target` は未定義のローカル変数を参照して例外になる

## 4.5 プラグイン

`plugin_module.py` の `PluginModule.load_plugin` は、P3 の時点では `PluginNotPorted` を送出するだけだった。P5（2026-09-27〜10-01）で `importlib` による名前解決に置き換え、標準付属プラグインは 85 本中 83 本を移植済み（as of 2026-10-03。残る `HRP2Cache`・`HRP2PostHook` は動かす経路が無く対象外）。呼び出し箇所（`generate` 指定子、through、domain・class の各プラグイン）は Ruby どおり移植してある。ロードの仕組みと `-L` の探索は [[tecsgen-python3内部仕様 - 09 プラグイン機構|9章]] を参照。

## Ruby版との差異

- モデルの構造・属性は Ruby 版と一致させる（[[tecsgen-python3内部仕様 - 06 意味解析#6.4 差分テスト|6.4]] のダンプ比較で確認）
- `TOOL_INFO`（`__tool_info__`）は P5l〜P5p で移植済み（2026-10-01）。`--help`・`--version` は Ruby 版とバイト一致（2026-10-02、P6b。テスト `tests/test_p3_cli.py`）。`-v` の差は Ruby/Python のバージョン行と同梱 CDL のインストール先パスだけで、意図した差（[[tecsgen-python3外部仕様 - 05 コマンドラインインターフェース|外部仕様 5章]]）

## Related

- [[tecsgen-python3内部仕様]] — 目次
- [[tecsgen-python3 Mixin粒度決定]] / [[tecsgen-python3 パッケージ構成決定]]
- [[tecsgen-python3内部仕様 - 06 意味解析]]
- [[tecsgen-python3移植計画]] — P3
- [[work/active/tecsgen/tecsgen内部仕様 - 04 クラス設計|Ruby版 4章]]

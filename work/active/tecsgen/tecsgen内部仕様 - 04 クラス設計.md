---
date: 2026-08-16
description: "tecsgen内部仕様書 第4章（クラス設計）— クラス階層、Generator・Namespace・Cell・Join・Pluginクラス。MultiPluginがPluginではなくNode直下である点を訂正。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 4 of 12.

## 4. クラス設計

### 4.1 クラス階層

```
Node                            # 基底クラス（locale 管理・エラー出力）
  ├── BDNode                    # Born-from-Declaration Node（名前・大域名管理）
  │     ├── NSBDNode            # Namespace/BDNode（ネームスペース文脈）
  │     │     ├── Namespace     # 名前空間ツリーノード
  │     │     │     └── Region  # リンクルート・ドメイン・クラス
  │     │     ├── Signature     # シグニチャ定義
  │     │     ├── Celltype      # セルタイプ定義
  │     │     │     └── CompositeCelltype  # 複合セルタイプ
  │     │     └── Cell          # セルインスタンス
  │     └── Join                # 結合記述（呼び口=セル.受け口 / 属性=値）
  ├── Port                      # 呼び口・受け口定義
  ├── FuncHead                  # シグニチャ関数ヘッダ
  ├── ParamDecl                 # パラメータ宣言
  ├── Decl                      # 型・属性・変数宣言
  ├── Typedef                   # typedef 宣言
  ├── Factory                   # factory{} / FACTORY{} 記述
  ├── C_EXP                     # C_EXP(式) ラッパ
  └── MultiPlugin                # ★ Plugin ではなく Node の直下（9.5参照）。get_plugin(superClass) で
                                  #   CelltypePlugin/SignaturePlugin/ThroughPlugin/CellPlugin いずれかの
                                  #   具象サブクラスへ委譲するディスパッチャであり、自身はそれらを継承しない

Plugin                          # プラグイン基底クラス
  ├── CelltypePlugin             # セルタイププラグイン基底
  ├── SignaturePlugin            # シグニチャプラグイン基底
  ├── ThroughPlugin              # through プラグイン基底
  └── CellPlugin                 # セルプラグイン基底
```

> [!warning] MultiPlugin は Plugin 階層の外側にある
> 一見すると「4種のプラグイン基底クラスをまとめる上位クラス」に見えるが、`MultiPlugin < Node`（9.5）であり `Plugin` を継承しない。`PluginModule#load_plugin` が `plClass <= MultiPlugin` を判定してから `get_plugin(superClass)` に委譲する二段構えになっているのはこのため——素直に `Plugin` の下に置いてディスパッチメソッドを1つ追加する設計も可能だったはずだが、実際には別系統の基底クラスとして実装されている。理由はソースから読み取れず未検証。

### 4.2 Generator クラス（bnf.y.rb）

`Generator` は Singleton パターン（クラスメソッドのみ）で実装される。

| 機能 | メソッド |
|------|---------|
| エラー出力 | `Generator.error(msg, *arg)` / `error2(locale, msg, *arg)` |
| 警告出力 | `Generator.warning(msg, *arg)` / `warning2(locale, msg, *arg)` |
| 情報出力 | `Generator.info(msg, *arg)` / `info2(locale, msg, *arg)` |
| エラー件数 | `Generator.get_n_error` / `get_n_warning` / `get_n_info` |
| 現在 locale | `Generator.current_locale` → `[@file, @lineno, @col]` |
| 構文解析完了通知 | `Generator.end_all_parse` |

`@@n_error` が 0 でない場合、コード生成フェーズはスキップされる。

### 4.3 Namespace クラス

```ruby
class Namespace < NSBDNode
  @name_list          # NamedList: Signature/Celltype/Cell/Typedef/Namespace
  @struct_tag_list    # NamedList: StructType
  @namespace_list     # Namespace[]
  @signature_list     # Signature[]
  @celltype_list      # Celltype[]
  @compositecelltype_list  # CompositeCelltype[]
  @cell_list          # Cell[]（Region のみ保持）
  @typedef_list       # Typedef[]
  @decl_list          # (Typedef|StructType|EnumType)[] 順序保持
  @const_decl_list    # Decl[]
end
```

ルート名前空間は `Region.new("::")` で生成される（Namespace と Region を兼ねる）。

ネームスペーススタック（`@@namespace_stack`）で現在のパース文脈を管理する。

### 4.4 Cell クラス

```ruby
class Cell < NSBDNode
  @celltype           # Celltype | CompositeCelltype
  @join_list          # NamedList: Join（呼び口結合・属性初期化）
  @reverse_join_list  # NamedList: ReverseJoin
  @b_defined          # Bool: 定義済み（prototype との区別）
  @b_checked          # Bool: set_definition_join 完了フラグ
  @require_joined_list # {cp_name=>true}: set_require_join 済み呼び口
  @generate           # [PluginName, option, Plugin]: generate 指定子
  @generate_list      # [[PluginName, option, Plugin], ...]: 全 generate
  @entry_array_max_subscript  # {Port=>Integer}: 受け口配列の最大添数
  @referenced_port_list       # {Port=>Integer}: 受け口参照カウント
end
```

### 4.5 Join クラス

```ruby
class Join < BDNode
  # 左辺
  @name          # Symbol: 属性名 or 呼び口名
  @subscript     # nil=非配列 / -1=添数未指定 / >=0=添数
  @definition    # Port | Decl: set_definition_join で解決
  # 右辺（ポート結合の場合）
  @cell          # Cell: 右辺のセル
  @port          # Port: 右辺の受け口
  @array_member  # rhs 配列（同名初回のみ）
  @array_member2 # Join[] 配列（同名初回のみ）
  @through_list  # cp_through + region_through + ep_through
end
```

### 4.6 Plugin クラス

プラグインは `gen_cdl_file` メソッドで CDL コードを生成し、その後 import で再解析される。コード生成段階では `gen_ep_func_body` でセルタイプの受け口関数本体を生成できる。

| メソッド | 呼び出し段階 | 説明 |
|---------|------------|------|
| `initialize(plugin_arg_str, next_cell, next_cell_opt)` | 構文解析時 | インスタンス生成・引数パース |
| `set_locale(locale)` | 構文解析完了後 | エラー locale の設定 |
| `gen_cdl_file(file)` | 意味解析後（ポストコード） | CDL コードを生成 |
| `gen_ep_func_body(...)` | コード生成 | 受け口関数本体を C で生成 |
| `gen_preamble(file, ...)` | コード生成 | preamble コードを出力 |
| `gen_postamble(file, ...)` | コード生成 | postamble コードを出力 |
| `new_cell(cell)` | ポストコードパース後 | 新しいセルが生成されたとき |

---


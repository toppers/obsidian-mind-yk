---
date: 2026-09-26
description: "tecsgen-python3移植でRuby版のクラス再オープン（Namespace等が7ファイルにまたがる）をPythonのMixinへ変換する際の粒度を決定。「クラス×関心事」単位でMixinを作り、Rubyの関心事ファイル構成をPythonモジュールとして踏襲する方針"
project: tecsgen-python3
status: proposed
quarter: Q3-2026
tags:
  - decision
---

# Decision: tecsgen-python3 Mixin粒度決定

## Context
[[reference/Rubyクラス再オープンとpython対応|Rubyクラス再オープンとpython対応]]の実測調査（[[reference/tecsgen_ruby_class_reopen.csv|tecsgen_ruby_class_reopen.csv]]）により、Ruby版[[tecsgen]]の中核クラス（`Namespace`が7ファイル、`Celltype`が6ファイル、`Cell`/`Signature`が各5ファイル等、計24クラス/モジュール）が「再オープン」パターンで複数ファイルにまたがって定義されていることが確定した。[[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]]へPython移植する際、Pythonにはクラス再オープンが存在しないため、[[reference/Ruby Mixinとpython多重継承対応|Mixin＋多重継承]]で置き換える必要がある。どの粒度でMixinを分割するかを決定する。

## 観察: 再オープンの軸は「クラス」ではなく「関心事（ファイル）」

実測データを`class`軸ではなく`ファイル`軸で読み直すと、再オープンの実体は「1つの関心事ファイルが複数の中核クラスを横断的に拡張する」構造だとわかる:

| 関心事ファイル | 拡張しているクラス |
|---|---|
| `generate.rb`（コード生成） | Namespace, Celltype, Signature, Typedef, StructType, Region, DomainType, ClassType |
| `optimize.rb`（意味解析・最適化） | Namespace, Celltype |
| `gen_xml.rb`（XML出力） | Namespace, Celltype, CompositeCelltype, Cell, Signature |
| `tecsinfo.rb`（診断情報） | Namespace, Celltype, Region, Cell, Signature, Port, FuncHead, Decl, ParamDecl, Type |
| `unjoin_plugin.rb`（unjoin処理） | Namespace, Celltype, CompositeCelltype, DomainType, Region, Signature, Cell, Join |
| `tecsflow.rb`（tecsflow連携） | Namespace, Cell |

つまりRuby版の設計は「1つの関心事＝1ファイル、そのファイルが必要なクラス全てに機能を追加する」という**横断的な関心事分離**であり、クラス単位のばらばらな再オープンではない。

## Options Considered

1. **クラス単位でMixinをまとめる**（`namespace_mixins.py`に`Namespace`用の全Mixinを集約、`celltype_mixins.py`に`Celltype`用を集約...）
   - 長所: Python側で「このクラスに関係するものは全部ここ」と一箇所に集まる
   - 短所: Ruby側の関心事ファイル（`generate.rb`一つ）が、Python側では8個以上のファイルに分散して同じロジックの断片が撒かれることになり、**Ruby原文との対応が追いにくくなる**。移植検証（原文と実装の突き合わせ）のコストが上がる

2. **関心事（Ruby元ファイル）単位でMixinをまとめる**（`generate.py`に`NamespaceGenerateMixin`/`CelltypeGenerateMixin`/...を全部集約、ファイル対ファイルで1対1対応）
   - 長所: **Ruby版の`generate.rb`とPython版の`generate.py`が1対1で対応**し、移植時・検証時に「このRubyファイルの内容はこのPythonファイルに移した」と機械的に追跡できる。既存の実測調査手法（AST突き合わせ）や[[Patterns - 検証と調査|一次資料を実際に読んで検証する]]という当vaultの検証パターンとも相性が良い
   - 短所: 1ファイル内に複数クラス向けのMixinが並ぶ（`generate.py`に8個のMixinクラス）ため、ファイルが大きくなりやすい。ただし現状のRuby版`generate.rb`自体が5000行超の巨大ファイルであることを踏まえると、Python側で関心事ごとに分割された時点で十分な改善になる

3. **完全に再設計する**（Ruby側のファイル境界を無視し、Python側で最適な関心事分割をゼロから設計）
   - 長所: 理想的な設計にできる可能性
   - 短所: Ruby原文との対応関係が失われ、移植の正しさ検証が困難になる。[[Patterns - 検証と調査]]で繰り返し確認されている教訓（一次資料との突き合わせなしに設計すると誤りに気づけない）に反する。現時点でPython版の意味解析・コード生成ロジックがまだ検証されていない段階でこれを行うのはリスクが高い

## Decision

**オプション2（関心事＝Ruby元ファイル単位でMixinをまとめる）を採用する。**

- Mixin命名規則: `<ClassName><Concern>Mixin`（例: `NamespaceGenerateMixin`, `CelltypeOptimizeMixin`, `NamespaceTecsinfoMixin`）
- ファイル配置: Ruby版のファイル構成をそのままPythonモジュールとして踏襲する
  - `generate.rb` → `generate.py`（`NamespaceGenerateMixin`・`CelltypeGenerateMixin`・`SignatureGenerateMixin`・`TypedefGenerateMixin`・`StructTypeGenerateMixin`・`RegionGenerateMixin`・`DomainTypeGenerateMixin`・`ClassTypeGenerateMixin`を1ファイルにまとめる）
  - `optimize.rb` → `optimize.py`
  - `gen_xml.rb` → `gen_xml.py`
  - `tecsinfo.rb` → `tecsinfo.py`
  - `unjoin_plugin.rb` → `unjoin_plugin.py`
  - `tecsflow.rb` → `tecsflow.py`
- 各クラスの「本体（`componentobj/<name>.rb`相当）」は`componentobj/<name>.py`に`<ClassName>Core`として定義（データ・`__init__`・継承関係のみ）
- 最終的な合成クラスは、[[reference/Ruby Mixinとpython多重継承対応|Mixin設計の実践ルール（Mixinを先、基底クラスを後）]]に従い、各`componentobj/<name>.py`の末尾（または専用の集約モジュール）で以下のように組み立てる:

```python
# componentobj/namespace.py の末尾、または assembly.py に集約
from generate import NamespaceGenerateMixin
from optimize import NamespaceOptimizeMixin
from gen_xml import NamespaceGenXmlMixin
from tecsinfo import NamespaceTecsinfoMixin
from unjoin_plugin import NamespaceUnjoinMixin
from tecsflow import NamespaceTecsflowMixin

class Namespace(
    NamespaceGenerateMixin,
    NamespaceOptimizeMixin,
    NamespaceGenXmlMixin,
    NamespaceTecsinfoMixin,
    NamespaceUnjoinMixin,
    NamespaceTecsflowMixin,
    NamespaceCore,
):
    pass
```

- Mixinには状態（インスタンス変数）を持たせない（[[reference/Ruby Mixinとpython多重継承対応|Mixin設計の実践ルール]]通り）。`__init__`・データ属性は`<ClassName>Core`のみが持つ

## Consequences

- **良い点**: Ruby原文の1ファイル＝Python移植後の1ファイルという対応が保たれるため、[[Patterns - 検証と調査|一次資料との突き合わせによる検証]]がしやすい。移植を関心事ファイル単位（例: まず`generate.rb`→`generate.py`だけ移植）で段階的に進められ、[[Patterns - 仕様書と実装|実装セッション区切りでのこまめなコミット]]という既存パターンとも整合する
- **注意点**: 1つのPythonファイルに複数クラス向けのMixinが並ぶため、命名規則（`<ClassName><Concern>Mixin`）を厳守しないと可読性が落ちる。また合成クラスの組み立て箇所（末尾 or 集約モジュール）は今後の実装時に確定する必要がある
- **実装で確定した事項（2026-10-03 確認、TBC 解消）**:
  - 合成クラスは、各 `componentobj/<name>.py` のモデルクラス自身が基底に mixin を並べる形にした（`class Namespace(NamespaceTECSInfo, NamespaceOptimize, NamespaceGenerate, NSBDNode)` など）。専用の `assembly.py` は作っていない。mixin の名前は `<ClassName><Concern>`（`Mixin` の接尾辞は付けない）
  - MRO 順序: 基底を2つ以上持つクラス18個を実行で調べ、mixin 間で同名のメソッドを定義するものは無かった。列挙順はメソッド解決に影響しない（並びは ty の MRO 検査のため）
  - `TECSCDE`・`TECSGEN` のような componentobj 以外の再オープン: `TECSCDE` は `tecscde.rb` ごと計画のスコープ外（[[tecsgen-python3 パッケージ構成決定]]）。`TECSGEN` は Ruby で4ファイルにまたがるが、Python 版は `core/tecsgen.py` の1クラス。`location.rb` は読み込まれず、`tool_info.rb` の位置情報（`Cell_location`・`Join_location`、`TECSGEN.new_cell_location` など）は他から使われない obsolete なコードなので移植していない（`core/tool_info.py` の docstring に明記）
- **未決定事項として残るもの**: なし

## Related
- [[tecsgen]] — Ruby実装版
- [[reference/Rubyクラス再オープンとpython対応|Rubyクラス再オープンとpython対応]] — 本決定の前提となった実測調査
- [[reference/Ruby1ファイル複数クラスとpython対応|Ruby1ファイル複数クラスとpython対応]] — 「1関心事ファイルに複数クラス向けMixin」構成が可能な前提知識（Pythonのファイル=モジュール=名前空間の性質）
- [[reference/tecsgen_ruby_class_reopen.csv|tecsgen_ruby_class_reopen.csv]] — 実測データ
- [[reference/Ruby Mixinとpython多重継承対応|Ruby Mixinとpython多重継承対応]] — Mixin設計の実践ルール
- [[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]] — 親ノート
- [[work/active/tecsgen-python3/tecsgen-python3内部仕様|tecsgen-python3内部仕様]] — 本決定を反映すべき内部仕様書

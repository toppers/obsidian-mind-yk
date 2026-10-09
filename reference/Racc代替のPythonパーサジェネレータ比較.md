---
date: 2026-09-26
description: "Racc（LALR(1)パーサジェネレータ）のPython対応物としてLark/SLY/ANTLR4を比較。tecsgenのbnf.y.rb（Racc製）をPython移植する際の候補整理"
tags:
  - reference
---

# Racc代替のPythonパーサジェネレータ比較

## Context
[[tecsgen]]（Ruby実装）は`tecslib/core/bnf.tab.rb`をRacc（LALR(1)パーサジェネレータ）で`bnf.y.rb`から生成している（[[Patterns - 検証と調査 Archive#Ruby構造解析は正規表現の行走査でなくAST（`RubyVM::AbstractSyntaxTree`）を使う（2026-09-24）|関連: Ruby構造解析の調査]]で`bnf.tab.rb`に触れた際に判明）。[[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]]でRacc相当のPython製パーサジェネレータを検討する際の候補整理。

> [!info] 既存方針との関係（2026-09-26確認）
> [!success] 結論（2026-09-27）
> 代替ジェネレータも tree-sitter も使わず、Ruby 版の racc が生成済みの LALR 表を取り出して Python で駆動する方式にした（純 Python、DLL 不要）→ [[tecsgen-python3 構文解析方式決定]]。以下は検討当時の記録。

> `tecsgen-python3`はtree-sitter製CDL/Cパーサ（TypeScript版[[TECSCDE-DT-EL実装]]等と共用済み）を既に採用しているが、**Pythonから利用する際はDLL（ネイティブバイナリ、`web-tree-sitter`のWASM運用とは別に、Python側は`tree-sitter`パッケージ経由でネイティブ言語パーサをビルド・ロードする構成が推奨）を使う運用になり、複雑になる可能性がある**。本ノートはそのDLL依存を避けられる代替手段の調査として、Racc（LALR文法→パーサ生成）のPython対応物であるLark/SLY/ANTLR4を比較したもの。tree-sitterを置き換える決定ではなく、**DLLなしで運用できる選択肢の候補出し**の段階。

## 候補比較

### 第一候補: Lark
- LALR(1)パーサを実装しており、位置付けがRaccに最も近い
- `pip install lark`（現行1.3.x系、活発にメンテされている）
- Racc同様、文法定義から構文木を自動生成する
- LALR(1)に加えてEarley法（曖昧な文法もOK）も選べ、Raccより柔軟性が高い

```python
from lark import Lark

grammar = r"""
    start: expr
    expr: expr "+" term   -> add
        | term
    term: term "*" factor -> mul
        | factor
    factor: NUMBER
    %import common.NUMBER
    %ignore " "
"""

parser = Lark(grammar, parser="lalr")
tree = parser.parse("1 + 2 * 3")
print(tree.pretty())
```

### 第二候補: SLY
- yacc/Raccと最も文法定義スタイルが近い（BNFに近い記法）
- PLYの後継、作者は同じDavid Beazley氏
- `pip install sly`
- 更新頻度はLarkより低く、事実上メンテナンスモードに近い

### 参考: ANTLR4（Pythonターゲット）
- LL(*)方式で、Raccとはアルゴリズムが異なるが、大規模な文法（言語処理系など）で実績が豊富
- Java製のジェネレータで`.g4`文法から`antlr4-tools`でPythonコードを生成する2段構え
- 別言語ランタイム込みの運用になるため、単一言語で完結させたいなら不向き

## tree-sitterのPython利用がDLLを要する具体的な仕組み（実測手順）

前段の「DLL運用が推奨される」という主張の具体的な仕組みを確認しておく。ネイティブCライブラリ（`.so`/`.dylib`/`.dll`）としてコンパイルしたtree-sitterパーサは、**`ctypes`経由でCシンボル（関数ポインタ）を整数アドレスとして取得し、`tree_sitter.Language(ptr)`に渡して初期化する**ことでPythonから利用する。

1. **ビルド**: `npx tree-sitter generate`で出力される`src/parser.c`（外部スキャナがあれば`src/scanner.c`も）を共有ライブラリとしてコンパイルする（`gcc -O3 -shared -fPIC -Isrc src/parser.c -o mylang.so`等）。この時点で`tree_sitter_<言語名>()`という、パーサ定義へのポインタを返す関数がエクスポートされる
2. **ロード**: Python側は`ctypes.cdll.LoadLibrary("./mylang.so")`でこの共有ライブラリを読み込み、`lang_func.restype = ctypes.c_void_p`でポインタ型を明示した上で`lang_func()`を呼んで`TSLanguage`ポインタ（整数アドレス）を取得
3. **初期化**: `Language(language_ptr)`に渡してパーサを初期化、以後は`Parser(MY_LANGUAGE)`で通常通りパースできる

**結論として確認できたこと**: tree-sitterをPythonから使う標準的な方法は、事前にコンパイルされたネイティブ共有ライブラリ（＝DLL/`.so`）を`ctypes`でロードする経路であり、これは[[reference/tecsgen動的typedef判定とPythonパーサ選定|前段で指摘した「動的typedef判定にはexternal scanner＝DLLが要る」]]という制約と表裏一体——tree-sitterを使う限り、**文法適用そのものにも、動的字句解析の拡張にも、いずれもネイティブビルド成果物が必要**になる。「DLLなしでtree-sitterを使う」余地はほぼ無く、DLL回避を優先するなら[[reference/Racc代替のPythonパーサジェネレータ比較|本ノートの結論]]通りLark/SLYへの切り替えが現実的な選択肢になる。

## 結論
RaccのようにLALR(1)で「文法→パーサ生成」という設計思想を素直に踏襲したいなら **Lark（`parser="lalr"`モード）** が最有力。TOPPERS/TECS関連でDSL的な文法を扱う想定があれば、Larkの`%import`やTransformerによるAST構築の仕組みがRaccの`Racc::Parser`役割に近く、移行コストも低い。

**DLL回避という観点では**: Lark・SLYはいずれも純Python実装（コンパイル済みネイティブ拡張への依存なし）で、tree-sitterのようなネイティブバイナリ/DLLビルドが不要。ANTLR4はJavaランタイムでのコード生成が必要な点で「単一言語で完結」から外れるため、DLL回避が目的ならLark/SLYが候補、ANTLR4は除外方向（TBC・未検証）。

## Related
- [[tecsgen]] — Ruby実装版、Raccベースの`bnf.tab.rb`/`bnf.y.rb`
- [[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]] — Python3移植の親ノート（現行方針はtree-sitter、本ノートとの関係は要確認）
- [[reference/Ruby動的ロードとPython対応|Ruby動的ロードとPython対応]] — 同じくtecsgen-python3移植検討で作成したRuby→Python対応リファレンス
- [[reference/tecsgen動的typedef判定とPythonパーサ選定|tecsgen動的typedef判定とPythonパーサ選定]] — 本ノートの比較結果を踏まえ、Ruby版の動的typedef判定機構がtree-sitter/Lark/SLYでどう再現できるかを検討。DLL依存という制約は本ノートの`ctypes`実測手順とも整合

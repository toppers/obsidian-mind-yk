---
date: 2026-06-18
description: "tecsgen コードベース graphify 知識グラフ構築セッション記録 — 238ファイル・3230ノード・God Nodes 4件（Celltype/Cell/Inline/CELLIDX）・Surprising Connections 4件特定・Obsidian/Wiki エクスポート完了"
tags:
  - reference
  - tecs
  - tecsgen
  - graphify
---

関連: [[TECS開発]]

❯ /graphify ./tecsgen

./tecsgen サブディレクトリへの新規グラフ構築リクエストです。まずパスを確認します。

Step 1 - インストール確認 & Step 2 - ファイル検出

  Ran 1 shell command

./tecsgen = E:\Crepo\ykominami_private\tecsgen\tecsgen を対象に新規グラフを構築します。既存の graphify-out/ を上書きします。

  Ran 2 shell commands

検出結果:
Corpus: 238 files · ~268,583 words
  code:   233 files (.rb)
  docs:     5 files (.txt)

238ファイル・コード中心のコーパスです。--mode deep なし。

意味抽出が必要: 5ファイル (doc) → 1エージェント、約45秒。
AST (233 Rubyファイル) と並行実行します。

Step B0 - キャッシュ確認

  Ran 1 shell command

5ファイル全てキャッシュヒット。意味抽出はスキップして Part C に進みます。AST抽出のみ実行します。

● Write(graphify-out\_ast2.py)
Wrote 26 lines to graphify-out\_ast2.py
import sys, json, io
from pathlib import Path

def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    from graphify.extract import collect_files, extract

    code_files = []
    detect = json.loads(Path('graphify-out/.graphify_detect.json').read_text(encoding='utf-8'))
    for f in detect.get('files', {}).get('code', []):
… +18 lines

  Ran 1 shell command

Part C - キャッシュ済み意味抽出 + AST をマージ

● Write(graphify-out\_merge2.py)
Wrote 42 lines to graphify-out\_merge2.py
mport sys, json, io
rom pathlib import Path

ef main():
   sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
   from graphify.cache import check_semantic_cache

   detect = json.loads(Path('graphify-out/.graphify_detect.json').read_text(encoding='utf-8'))
   non_code = [f for ftype in ['document','paper','image'] for f in detect['files'].get(ftype, [])]
… +34 lines

  Ran 1 shell command

Step 4 - グラフ構築・クラスタリング

● Write(graphify-out\_build2.py)
Wrote 42 lines to graphify-out\_build2.py
import sys, json, io
from pathlib import Path

def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    from graphify.build import build_from_json
    from graphify.cluster import cluster, score_all
    from graphify.analyze import god_nodes, surprising_connections, suggest_questions
    from graphify.report import generate
    from graphify.export import to_json
… +35 lines

  Ran 1 shell command

サブディレクトリのみが対象のため、ノード数が減るのは正常です。force=True で上書きします。

● Write(graphify-out\_build2.py)
Added 1 line, removed 1 line

    report = generate(G, communities, cohesion, labels, gods, surprises, detection, tokens, '.', sugges
ted_questions=questions)
    Path('graphify-out/GRAPH_REPORT.md').write_text(report, encoding='utf-8')
    to_json(G, communities, 'graphify-out/graph.json')
    to_json(G, communities, 'graphify-out/graph.json', force=True)

    analysis = {
        'communities': {str(k): v for k, v in communities.items()},

  Ran 1 shell command

Step 5 - コミュニティラベリング

● Write(graphify-out\_show2.py)
Wrote 16 lines to graphify-out\_show2.py
import sys, json, io
from pathlib import Path

def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    analysis = json.loads(Path('graphify-out/.graphify_analysis.json').read_text(encoding='utf-8'))
    communities = {int(k): v for k, v in analysis['communities'].items()}
    sizes = {cid: len(nodes) for cid, nodes in communities.items()}
    top20 = sorted(sizes.items(), key=lambda x: -x[1])[:20]
    for cid, size in top20:
… +6 lines

  Ran 1 shell command

● Write(graphify-out\_label2.py)
Wrote 51 lines to graphify-out\_label2.py
mport sys, json, io
rom pathlib import Path

ef main():
   sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
   from graphify.build import build_from_json
   from graphify.cluster import score_all
   from graphify.analyze import suggest_questions
   from graphify.report import generate
… +43 lines

  Ran 1 shell command

Step 6 - HTML生成 & クリーンアップ

  Ran 2 shell commands

グラフ完成。E:\Crepo\ykominami_private\tecsgen\graphify-out\ に出力されました。

  graph.html      - ブラウザで開くインタラクティブグラフ (フルノードビュー)
  GRAPH_REPORT.md - 監査レポート
  graph.json      - 生グラフデータ

---
God Nodes

1. Celltype - 最多接続
2. Cell - 2位
3. Inline - 3位
4. CELLIDX - 4位

Surprising Connections

  Searched for 2 patterns

---
Surprising Connections

- celltype_plugin_new_cell() → print_exception() [INFERRED] celltypeModule.rb → tecsgen.rb
- parse() → print_exception() [INFERRED] C_parser.y.rb → tecsgen.rb
- generate_and_parse() → set_plugin() [INFERRED] pluginModule.rb → bnf.y.rb
- load_plugin() → require_tecsgen_lib() [INFERRED] pluginModule.rb → tecsgen.rb

Suggested Questions

- Type はなぜ4つの異なるコミュニティを橋渡しするか? (betweenness 0.020)
- StructType はなぜ Community 27・52・37・78 を繋ぐか? (betweenness 0.013)
- Node はなぜ5コミュニティにまたがるか? (betweenness 0.013)

---
最も興味深い質問: Type がなぜ NBO TDR Inline Marshaling・CDE Palette UI・Type System and Values など全く異なるコミュニティを橋渡しするのか? これを追いたいですか?

✻ Baked for 3m 19s

※ recap: Built knowledge graphs for the tecsgen project using graphify — first the full repo (5,845 nodes), then the tecsgen subdirectory alone (3,230 nodes). Both are in graphify-out/ with HTML and Obsidian vault exports complete. (disable recaps in /config)

❯ /graphify ./tecsgen --obsidian --obsidian-dir C:\0-MD-2\_ARCHIVE\ObsidianVault2\tecsgen

./tecsgen のグラフは直前のセッションで構築済み (graphify-out/graph.json = 3230ノード、./tecsgen が対象)。--obsidian エクスポートのみ実行します。

  Ran 1 shell command

完了。

C:\0-MD-2\_ARCHIVE\ObsidianVault2\tecsgen\
  3,459 ノートファイル (./tecsgen サブディレクトリのグラフ)
  graph.canvas  — Obsidian Canvas コミュニティマップ

前回の全体グラフ (6,581ノート) より小さく、tecsgen/ の Ruby コードと関連ドキュメントに絞った内容です。Obsidian で同じボルトパスを開くと上書きされた状態になります。

✻ Cooked for 36s

※ recap: tecsgenプロジェクトのナレッジグラフ構築が完了。全体（804ファイル）と`./tecsgen`サブディレクトリ（238ファイル）の2つのグラフを生成し、ObsidianボルトとHTMLビジュアライザーを出力済み。次のアクションは特になし。

❯ /graphify ./tecsgen --wiki

./tecsgen のグラフは構築済み。Wiki エクスポートを実行します。まず exports 仕様を確認します。

  Read 1 file, ran 1 shell command

完了。

graphify-out/wiki/
  index.md         - エージェントエントリポイント (229コミュニティ + サマリー)
  239 articles     - コミュニティごとの記事

wiki/index.md をエージェントに渡せば、コードベース全体をコミュニティ単位でナビゲートできます。CLAUDE.md に @graphify-out/wiki/index.md と書くと、将来のセッションでグラフ知識が自動的に読み込まれます。

✻ Sautéed for 37s

❯ /graphify ./tecsgen --svg

既存の ./tecsgen グラフに対して SVG エクスポートのみ実行します。

  Ran 1 shell command

matplotlib が未インストールです。インストールしてリトライします。

  Ran 6 shell commands

完了。

graphify-out/graph.svg  - SVGグラフ (Notion・GitHub README・Obsidianに埋め込み可能)

GitHub README に貼る場合: ![tecsgen graph](graphify-out/graph.svg)
Notion に貼る場合: SVGファイルをドラッグ&ドロップでブロックとして挿入できます。

✻ Worked for 1m 39s

❯ /graphify ./tecsgen --graphml

  Ran 1 shell command

GraphML エクスポートに問題があります。lxml の不足に加え、グラフデータにリスト型の属性が含まれており、GraphML フォーマットがリスト値をサポートしないためエラーになっています。

これは graphify 側のシリアライズ問題です。lxml をインストールしても根本原因は解決しません。

回避策として、Gephi/yEd で使いたい場合は同等の情報を持つ代替フォーマットが使えます:

- graph.json — NetworkX や Python で直接読み込める (属性制限なし)
- Neo4j/FalkorDB — --neo4j で Cypher ファイル生成 (Gephi も Cypher インポート対応)

GraphML が必要な場合は graphify の Issue として報告することを推奨します。現状のグラフデータは graphify-out/graph.json で完全に保存されています。

✻ Brewed for 25s

❯ /graphify ./tecsgen --neo4j

  Ran 1 shell command

完了。

graphify-out/cypher.txt  - Neo4j Cypher インポートファイル

インポート方法:
cypher-shell -u neo4j -p <password> < graphify-out/cypher.txt

または Neo4j Browser で graphify-out/cypher.txt の内容をペーストして実行してください。MERGE を使っているので重複なく何度でも再実行できます。

✻ Baked for 12s

※ recap: tecsgenプロジェクトのknowledge graphを構築してObsidian・Wiki・SVG・Neo4j Cypherなど各種フォーマットにエクスポートしました。現在のgraphify-outはtecsgenサブディレクトリのグラフ（3230ノード）が対象です。次の操作を指示してください。
  
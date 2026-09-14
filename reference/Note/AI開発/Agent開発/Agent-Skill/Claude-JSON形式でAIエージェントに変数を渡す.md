---
date: 2026-07-23
description: "Claude Code のスキルで JSON ファイルを読み込んで変数として扱えるかの回答 — SKILL.md 自体は変数を持たず、指示に従って実行するスクリプト側が変数を持つ構造になる"
tags:
  - reference
  - claude-code
  - skill
---

claude code のskill で、特定の指定JSONファイルを読み込み、変数群に値を設定し、それらの変数群を参照することはできますか

できます。ただし「Skill(SKILL.md)自体が変数を持つプログラム」ではなく、「SKILL.mdの指示に従ってClaudeがスクリプトを実行し、そのスクリプト側で変数を持つ」という構造になります。この違いを理解しておくと設計を間違えません。

**仕組み**

SKILL.mdはMarkdownで書かれたプロンプト(自然言語の指示書)です。JSONパースや変数代入のような処理はSKILL.md自身には書けません。実際の処理は、SKILL.mdから呼び出す補助スクリプト(bash/Python/Node/Rubyなど、`scripts/`配下に置くファイル)が担当します。

**パターン1: スクリプトに変数管理を任せる(推奨)**

SKILL.mdには「このJSONを読んで、こう使え」という指示だけ書き、実処理はPythonスクリプトに閉じ込めます。

```python
# scripts/load_config.py
import json
import sys

with open(sys.argv[1]) as f:
    config = json.load(f)

api_key = config["api_key"]
target_dir = config["target_dir"]
options = config.get("options", {})

# 以降、api_key / target_dir / options を通常のPython変数として参照
print(f"loaded target_dir={target_dir}")
```

SKILL.md側には「`python3 scripts/load_config.py path/to/config.json` を実行し、その出力に基づいて次のステップに進め」のように書きます。変数のスコープはそのスクリプトプロセス内に閉じます。

**パターン2: bash + jq で環境変数化して、以降のコマンド列で参照**

一連のbashコマンドを跨いで値を使い回したいなら、jqで抽出してexportします。

```bash
API_KEY=$(jq -r '.api_key' config.json)
TARGET_DIR=$(jq -r '.target_dir' config.json)

echo "target: $TARGET_DIR"
# 後続のコマンドで $API_KEY, $TARGET_DIR を参照
```

これはClaude Codeが同一Bashセッション内でコマンドを連続実行する場合に有効です。ただしCowork環境のようにBash呼び出しごとに環境がリセットされる場合は、1回のシェルコマンド内(`&&`で連結、またはヒアドキュメント)で完結させる必要があります。

**パターン3: Claude自身がJSONを読んで「文脈上の変数」として保持**

Read toolでJSONの中身を読み、その値をClaudeが会話コンテキストで覚えておき、後続のEdit/Bash呼び出しのパラメータとして埋め込む、というやり方も可能です。ただしこれは「プログラム変数」ではなく「Claudeが読んだ値を後で使う」だけなので、値の数が多い・繰り返し参照する用途にはパターン1か2の方が確実です。

**実践上の指針**

- 設定値が数個で使い捨てなら:パターン3(Claudeが読んで直接使う)で十分
- 設定値を条件分岐や複数ステップで繰り返し参照するなら:パターン1(Pythonスクリプトに閉じ込める)が安全。型チェックやデフォルト値処理もしやすい
- シェルスクリプト中心のワークフロー(ファイル一括処理など)なら:パターン2(jq+環境変数)が軽量

もし具体的にどんなJSON構造・どんな用途(例えば設定ファイルからAPIキーとパスを読んでバッチ処理する、など)を想定しているか教えてもらえれば、そのユースケースに合わせたSKILL.md + スクリプトの雛形を書きます。
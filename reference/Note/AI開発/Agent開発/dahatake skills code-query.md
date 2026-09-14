---
date: 2026-08-29
description: "dahatake/skills の code-query（cq）CLIヘルプ控え — index/stats/search/def/get/refs/trace/watch/mapサブコマンドの全オプション"
tags:
  - reference
  - ai
  - agents
---
[[dahatake skills code-query reference]]
[[dahatake skills code-query 実装]]
# code-query の使い方

code-query（エンジン名 cq）は、ソースコードを横断検索して定義・参照・小さな snippet だけを返すツール。markdown-query の姉妹版で、.md は索引せずソースコード専用（.py, .cs, .js, .ts, .sh, .ps1 など）。

1. 導入（未導入のリポジトリの場合）

対象リポジトリのルートで実行（git 管理下である必要あり）:

# Windows
pwsh -NoLogo -NoProfile -File code-query\install.ps1
# macOS/Linux
bash code-query/install.sh

これで cq.toml（索引対象設定）・.github/skills/code-query/（Skill定義）・.cq/（SQLite索引）が生成される。cq.toml が無いと全コマンド fail-closed で止まる。

2. よく使うコマンド

python -m cq stats  --profile <profile>                          # 索引の存在・規模確認
python -m cq index  --profile <profile>                          # 索引作成/更新
python -m cq search --profile <profile> --q "<探したい語>"        # 検索（既定: auto mode, top-k 5）
python -m cq search --profile <profile> --q "<語>" --return-unit chunk  # 関数/クラス単位で本文ごと取得
python -m cq def    --profile <profile> --symbol <Class.method>  # 定義へ直行
python -m cq refs   --profile <profile> --symbol <symbol>        # 呼び出し元を列挙
python -m cq get    --profile <profile> --chunk-id <ID>          # snippet で不足時に本文取得
python -m cq map    --profile <profile> --paths "<dir>/*" --max-tokens 1200  # 俯瞰マップ
python -m cq watch  --profile <profile>                          # 保存を即座に索引反映

配布キット経由でインストールした場合は python -m cq は使えない（vendor化されているため）。同梱ランチャを使う:

code-query\cq.ps1 search --q "<探したい語>"
bash code-query/cq.sh search --q "<探したい語>"

profile が1つだけなら --profile 省略可。複数ある場合は --profile <名> か $env:CQ_PROFILE / export CQ_PROFILE= で指定。

3. 検索モード（--mode auto が既定で自動判定）


│     探したいもの     │ 判定されるモード │
│ FR-CQ-06 などのID    │ trace            │
│ 関数名・クラス名     │ symbol           │
│ 記号を含む部分文字列 │ substr           │
│ 正規表現             │ --re "<pattern>" │
│ 自然文・複数語       │ bm25             │


0件時は自動フォールバック（bm25→or-fallback→path一致）する。結果の route/match フィールドで経路を確認できる。

4. このリポジトリ自身で試す例

mkdir -p /tmp/demo/src && cd /tmp/demo && git init -q && \
  printf 'def resolve_run_id(name):\n    return name.upper()\n' > src/app.py && \
  git add -A && git -c user.email=ci@example.com -c user.name=ci commit -qm init
bash /path/to/skills/code-query/install.sh --skip-prereq --repo-root /tmp/demo
cd /tmp/demo
bash tools/code-query/cq.sh search --q resolve_run_id

詳細は code-query/skill/SKILL.md（フル仕様）、code-query/GETTING-STARTED.md（導入手順）、code-query/USAGE.md（日常運用）を参照。


## Related
- [[dahatake skills]]

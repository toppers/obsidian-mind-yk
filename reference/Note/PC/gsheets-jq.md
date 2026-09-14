---
date: 2026-06-22
description: "gsheets/jq クイックリファレンス — TRANSPOSE/SPLIT 数式・tecsgen インストール済みプラグイン一覧取得"
tags:
  - reference
  - cli
---

# gsheets / jq クイックリファレンス

## gsheets
```
=TRANSPOSE(SPLIT(A2, CHAR(10)))
```

## jq
```sh
jq '.plugins | keys[]' /home/ykomi/repo/svn-toppers-TECS-2/git-svn-y/toppers/tecsgen/installed_plugins2.json
```

## Related
- [[tecsgen内部仕様]]

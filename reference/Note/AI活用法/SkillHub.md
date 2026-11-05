---
date: 2026-08-08
description: "SkillHub ランタイムの起動・停止コマンド控え。runtime.sh を curl で取得して up/down、Web UI は :80・API は :8080、本番は --public-url でURL指定"
tags:
  - reference
  - skill
  - cli
source: https://github.com/iflytek/skillhub
---

curl -fsSL https://imageless.oss-cn-beijing.aliyuncs.com/runtime.sh | sh -s -- up

SkillHub runtime started.
Web UI: http://localhost
Backend API: http://localhost:8080
Runtime dir: /tmp/skillhub-runtime
Stop with:
  curl -fsSL https://raw.githubusercontent.com/iflytek/skillhub/main/scripts/runtime.sh | sh -s -- down

# 本番向け：パブリックURLを指定して起動
curl -fsSL https://imageless.oss-cn-beijing.aliyuncs.com/runtime.sh | sh -s -- up \
  --public-url https://skillhub.your-company.com

## Related

- [[Claude-Code-Skills]]
- [[Skillの分類]]

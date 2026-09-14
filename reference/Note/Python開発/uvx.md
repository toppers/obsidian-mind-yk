---
date: 2026-05-16
description: "uvx の実行例 — gcloud の認証後、PYTHONUTF8 と chcp 65001 を設定して google-agents-cli setup を走らせる"
tags:
  - reference
  - python
  - uv
---

gcloud auth application-default login

Bash($env:PYTHONUTF8=1; chcp 65001 | Out-Null; uvx google-agents-cli setup)
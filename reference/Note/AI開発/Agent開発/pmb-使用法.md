---
date: 2026-06-30
description: "PMB のセットアップ選択肢の比較表 — 埋め込みモデルのRAM使用量と、CJK など希少スクリプトの想起精度のトレードオフ"
tags:
  - reference
  - agent
  - pmb
---

│       #  Option               RAM      Good for                 Plus / minus                                         │
│       1  Light & fast         ~0.5 GB  any machine, <=8 GB RAM  + tiny, fast, works everywhere                       │
│                                                                 - weaker cross-language & rare-script (CJK) recall   │
│   ◆   2  Balanced  (current)  ~1.1 GB  12 GB+ RAM               + noticeably more accurate, same family (no extra    │
│                                                                 setup)                                               │
│                                                                 - ~2x the RAM, a bit slower than Light               │
│       3  Best quality         ~2 GB    16 GB+ RAM               + best cross-language + CJK, sharpest matching       │
│                                                                 - heavy RAM, slower on CPU, longer first load        │

│       #  Option                         Needs                            Plus / minus                                │
│   ◆   1  Auto (recommended)  (current)  nothing if you use Claude Code   + zero setup - Claude CLI if present,       │
│                                                                          else API key, else Ollama                   │
│                                                                          - uses whatever is available (less          │
│                                                                          explicit)                                   │
│       2  Claude CLI                     `claude` in PATH                 + no API key - reuses your Claude Code      │
│                                                                          auth                                        │
│                                                                          - requires Claude Code installed            │
│       3  Ollama (local)                 `ollama serve` + a pulled model  + fully local & private, no cloud           │
│                                                                          - you run the server; quality depends on    │
│                                                                          the local model                             │
│       4  Anthropic API                  ANTHROPIC_API_KEY                + fast, nothing to install locally │

│  ✓  found claude-code, cursor, codex, gemini                                                                         │
│  ✓  wired into claude-code  +hooks  +shared-daemon E:\Ccur\python3\xyz\.mcp.json      │
│  ✓  memory engine ready                                                                                              │
│  ✓  remembered & recalled in 815 ms                                                                                  │




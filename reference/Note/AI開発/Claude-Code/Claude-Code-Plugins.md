---
date: 2026-06-04
description: "Claude Code のプラグイン/MCP接続状況ダンプと整理メモ。要対応(auth待ち・failed)のMCP、User/Project/claude.ai スコープ別の一覧、X印で不要候補をマーク"
tags:
  - reference
  - claude-code
  - plugin
  - mcp
---

# Needs attention
X  ❯ aws-mcp MCP · ✘ failed
X    vercel MCP · △ Enter to auth
X    vercel MCP · △ Enter to auth
X    cloudflare-api MCP · △ Enter to auth
X    claude.ai Stripe MCP · △ Enter to auth
======
User

x  ❯ amazon-location-service Plugin · claude-plugins-official · ✔ enabled
    endless-toil Plugin · endless-toil · ✔ enabled
    obsidian Plugin · obsidian-skills · ✔ enabled
x    rust-analyzer-lsp Plugin · claude-plugins-official · ✔ enabled
x    vercel Plugin · claude-plugins-official · ✔ enabled
x    vercel Plugin · vercel · ✔ enabled
    wiki Plugin · llm-wiki · ✔ enabled
    agentmemory MCP · ✔ connected
  ❯ codex MCP · ✔ connected

claudeai

    claude.ai Bitly MCP · ✔ connected
    claude.ai Box MCP · ✔ connected
    claude.ai Canva MCP · ✔ connected
    claude.ai Cloudflare Developer Platform MCP · ✔ connected
    claude.ai Context7 MCP · ✔ connected
    claude.ai Figma MCP · ✔ connected
    claude.ai Gmail MCP · ✔ connected
    claude.ai Google Calendar MCP · ✔ connected
    claude.ai Google Drive MCP · ✔ connected
  ❯ claude.ai Hugging Face MCP · ✔ connected
    claude.ai Mermaid Chart MCP · ✔ connected
    claude.ai PayPal MCP · ✔ connected
    claude.ai Slack MCP · ✔ connected

===============
# claude Plugins
qmd
llm-wiki Plugin 
vercel MCP
cloudflare-api MCP
claude.ai GitLab MCP
claude.ai Strip MCP

Project
slack MCP 

User
agemntmemory Plugin
amazon-location-service Plugin
endless-toil Plugin · endless-toil
obsidian Plugin · obsidian-skills
rust-analyzer-lsp Plugin · claude-plugins-official
vercel Plugin · claude-plugins-official 
vercel Plugin · vercel 
wiki Plugin · llm-wiki
agentmemory MCP
codex MCP 

claudeai

    claude.ai Bitly MCP · ✔ connected
    claude.ai Box MCP · ✔ connected
    claude.ai Canva MCP · ✔ connected
    claude.ai Cloudflare Developer Platform MCP · ✔ connected
    claude.ai Context7 MCP · ✔ connected
    claude.ai Figma MCP · ✔ connected
    claude.ai Gmail MCP · ✔ connected
    claude.ai Google Calendar MCP · ✔ connected
    claude.ai Google Drive MCP · ✔ connected
    claude.ai Hugging Face MCP · ✔ connected
    claude.ai Mermaid Chart MCP · ✔ connected
    claude.ai PayPal MCP · ✔ connected
  ❯ claude.ai Slack MCP · ✔ connected

## Related

- [[MCP-LIST]]
- [[Claude-Code-Skills]]

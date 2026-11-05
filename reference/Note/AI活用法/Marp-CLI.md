---
date: 2026-04-19
description: "Marp CLI でスライドを変換するコマンド控え — Markdown から HTML への変換と出力先の指定"
tags:
  - reference
  - marp
  - cli
---

# Convert slide deck into HTML
npx @marp-team/marp-cli@latest slide-deck.md
npx @marp-team/marp-cli@latest slide-deck.md -o output.html

# Convert slide deck into PDF
npx @marp-team/marp-cli@latest slide-deck.md --pdf
npx @marp-team/marp-cli@latest slide-deck.md -o output.pdf

# Convert slide deck into PowerPoint document (PPTX)
npx @marp-team/marp-cli@latest slide-deck.md --pptx
npx @marp-team/marp-cli@latest slide-deck.md -o output.pptx

# Watch mode
npx @marp-team/marp-cli@latest -w slide-deck.md

# Server mode (Pass directory to serve)
npx @marp-team/marp-cli@latest -s ./slides

[GitHub \- marp\-team/marp\-cli: A CLI interface for Marp and Marpit based converters · GitHub](https://github.com/marp-team/marp-cli)

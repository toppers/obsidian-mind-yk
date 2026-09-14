---
date: 2026-08-29
description: "dahatake/skills の markdown-query（mdq index）CLIヘルプ控え — heading/semantic_paragraph/pageindex/graphrag等チャンク戦略の全オプション"
tags:
  - reference
  - ai
  - agents
---

# dahatake skills mdq index

usage: mdq index [-h] [--db DB] [--lang {ja-jp,en-us}]
                 [--strategy {heading,heading_recursive,fixed_window,semantic_paragraph,pageindex,graphrag}] [--root ROOT]
                 [--tabular TABULAR] [--rebuild] [--no-prune] [--max-chunk-chars MAX_CHUNK_CHARS]
                 [--overlap-paragraphs OVERLAP_PARAGRAPHS] [--breakpoint-percentile-lo BREAKPOINT_PERCENTILE_LO]
                 [--breakpoint-percentile-hi BREAKPOINT_PERCENTILE_HI] [--min-chars MIN_CHARS] [--embed-provider EMBED_PROVIDER]
                 [--embed-model EMBED_MODEL] [--no-semantic-contextualize] [--late-chunking]
                 [--pageindex-summary-chars PAGEINDEX_SUMMARY_CHARS] [--pageindex-summary-mode {head,first_paragraph}]
                 [--graphrag-working-dir GRAPHRAG_WORKING_DIR] [--graphrag-llm-provider {ollama,mock}]
                 [--graphrag-llm-model GRAPHRAG_LLM_MODEL] [--graphrag-embed-provider {ollama,mock}]
                 [--graphrag-embed-model GRAPHRAG_EMBED_MODEL] [--graphrag-base-url GRAPHRAG_BASE_URL]
                 [--graphrag-allow-remote-ollama] [--graphrag-timeout GRAPHRAG_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --db DB               SQLite store path. If omitted, resolves to .mdq/index-<lang>-<strategy>.sqlite via --lang/--strategy.
  --lang {ja-jp,en-us}  Tokenize language (default: ja-jp). Selects FTS5 tokenizer and the per-language DB instance.
  --strategy {heading,heading_recursive,fixed_window,semantic_paragraph,pageindex,graphrag}
                        Markdown chunking strategy (default: heading). 'graphrag' uses LightRAG (SQLite-independent; see
                        --graphrag-* options).
  --root ROOT           Index root (repeatable). When omitted, roots are resolved from mdq.toml / .mdq/config.toml
                        ([index].roots) or fall back to the built-in generic defaults. See mdq.config.
  --tabular TABULAR     Repo-root-relative glob of a CSV/TSV file indexed row-by-row (repeatable). When omitted, resolved from
                        [index].tabular in mdq.toml / .mdq/config.toml. Empty means no tabular file is indexed.
  --rebuild             Rebuild even if file hashes match
  --no-prune            Do not remove store entries for files that no longer exist on disk (default: prune enabled)
  --max-chunk-chars MAX_CHUNK_CHARS
                        If >0, sub-split chunks larger than this many chars at paragraph/line boundaries (code fences stay
                        intact). 0 disables (default).
  --overlap-paragraphs OVERLAP_PARAGRAPHS
                        heading_recursive strategy only: prepend trailing N paragraphs of each text sub-chunk to the next
                        (overlap window). Defaults to mdq.strategies.HEADING_RECURSIVE_OVERLAP_PARAGRAPHS (=1).
  --breakpoint-percentile-lo BREAKPOINT_PERCENTILE_LO
                        semantic_paragraph: lower bound of percentile binary search (default: 50).
  --breakpoint-percentile-hi BREAKPOINT_PERCENTILE_HI
                        semantic_paragraph: upper bound of percentile binary search (default: 99).
  --min-chars MIN_CHARS
                        semantic_paragraph: minimum chunk size in chars (default: 200). Shorter sub-chunks are merged into
                        predecessor.
  --embed-provider EMBED_PROVIDER
                        semantic_paragraph: embedding provider name. Falls back to MDQ_EMBED_PROVIDER env or 'fastembed'
                        (default).
  --embed-model EMBED_MODEL
                        semantic_paragraph: embedding model name. Falls back to MDQ_EMBED_MODEL env or
                        'intfloat/multilingual-e5-large' (default; MIT, ~2.2GB first DL).
  --no-semantic-contextualize
                        semantic_paragraph: disable the default-on contextualizer template (Q11=B). When set, chunk text is raw
                        body only.
  --late-chunking       semantic_paragraph: enable late-chunking pass (Q9=B). Embeds each final chunk and persists vectors into
                        the chunk_embedding column for linear-weighted retrieval fusion.
  --pageindex-summary-chars PAGEINDEX_SUMMARY_CHARS
                        pageindex: per-chunk summary length in characters (0 uses code default PAGEINDEX_SUMMARY_CHARS=200).
  --pageindex-summary-mode {head,first_paragraph}
                        pageindex: summary extraction mode (default: 'head' — first N chars of the body). 'first_paragraph'
                        picks the first paragraph, clipped to N chars.
  --graphrag-working-dir GRAPHRAG_WORKING_DIR
                        graphrag: LightRAG storage directory (default: .mdq/graphrag-<lang>/).
  --graphrag-llm-provider {ollama,mock}
                        graphrag: LLM provider for entity/relation extraction (default: ollama). Use 'mock' for offline testing
                        — produces deterministic stub completions with no external dependency.
  --graphrag-llm-model GRAPHRAG_LLM_MODEL
                        graphrag: LLM model name (default: qwen2.5:7b; ignored when provider=mock).
  --graphrag-embed-provider {ollama,mock}
                        graphrag: embedding provider (default: ollama).
  --graphrag-embed-model GRAPHRAG_EMBED_MODEL
                        graphrag: embedding model name (default: nomic-embed-text; ignored when provider=mock).
  --graphrag-base-url GRAPHRAG_BASE_URL
                        graphrag: Ollama base URL for both LLM and embedding (default: http://127.0.0.1:11434). Must be a
                        loopback URL unless --graphrag-allow-remote-ollama is set.
  --graphrag-allow-remote-ollama
                        graphrag: allow non-loopback Ollama base URL. Emits a RuntimeWarning. Use only on trusted networks.
  --graphrag-timeout GRAPHRAG_TIMEOUT
                        graphrag: HTTP timeout for Ollama requests in seconds (default: 120).

## Related
- [[dahatake skills]]
- [[dahatake skills graphrag]]

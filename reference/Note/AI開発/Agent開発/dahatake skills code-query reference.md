---
date: 2026-08-29
description: "dahatake/skills の code-query（cq）CLIヘルプ控え — index/stats/search/def/get/refs/trace/watch/map 全サブコマンドのオプション一覧"
tags:
  - reference
  - tool
  - dahatake-skills
  - code-search
---

# usage
usage: cq [-h] {index,stats,search,def,get,refs,trace,watch,map} ...

local source-code search

positional arguments:
  {index,stats,search,def,get,refs,trace,watch,map}
    index               build or update the index
    stats               report index contents
    search              search the index
    def                 locate a definition without its body
    get                 print one chunk in full
    refs                list references to a symbol
    trace               resolve traceability between code and docs
    watch               keep the index current while sources change
    map                 token-budgeted overview of the codebase

options:
  -h, --help            show this help message and exit
## index
usage: cq index [-h] [--profile PROFILE] [--repo-root REPO_ROOT] [--db DB] [--rebuild]

options:
  -h, --help            show this help message and exit
  --profile PROFILE
  --repo-root REPO_ROOT
  --db DB               override the index path
  --rebuild
## stats
usage: cq stats [-h] [--profile PROFILE] [--repo-root REPO_ROOT] [--db DB]

options:
  -h, --help            show this help message and exit
  --profile PROFILE
  --repo-root REPO_ROOT
  --db DB               override the index path

## search
usage: cq search [-h] [--profile PROFILE] [--repo-root REPO_ROOT] [--db DB] [--q QUERY] [--re REGEX]
                 [--mode {auto,trace,symbol,substr,regex,bm25}] [--top-k TOP_K] [--max-tokens MAX_TOKENS]
                 [--snippet-radius SNIPPET_RADIUS] [--regex-max-candidates REGEX_MAX_CANDIDATES] [--paths PATHS]
                 [--return-unit {line,chunk}] [--auto-reindex-limit AUTO_REINDEX_LIMIT]

options:
  -h, --help            show this help message and exit
  --profile PROFILE
  --repo-root REPO_ROOT
  --db DB               override the index path
  --q QUERY
  --re REGEX
  --mode {auto,trace,symbol,substr,regex,bm25}
  --top-k TOP_K
  --max-tokens MAX_TOKENS
  --snippet-radius SNIPPET_RADIUS
  --regex-max-candidates REGEX_MAX_CANDIDATES
  --paths PATHS         GLOB filter over repository paths
  --return-unit {line,chunk}
                        excerpt granularity: 'line' keeps the --snippet-radius window; 'chunk' returns the whole matching chunk
                        and widens 'lines' to match, which fills --max-tokens with fewer hits
  --auto-reindex-limit AUTO_REINDEX_LIMIT
                        re-index up to N drifted files before answering (-1 disables the check)
## def
usage: cq def [-h] [--profile PROFILE] [--repo-root REPO_ROOT] [--db DB] --symbol SYMBOL [--top-k TOP_K]

options:
  -h, --help            show this help message and exit
  --profile PROFILE
  --repo-root REPO_ROOT
  --db DB               override the index path
  --symbol SYMBOL
  --top-k TOP_K
## get
usage: cq get [-h] [--profile PROFILE] [--repo-root REPO_ROOT] [--db DB] --chunk-id CHUNK_ID

options:
  -h, --help            show this help message and exit
  --profile PROFILE
  --repo-root REPO_ROOT
  --db DB               override the index path
  --chunk-id CHUNK_ID
## refs
usage: cq refs [-h] [--profile PROFILE] [--repo-root REPO_ROOT] [--db DB] --symbol SYMBOL [--top-k TOP_K]

options:
  -h, --help            show this help message and exit
  --profile PROFILE
  --repo-root REPO_ROOT
  --db DB               override the index path
  --symbol SYMBOL
  --top-k TOP_K
## trace
usage: cq trace [-h] [--profile PROFILE] [--repo-root REPO_ROOT] [--db DB] (--id TRACE_ID | --by-path BY_PATH) [--top-k TOP_K]

options:
  -h, --help            show this help message and exit
  --profile PROFILE
  --repo-root REPO_ROOT
  --db DB               override the index path
  --id TRACE_ID
  --by-path BY_PATH
  --top-k TOP_K

## watch
usage: cq watch [-h] [--profile PROFILE] [--repo-root REPO_ROOT] [--db DB] [--debounce-ms DEBOUNCE_MS]

options:
  -h, --help            show this help message and exit
  --profile PROFILE
  --repo-root REPO_ROOT
  --db DB               override the index path
  --debounce-ms DEBOUNCE_MS

## map
usage: cq map [-h] [--profile PROFILE] [--repo-root REPO_ROOT] [--db DB] [--paths PATHS] [--max-tokens MAX_TOKENS]
              [--format {text,json}]

options:
  -h, --help            show this help message and exit
  --profile PROFILE
  --repo-root REPO_ROOT
  --db DB               override the index path
  --paths PATHS         GLOB filter over repository paths
  --max-tokens MAX_TOKENS
  --format {text,json}

## Related

- [[dahatake skills code-query]]
- [[AIコーディングツール・知識グラフ・コードベース分析・リポジトリ管理ツールのリファレンスリスト]]

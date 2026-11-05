---
date: 2026-08-19
description: "QMD のクラス依存関係を Mermaid classDiagram 形式で出力した図（LLMSessionManager 等）"
project:
status: active
tags:
  - work-note
---

%% QMD (src/**/*.ts) class dependency diagram
%% Generated with the gen-class-dependency-diagram skill.
%%
%% Note: this codebase is almost entirely function-based (store.ts, db.ts,
%% cli/qmd.ts, mcp/server.ts, collections.ts, ast.ts, paths.ts export zero
%% classes). Only src/llm.ts and src/maintenance.ts define classes; the
%% TypeScript interfaces they implement/use (LLM, ILLMSession, Store) are
%% included here for context, marked "(interface)" in a comment since this
%% renderer's classDiagram parser rejects the double-angle-bracket stereotype
%% annotation block (even inside a comment).
%%
%% Excluded (include_external = false): SessionReleasedError extends the
%% built-in JS `Error` class — not drawn since it is external to the project.

classDiagram
    class Maintenance {
        -store: Store
        +vacuum()
        +cleanupOrphanedContent()
        +cleanupOrphanedVectors()
        +clearLLMCache()
        +deleteInactiveDocs()
        +clearEmbeddings()
    }

    class LlamaCpp {
        -llama: Llama
        -embedModel: LlamaModel
        -generateModel: LlamaModel
        -rerankModel: LlamaModel
        +embed()
        +embedBatch()
        +expandQuery()
        +rerank()
        +dispose()
    }

    class LLMSessionManager {
        -llm: LlamaCpp
        -activeSessionCount: number
        -inFlightOperations: number
        +acquire()
        +release()
        +canUnload() bool
        +getLlamaCpp() LlamaCpp
    }

    class LLMSession {
        -manager: LLMSessionManager
        -abortController: AbortController
        -released: bool
        +embed()
        +embedBatch()
        +expandQuery()
        +rerank()
        +release()
    }

    class SessionReleasedError {
        +name: string
    }

    %% (interface) src/llm.ts
    class LLM
    %% (interface) src/llm.ts
    class ILLMSession
    %% (interface) src/store.ts — type Store
    class Store {
        db
        dbPath
    }

    LLM <|.. LlamaCpp : 実装
    ILLMSession <|.. LLMSession : 実装
    Maintenance ..> Store : DB操作をラップ
    LLMSessionManager ..> LlamaCpp : モデル取得・操作を委譲
    LLMSession ..> LLMSessionManager : セッション管理を委譲
    LLMSession ..> SessionReleasedError : 例外生成

## Related
- [[reference/Note/AI開発/Claude-Code/MCP/QMD/QMD-クラス依存関係|QMD クラス依存関係]]

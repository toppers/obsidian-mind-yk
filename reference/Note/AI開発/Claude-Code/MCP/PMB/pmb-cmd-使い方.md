---
date: 2026-08-19
description: " PMB CMD の使い方"
tags:
  - reference
  - claude-code
  - mcp
  - pmb
---

Usage: pmb [OPTIONS] [COMMAND] [ARGS]...

 PMB - local-first memory for AI agents. Bare `pmb` opens the command palette (in a terminal) or the status dashboard
 (piped).

╭─ Options 
│ --help          Show this message and exit.                                                                          │

╭─ ✦ Setup & agents 
│ setup                Guided first-time setup - detect your agent and wire PMB in one go.  │
│ connect              Add a `pmb` entry to your agent's MCP config without touching other entries. │
│ doctor               Diagnose the installation and runtime state. │
│ ambient-watch        Ambient memory for MCP-only agents (Cursor, VS Code, Zed, Gemini, …).  │
│ codex-notify         Ambient memory for Codex: observe the turn's actions from the rollout │
│                      log and journal them if the agent didn't.                                                       │
│ hooks                Install force-feeding session-start hooks into your agent's config so PMB context arrives│
│                      BEFORE the model thinks.                                                                        │
│ mcp                  Run the MCP server. Stdio (per-developer) is the default; streamable-http exposes one shared    │
│                      instance to a team.                                                                             │
│ daemon               Manage the persistent memory daemon (warm hooks). │

╭─ Capture 
│ remember             Manually add a Q/A pair to memory. │
│ fact                 Record a standalone fact (project decision, preference, setting). │
│ note                 Instant capture - jot a memory straight from the terminal, no agent.│
│ learn                Teach PMB a durable LESSON - a correction or technique to apply going│
│                      forward, not just a one-off fact.                                                               │
│ distill              Auto-distill durable LESSONS & FAILURES from a session via an LLM. │
│ lessons              List the durable lessons PMB has learned (procedural memory). │
│ watch                Auto-capture: ingest new paragraphs from a notes file/folder into memory. │
│ sync                 Capture git commits into memory. │
│ import               Import existing memory from another tool - no more empty cold start.│
│ tag                  Tag a memory for local organization (collections). │
│ untag                Remove tag(s) from a memory. │
│ tags                 List all tags in this workspace with counts. │
│ tagged               List memories with a given tag (a local 'collection'). │
│ ttl                  Set (or clear) an expiry on a memory. │

╭─ Recall & explore 
│ recall               Search memory for relevant events. │
│ why                  Explain WHY recall ranked results the way it did - full PAMVR trace. │
│ overview             'What do I know about <topic>?' - a structured overview from memory.│
│ audit                'What does PMB know about me?' - a grouped, read-only view of memory.│
│ timeline             Chronological view of your memory - the story of a project, by day. │
│ insights             Personal analytics over your memory: size, growth, and top topics.│
│ digest               'What did I tell you recently?' - a quick recap of new memories. │
│ history              Commit history for a file. │
│ correlate            Files that frequently change together with the given one.  │
│ reminders            Proactive reminders: goals that are overdue or due soon. │
│ goals                List open goals, mark one done, or reconcile completed work. │
│ session              Manage sessions. `brief` = digest of what was decided/done this │
│                      session (re-orient after a long session / context loss). │

╭─ Maintain memory 
│ pin                  Pin an event - high importance, never auto-archived. │
│ forget               Archive an event (reversible). Restore with `pmb restore <ulid>`. │
│ forget-topic         Forget everything about a topic in one command (archives, reversible).│
│ forget-auto          Archive everything ambient auto-write recorded (source=autowrite). │
│ decay                Apply the forgetting curve, or (--archive-cold) archive cold stale facts. │
│ declutter            Sweep obvious junk out of memory (archive-only). │
│ dedupe               Improvement U: multi-layer dedup. │
│ prune-expired        Archive memories whose TTL has passed (set via `pmb ttl` / `--ttl`). │
│ prune-graph          Improvement V: prune weak co-occurrence edges to keep recall fast.│
│ compact              Compact storage: move old archived events to cold storage + VACUUM.  │
│ reindex              Re-embed all events with the current model. │
│ regraph              Wipe and rebuild the entity/edge graph from active events. │
│ repair-keyed         Collapse competing keyed facts onto one canonical value per attribute. │
│ rehearse             Spaced-repetition rehearsal - refresh important but idle memories.│
│ consolidate          LLM-based sleep-stage consolidation. │
│ reflect              PMB v2 - Reflective Memory. │
│ arcs                 PMB v2 - narrative arcs. │
│ feedback             Record real recall feedback. This drives adaptive importance over time.│
│ migrate-workspaces   Merge a per-project workspace into a unified memory (issue #7).│
│ schedule             Generate OS scheduler config (cron / Windows schtasks). │

╭─ Workspaces & data 
│ init                 Initialize a workspace in the current directory.    │
│ workspaces           List all known workspaces.                           │
│ stats                Statistics for the current workspace.                   │
│ list                 Recent events in the current workspace.              │
│ export               Export all memory to readable Markdown or JSON - your data, in the open. │
│ dashboard            Launch the local web dashboard - an interactive map of your memory.│
│ warmup               P1-1: Eagerly load model + BM25 + LanceDB so the next recall is fast. │
│ workspace            Git-backed workspace sync: push / pull / clone your memory to any remote.                       │
│ index                Index external content into PMB memory (PDFs, code projects). │
│ track                Semantic project tracking: what changed and WHY (git-tied), plus per-module purpose.            │
│ resume               Resume note: committable markdown of 'where we are now'.  │
│ memory               Memory Delta ledger: handles, rehydrate, status.  │
│ snapshot             Local, offline snapshots of your workspace (no cloud).  │

╭─ Agent internals 
│ prepare-context      Print a compact PMB context block for a user message. │
│ auto-context         Inspect what the auto-recall hook would inject for a given message. │
│ session-restore      Rebuild 'where you left off' after the agent's context compacts. │
│ lesson-followcheck   Infer lesson follow-through from recorded activity - no model needed. │
│ track-action         Log one observed agent action. Reads the PostToolUse hook JSON from                             │
│                      stdin and writes a single row to the agent_actions log. Instant, no │
│                      model. Significance (edit vs read) is judged at write time. │
│ autowrite            Journal what the agent did this turn - but ONLY if the agent didn't│
│                      record anything itself. Synthesizes one activity entry from the observed │
│                      action log (template by default; LLM if autowrite.synthesizer is set). │

╭─ More 
│ delete               Delete one or more memories - the clear front-door for removing things.│
│ restore              Restore an archived memory - undo a soft `pmb delete` / `pmb forget`.│
│ capture-exploration  Auto-capture an exploration memo from the transcript at turn end.│
│ model                Switch the embedding model and load it - download + re-embed memory +                           │
│                      restart the daemon, in ONE step.                                                                │
│ graph                Inspect the association graph (entities + edges). │
│ health               Health checks: self-test, trends, conflicts, user feedback. │
│ config               Inspect and tune PMB knobs from the console. │
│ ollama               Ollama integration - fully local LLM ops │
│ lang                 Manage language packs (extend lexical defaults). │


## Related
- [[reference/Note/AI開発/Claude-Code/MCP/PMB/PMB-使い方|PMB の使い方]]

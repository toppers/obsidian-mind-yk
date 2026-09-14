---
date: 2026-06-17T00:00:00.000Z
description: "llm-checkerによるモデル推薦出力 — Hardware Tier: MEDIUM HIGH、229モデル分析、カテゴリ別ベストモデル"
tags:
  - reference
  - ollama
  - local-llm
---

## 関連

- [[_ローカルLLM-まとめ]]
- [[Ollama-モデル]]
## 使い方
npx llm-checker hw-detect
npx llm-checker check
npx llm-checker ollama
npx llm-checker installed
npx llm-checker ollama-plan
npx llm-checker recommend

Check which LLM models your computer can run

Options:
  -V, --version                         output the version number
  -h, --help                            display help for command

Commands:
  help [command]                        Show all commands and how to use them
  mcp-setup [options]                   Show or apply MCP setup for llm-checker (Claude Code, Codex, Cursor, Windsurf, Gemini, Kimi,
                                        Grok, or generic)
  policy                                Manage enterprise policy files (policy.yaml)
  audit                                 Run policy audits and export compliance reports
  calibrate [options]                   Generate calibration contract artifacts from a JSONL prompt suite
  check [options]                       Analyze your system and show compatible LLM models
  ollama [options]                      Check Ollama integration status (use `installed` to rank installed models)
  installed [options]                   Show ranking of installed Ollama models by compatibility and use-case
  ollama-plan [options]                 Plan safe Ollama runtime settings for selected local models
  recommend [options]                   Get intelligent model recommendations for your hardware
  simulate [options]                    Simulate hardware profiles to see compatible LLM models for different systems
  list-models [options]                 List models (Ollama catalog by default; --registry/--source lists HF + Ollama + GPT4All)
  ai-check [options]                    AI-powered model evaluation with meta-analysis
  ai-run [options]                      AI-powered model selection and execution
  demo                                  Demo of the enhanced verbose progress with progress bars
  sync [options]                        Sync the model database from Ollama registry (scrapes all models)
  registry-sync [options]               Sync the multi-source model registry (Ollama, Hugging Face, GPT4All)
  registry-search [options] [query]     Search exact downloadable/installable artifacts in the multi-source model registry
  registry-recommend [options] [query]  Recommend the best exact model artifacts from the multi-source registry for this hardware
  search [options] <query>              Search models (Ollama catalog by default; --registry/--source searches HF + Ollama + GPT4All)
  smart-recommend [options]             Experimental recommendations using the alternate scoring engine
  gpu-plan [options]                    Multi-GPU placement advisor with safe model-size envelopes
  verify-context [options]              Verify practical context window limits for a local Ollama model
  verify [options] <file>               ModelVet: verify GGUF or safetensors structural safety before loading
  amd-guard [options]                   AMD/Windows reliability guard with actionable mitigation hints
  toolcheck [options]                   Tool-calling compatibility tester for local Ollama models
  hw-detect [options]                   Detect and display detailed hardware capabilities


## llm-checker推薦（2026-08-16）
AI-check
 AI-CHECK RESULTS
╭─────────────────────────────────────────────────────────────────
│ Evaluator: qwen2.5-coder:7b-base-q6_K

│ Models Evaluated: 12
│ 📝 Note: AI evaluation failed (Failed to run chat request: HTTP 404: Not Found - {"error":"model 'qwen2.5-coder:7b-base-q6_K' not found"}); showing deterministic results.
╰
╔═══════════════╤════════╤═════════════╤════════════╤═════════╤═════════════╤══════════╤═════════╤══════════════╗
║  Model        │  Size  │  Det Score  │  AI Score  │  Final  │  Fine-tune  │  RAM     │  Speed  │  Status      ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ qwen2.5-coder │ 7B     │ 62/100      │ N/A        │ 62/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ llama3.1      │ 7B     │ 62/100      │ N/A        │ 62/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ llama3.2      │ 7B     │ 62/100      │ N/A        │ 62/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ qwen2.5       │ 7B     │ 62/100      │ N/A        │ 62/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ gemma3        │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ mistral       │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ gemma2        │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ qwen3-coder   │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ codegemma     │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ qwen3         │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ gemma4        │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ gemma         │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╚═══════════════╧════════╧═════════════╧════════════╧═════════╧═════════════╧══════════╧═════════╧══════════════╝


 AI-POWERED RECOMMENDATION
╭──────────────────────────────────────────────────
│ Best Model: qwen2.5-coder
│ Final Score: 62/100
│ ⚖️  Det: 62 + AI: N/A
│ Fine-tuning: No accel
│
│ 📥 Install command:
│   ollama pull qwen2.5-coder
│
│ Why this model?
│   • fits in 8.308752/25.200000000000003GB, Q8_0, coder-tuned, 7B is sweet spot
│   • AI: evaluation failed
╰
 SYSTEM INFORMATION
╭──────────────────────────────────────────────────
│ CPU: Core™ Ultra 7 265K (20 cores, 3.9GHz)
│ Architecture: x64
│ RAM: 31GB
│ GPU: NVIDIA GeForce RTX 5070 Ti
│ Backend: NVIDIA CUDA
│ VRAM: 16GB (Dedicated)
│ Dedicated GPUs: NVIDIA GeForce RTX 5070 Ti
│ Integrated GPUs: Intel(R) Graphics
│ Hardware Tier: MEDIUM HIGH
╰

 SYSTEM INFORMATION
╭──────────────────────────────────────────────────
│ CPU: Core™ Ultra 7 265K (20 cores, 3.9GHz)
│ Architecture: x64
│ RAM: 31GB
│ GPU: NVIDIA GeForce RTX 5070 Ti
│ Backend: NVIDIA CUDA
│ VRAM: 16GB (Dedicated)
│ Dedicated GPUs: NVIDIA GeForce RTX 5070 Ti
│ Integrated GPUs: Intel(R) Graphics
│ Hardware Tier: MEDIUM HIGH
╰

 INTELLIGENT RECOMMENDATIONS BY CATEGORY
╭─────────────────────────
│ Hardware Tier: MEDIUM HIGH | Models Analyzed: 5308
│ Optimization: BALANCED | Runtime: AUTO
│ Source: Multi-source registry
│
│ BEST OVERALL: Qwen/Qwen3-8B
│    Command: hf download Qwen/Qwen3-8B
│    Score: 91/100 | Category: general
│    Quantization: Q4_K_M
│    Runtime: vllm | Source: huggingface
│    Fine-tuning: QLoRA
│
│ Coding (Coding):
│    Qwen/Qwen2.5-Coder-7B-Instruct-GGUF (7B)
│    Score: 79/100 | Pulls: 149,415
│    Quantization: Q6_K
│    Runtime: ollama | Source: huggingface
│    Fine-tuning: LoRA+QLoRA
│    Command: hf download Qwen/Qwen2.5-Coder-7B-Instruct-GGUF qwen2.5-coder-7b-instruct-q6_k-00001-of-00002.gguf
│
│ Reasoning (Reasoning):
│    MaziyarPanahi/Qwen3-14B-GGUF (14B)
│    Score: 89/100 | Pulls: 271,180
│    Quantization: Q6_K
│    Runtime: ollama | Source: huggingface
│    Fine-tuning: QLoRA
│    Command: hf download MaziyarPanahi/Qwen3-14B-GGUF Qwen3-14B.Q6_K.gguf
│
│ Multimodal (Multimodal):
│    Qwen/Qwen3-VL-8B-Instruct (8B)
│    Score: 91/100 | Pulls: 7,347,992
│    Quantization: Q4_K_M
│    Runtime: vllm | Source: huggingface
│    Fine-tuning: QLoRA
│    Command: hf download Qwen/Qwen3-VL-8B-Instruct
│
│ Creative (Creative):
│    Qwen/Qwen3-8B (8B)
│    Score: 89/100 | Pulls: 12,750,554
│    Quantization: Q4_K_M
│    Runtime: vllm | Source: huggingface
│    Fine-tuning: QLoRA
│    Command: hf download Qwen/Qwen3-8B
│
│ Talking (Chat):
│    Qwen/Qwen3-8B (8B)
│    Score: 89/100 | Pulls: 12,750,554
│    Quantization: Q4_K_M
│    Runtime: vllm | Source: huggingface
│    Fine-tuning: QLoRA
│    Command: hf download Qwen/Qwen3-8B
│
│ Reading (Reading):
│    athrael-soju/colqwen3.5-4.5B-v3 (4.5B)
│    Score: 87/100 | Pulls: 134,610
│    Quantization: Q4_K_M
│    Runtime: vllm | Source: huggingface
│    Fine-tuning: LoRA+QLoRA
│    Command: hf download athrael-soju/colqwen3.5-4.5B-v3 model.safetensors
│
│ General (General):
│    Qwen/Qwen3-8B (8B)
│    Score: 91/100 | Pulls: 12,750,554
│    Quantization: Q4_K_M
│    Runtime: vllm | Source: huggingface
│    Fine-tuning: QLoRA
│    Command: hf download Qwen/Qwen3-8B
│
╰
SYSTEM SUMMARY
──────────────────
CPU: Core™ Ultra 7 265K (20 cores)
Memory: 31GB RAM
GPU: NVIDIA GeForce RTX 5070 Ti
Architecture: x64
Backend: NVIDIA CUDA
Hardware Tier: MEDIUM HIGH

RECOMMENDED MODEL
──────────────────
Model: Mistral Small 3.1
Size: 15GB
Compatibility Score: 88.5/100
Fine-tuning: No FT
Reason: Best general-purpose model for your hardware
Estimated Speed: 46 tokens/sec
Runtime: Ollama
Status: Available for installation

Pull: ollama pull devstral-small-2

QUICK START
──────────────────
1. Install the recommended model:
   ollama pull devstral-small-2
2. Start using it:
   ollama run devstral-small-2

INSTALLED MODELS RANKING
╭──────────────────────────────────
│ Sorted by: score | Hardware: 31GB RAM
├──────────────────────────────────
╔═════╤═════════════════╤════════╤═══
║  #  │  Model          │  Size  │  Score  │  Use Case  │  Command               ║
╟─────┼─────────────────┼────────┼
║ 🥇  │ llama3.1:8b     │ 4.6GB  │ 85/100  │ general    │ ollama run llama3.1    ║
╟─────┼─────────────────┼────────┼
║ 🥈  │ qwen2.5:7b      │ 4.4GB  │ 84/100  │ general    │ ollama run qwen2.5     ║
╟─────┼─────────────────┼────────┼
║ 🥉  │ gemma4:latest   │ 8.9GB  │ 81/100  │ general    │ ollama run gemma4      ║
╟─────┼─────────────────┼────────┼
║ 4.  │ qwen3-coder:30b │ 17.3GB │ 75/100  │ coding     │ ollama run qwen3-coder ║
╚═════╧═════════════════╧════════╧═

 OLLAMA CAPACITY PLAN
Hardware: NVIDIA CUDA (cuda)
Memory budget: 14GB usable (reserve 2GB)

Selected models:
  - qwen3-coder:30b (30.5B, ~18GB base)

Recommended envelope:
  Context: 2048 (requested 8192)
  Parallel: 1 (requested 2)
  Loaded models: 1 (requested 2)
  Estimated memory: 19.22GB / 14GB (137%)
  Risk: CRITICAL (100/100)

Notes:
  - Requested settings exceed available memory budget; reduced settings are recommended.
  - No safe configuration fits the memory budget for this model selection; choose a smaller or more-quantized model.
  - Context reduced from 8192 to 2048 to avoid memory pressure.
  - Parallelism reduced from 2 to 1 to keep memory stable.
  - Loaded models capped at 1 for this objective and memory budget.

Recommended env vars:
  export OLLAMA_NUM_CTX=2048
  export OLLAMA_NUM_PARALLEL=1
  export OLLAMA_MAX_LOADED_MODELS=1
  export OLLAMA_MAX_QUEUE=4
  export OLLAMA_KEEP_ALIVE=15m
  export OLLAMA_FLASH_ATTENTION=1

Fallback profile:
  OLLAMA_NUM_CTX=2048 OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1

## llm-checker推薦（2026-06-17）

 INTELLIGENT RECOMMENDATIONS BY CATEGORY
╭─────────────────────────
│ Hardware Tier: MEDIUM HIGH | Models Analyzed: 229
│ Optimization: BALANCED
│
│ BEST OVERALL: granite4:7b-a1b-h
│    Command: ollama pull granite4:7b-a1b-h
│    Score: 90/100 | Category: general
│    Quantization: Q4_K_M
│    Fine-tuning: LoRA+QLoRA
│
│ Coding (Coding):
│    granite3.3:8b (8B)
│    Score: 85/100 | Pulls: 1,000,000
│    Quantization: Q4_K_M
│    Fine-tuning: QLoRA
│    Command: ollama pull granite3.3:8b
│
│ Reasoning (Reasoning):
│    qwen3:30b-a3b (30B)
│    Score: 91/100 | Pulls: 28,200,000
│    Quantization: Q6_K
│    Fine-tuning: No FT
│    Command: ollama pull qwen3:30b-a3b
│
│ Multimodal (Multimodal):
│    llava-llama3:8b (8B)
│    Score: 89/100 | Pulls: 2,200,000
│    Quantization: Q4_K_M
│    Fine-tuning: QLoRA
│    Command: ollama pull llava-llama3:8b
│
│ Creative (Creative):
│    granite4:7b-a1b-h (7B)
│    Score: 88/100 | Pulls: 1,200,000
│    Quantization: Q4_K_M
│    Fine-tuning: LoRA+QLoRA
│    Command: ollama pull granite4:7b-a1b-h
│
│ Talking (Chat):
│    granite4:7b-a1b-h (7B)
│    Score: 88/100 | Pulls: 1,200,000
│    Quantization: Q4_K_M
│    Fine-tuning: LoRA+QLoRA
│    Command: ollama pull granite4:7b-a1b-h
│
│ Reading (Reading):
│    qwen3:1.7b (1.7B)
│    Score: 83/100 | Pulls: 28,200,000
│    Quantization: Q8_0
│    Fine-tuning: LoRA+QLoRA
│    Command: ollama pull qwen3:1.7b
│
│ General (General):
│    granite4:7b-a1b-h (7B)
│    Score: 90/100 | Pulls: 1,200,000
│    Quantization: Q4_K_M
│    Fine-tuning: LoRA+QLoRA
│    Command: ollama pull granite4:7b-a1b-h
│

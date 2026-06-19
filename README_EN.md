<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <img src="https://img.shields.io/badge/python-3.10+-green" alt="Python">
  <img src="https://img.shields.io/badge/version-v1.2-brightgreen" alt="Version">
  <img src="https://img.shields.io/badge/embedding-bge--m3_MTEB_63.2-blue" alt="Embedding">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs Welcome">
</p>

<h1 align="center">🧠 Hermes-MemVault</h1>
<p align="center"><strong>A purpose-built memory system for the Hermes Agent — grounded in cognitive neuroscience</strong></p>
<p align="center">
  <em>It forgets. It consolidates knowledge during sleep. It grows its own rules.</em>
</p>

---

## What Is This?

**Hermes-MemVault** is the memory subsystem for the Hermes Agent. It is not yet another RAG framework — it is a complete three-tier memory architecture, with every mechanism from the human forgetting curve to sleep consolidation engineered directly into code.

What sets it apart:
- 🧠 **Neuroscience-aligned** — every mechanism has a grounding in cognitive neuroscience (Ebbinghaus / Kahana / Buzsáki)
- 🔍 **Semantic retrieval** — bge-m3 (Ollama / 1024-dim / MTEB 63.2) replaces brute-force full-text injection
- 🌙 **Sleep Loop** — nightly clustering → abstract rule extraction → knowledge graph writes
- 📉 **66% token savings** — down from 35K/round to 12K/round

---

## Quick Start

```bash
# Install the hermes-memv pip package (standalone use)
pip install hermes-memv

# Or clone the full Hermes-integrated version
git clone https://github.com/SnowHaruna/Hermes-MemVault.git
```

```python
from hermes_memv import MemoryVault

vault = MemoryVault()
vault.remember("Fixed a concurrency bug today — root cause was the connection pool missing max_overflow")
results = vault.recall("bug")
```

> **Detailed docs:** [Experience Report v1.2](docs/memvault-experience-report-2026-06-13.md) — 738 lines of design rationale, iteration history, and real-world deployment notes

---

## Three-Tier Memory Architecture

```
L0  Working Memory
    ├── Brain region: Prefrontal Cortex (PFC)
    ├── Storage: Context window
    └── TTL: Current conversation

L1  Episodic Memory
    ├── Brain region: Hippocampus
    ├── Storage: MEMORY.md + bge-m3 vector index
    ├── TTL: Permanent (7-day weight half-life)
    └── Content: Concrete events, preferences, lessons learned

L2  Semantic Memory
    ├── Brain region: Neocortex
    ├── Storage: KG JSON (kg_nodes.json + kg_edges.json)
    ├── TTL: Permanent
    └── Content: Abstract rules, patterns, regularities
```

---

## Core Mechanisms

| Mechanism | Implementation | Neuroscientific Basis |
|-----------|---------------|----------------------|
| **Forgetting Curve** | `weight = e^(-days/7) + usage×0.05 + correction×0.3` | Ebbinghaus (1885) |
| **Sleep Loop** | Nightly clustering → DeepSeek abstraction → KG writes | Buzsáki SWR (1989) |
| **Emotion Tagging** | Keyword-based automatic importance scoring | Amygdala |
| **Pattern Separation** | Similar-item retrieval weight reduced by 60% | Dentate Gyrus (DG) |
| **Three-Path Retrieval** | Dense + Sparse + ColBERT → RRF fusion | — |
| **Adversarial Rejection** | Irrelevant queries return empty results ("knows what it doesn't know") | — |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Embedding model | bge-m3 (Ollama / 1024-dim / MTEB 63.2) |
| Standalone storage | SQLite + WAL + FTS5 + connection pool |
| Integrated storage | MEMORY.md + LlamaIndex vector index |
| Knowledge graph | JSON files (kg_nodes.json + kg_edges.json) |
| Sleep Loop | Cron job (nightly 2:00–3:00) + DeepSeek v4-pro |
| Dependencies | Ollama (embeddings) / DeepSeek (abstraction) / zero external SaaS |

---

## Relationship to Related Projects

| Project | Relationship |
|---------|-------------|
| [memvault](https://github.com/SnowHaruna/memvault) | Upstream standalone pip package (original by @GwynCat), 127 tests, SQLite+FTS5 |
| [hermes-tentacles](https://github.com/SnowHaruna/hermes-tentacles) | Background task engine; Sleep Loop triggers through it |
| Hermes Agent | Host system; MemVault plugs in as the memory subsystem |

---

## Quick Health Checks

```bash
# Is the embedding model online?
curl -s http://127.0.0.1:11434/api/tags | grep bge-m3

# Index size & memory count
du -sh ~/.hermes/memory_index/
grep -c "§" ~/.hermes/memories/MEMORY.md

# Weight statistics
python3 -c "import json; d=json.load(open('$HOME/.hermes/memory_meta.json')); print(len(d),'entries')"
```

---

## License

MIT — see [LICENSE](LICENSE).

---

<p align="center">
  <em>"Knowing what to forget is harder than knowing what to remember."</em>
</p>

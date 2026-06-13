<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <img src="https://img.shields.io/badge/python-3.10+-green" alt="Python">
  <img src="https://img.shields.io/badge/版本-v1.2-brightgreen" alt="Version">
  <img src="https://img.shields.io/badge/嵌入-qwen3--embedding:8b_MTEB_70.58-orange" alt="Embedding">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs Welcome">
</p>

<h1 align="center">🧠 Hermes-MemVault</h1>
<p align="center"><strong>Hermes Agent 定制版 AI 记忆系统 —— 以认知神经科学为理论底座</strong></p>
<p align="center">
  <em>它会遗忘。会在睡眠中巩固知识。会自己长出新规则。</em>
</p>

---

## 这是什么

**Hermes-MemVault** 是 Hermes Agent 的记忆子系统。它不是另一个 RAG 框架——它是一个完整的三层记忆架构，从人脑的遗忘曲线到睡眠巩固，全部落地为工程代码。

核心差异化：
- 🧠 **脑科学对齐** —— 每个机制都有认知神经科学依据（Ebbinghaus / Kahana / Buzsáki）
- 🔍 **语义检索** —— qwen3-embedding:8b（MTEB 70.58 全球第一）替代全文硬灌
- 🌙 **Sleep Loop** —— 每夜自动聚类记忆、提炼抽象规则、写入知识图谱
- 📉 **Token 省 66%** —— 从 35K/轮 降到 12K/轮

---

## 快速开始

```bash
# 安装 hermes-memv pip 包（独立使用）
pip install hermes-memv

# 或克隆 Hermes 集成版
git clone https://github.com/SnowHaruna/Hermes-MemVault.git
```

```python
from hermes_memv import MemoryVault

vault = MemoryVault()
vault.remember("今天修复了一个并发 bug，根因是连接池未设置 max_overflow")
results = vault.recall("bug")
```

> **详细文档：** [体验报告 v1.2](docs/memvault-experience-report-2026-06-12.md) — 738 行完整设计、迭代与实战记录

---

## 三层记忆架构

```
L0  工作记忆 (Working Memory)
    ├── 脑区: 前额叶皮层 (PFC)
    ├── 存储: Context window
    └── TTL: 当前对话

L1  情景记忆 (Episodic Memory)
    ├── 脑区: 海马体 (Hippocampus)
    ├── 存储: MEMORY.md + qwen3-embedding:8b 向量索引
    ├── TTL: 永久（7 天权重半衰）
    └── 内容: 具体事件、偏好、教训

L2  语义记忆 (Semantic Memory)
    ├── 脑区: 新皮层 (Neocortex)
    ├── 存储: KG JSON（kg_nodes.json + kg_edges.json）
    ├── TTL: 永久
    └── 内容: 抽象规则、模式、规律
```

---

## 核心机制

| 机制 | 实现 | 脑科学来源 |
|------|------|-----------|
| **遗忘曲线** | `weight = e^(-days/7) + usage×0.05 + correction×0.3` | Ebbinghaus (1885) |
| **Sleep Loop** | 每夜聚类 → DeepSeek 抽象 → KG 写入 | Buzsáki SWR (1989) |
| **情绪标引** | 关键词自动评分重要性 | Amygdala |
| **模式分离** | 相似条目检索降权 60% | DG 齿状回 |
| **三路检索** | Dense + Sparse + ColBERT → RRF 融合 | — |
| **对抗拒绝** | 无关查询返回空结果（「知不知」能力） | — |

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 嵌入模型 | qwen3-embedding:8b (Ollama / 2048维 / MTEB 70.58) |
| 独立包存储 | SQLite + WAL + FTS5 + 连接池 |
| 集成版存储 | MEMORY.md + LlamaIndex 向量索引 |
| 知识图谱 | JSON 文件（kg_nodes.json + kg_edges.json） |
| Sleep Loop | Cron job（每夜 2:00-3:00）+ DeepSeek v4-pro |
| 依赖 | Ollama（嵌入）/ DeepSeek（抽象） / 零外部 SaaS |

---

## 与相关项目的关系

| 项目 | 关系 |
|------|------|
| [memvault](https://github.com/SnowHaruna/memvault) | 上游独立 pip 包（原作者 @GwynCat），127 测试，SQLite+FTS5 |
| [hermes-tentacles](https://github.com/SnowHaruna/hermes-tentacles) | 触手后台任务引擎，Sleep Loop 通过它触发 |
| Hermes Agent | 宿主，MemVault 作为记忆子系统集成 |

---

## 快速状态检查

```bash
# 嵌入模型在线？
curl -s http://127.0.0.1:11434/api/tags | grep qwen3-embedding

# 索引大小 & 记忆条数
du -sh ~/.hermes/memory_index/
grep -c "§" ~/.hermes/memories/MEMORY.md

# 权重统计
python3 -c "import json; d=json.load(open('$HOME/.hermes/memory_meta.json')); print(len(d),'entries')"
```

---

## 许可证

MIT — 详见 [LICENSE](LICENSE)。

---

<p align="center">
  <em>「知道什么该忘，比知道什么该存更难。」</em>
</p>

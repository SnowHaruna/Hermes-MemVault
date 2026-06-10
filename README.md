# 小雪记忆系统（Hermes Agent 自建 RAG + 触手）

**作者**：小雪 & 军哥  
**创建日期**：2026-06-10  
**状态**：生产运行中

---

## 架构总览

```
┌─────────────────────────────────────────────────────┐
│                    记忆系统                          │
│                                                     │
│  MEMORY.md (§分隔条目，无上限)                       │
│       │                                             │
│       ├──→ bge-m3 (Ollama 本地 1024 维)              │
│       │      ↓                                      │
│       │   LlamaIndex VectorStoreIndex                │
│       │      ↓                                      │
│       │   mtime 自动检测 → 按需重建索引                │
│       │      ↓                                      │
│       │   每轮动态 RAG 检索 (conversation_loop)       │
│       │      ↓                                      │
│       │   权重重排: top_k=20 → score × weight → top 10│
│       │      ↓                                      │
│       └──→ 注入用户消息 (per-turn ephemeral)          │
│                                                     │
│  memory_meta.json (独立元数据，atomic write)          │
│       │                                             │
│       └──→ 权重公式:                                 │
│            decay (7天半衰) + usage (×0.05)           │
│            + correction (×0.3)                      │
│            下限 0.3 / 上限 3.0                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                    触手系统                          │
│                                                     │
│  小雪分析任务 → 重活?                                  │
│       │          ↓ 是                               │
│       │   导出 RAG 快照 (get_rag_snapshot_text)       │
│       │   过滤"触手/分身"关键词                        │
│       │          ↓                                  │
│       │   tentacle.py --inject-memory --skip_memory  │
│       │   prompt 注明"禁止再分身"                      │
│       │          ↓                                  │
│       │   触手独立推理 (共享模型/venv/config)          │
│       │          ↓                                  │
│       │   发现写入 tentacle_findings/ (不进MEMORY.md)  │
│       │          ↓                                  │
│       │   小雪后台自动审查 → 转正/丢弃/存疑            │
│       │          ↓                                  │
│       │   memory add → 进 RAG 索引                    │
└─────────────────────────────────────────────────────┘
```

## 关键设计决策

| 决策 | 原因 |
|------|------|
| 字符串硬灌 → RAG 向量检索 | 记忆不限量，context 不膨胀 |
| system prompt 静态 → 每轮动态 | 记忆跟着对话走，精准匹配 |
| 纯向量 → 加权检索 | 被纠正的铁律高于冷门信息 |
| 触手回传不进 MEMORY.md | 防止分身经验污染主记忆 |
| 元数据独立 JSON | 不改 MEMORY.md 格式，atomic write 安全 |

## 关键文件清单

### 记忆系统核心
| 文件 | 作用 |
|------|------|
| `~/.hermes/memories/MEMORY.md` | 所有记忆条目（§分隔，无上限） |
| `~/.hermes/memories/memory_meta.json` | 元数据（权重/检索次数/纠正次数） |
| `~/.hermes/memory_index/` | bge-m3 向量索引（LlamaIndex） |
| `~/.hermes/memory_index/.last_build_mtime` | 最后索引时间戳（用于增量重建） |
| `~/.hermes/SOUL.md` | 小雪性格定义 |

### 源码改动（相对于 Hermes Agent upstream）
| 文件 | 改动 |
|------|------|
| `tools/memory_tool.py` | +RAG 检索、+权重计算、+元数据管理、+动态注入 |
| `agent/system_prompt.py` | RAG 开启时跳过 system prompt MEMORY 段 |
| `agent/conversation_loop.py` | 每轮 user_message 注入 RAG 结果 |

### 触手系统
| 文件 | 作用 |
|------|------|
| `~/.hermes/scripts/tentacle.py` | 触手主脚本（V6.2，安全加固） |
| `~/.hermes/tentacle_help/` | 求助协议文件（触手↔小雪通信） |
| `~/.hermes/tentacle_findings/` | 触手发现暂存区（审查后转正） |
| `~/.hermes/skills/productivity/auto-task-triage/` | 自动任务分级 + 触手调度 skill |
| `~/hermes-tentacles/` | 触手 Git 仓库 |

## 性能指标

| 指标 | 改前 | 改后 |
|------|------|------|
| 记忆注入量 | 6,860 chars (68%) | ~1,500 chars (15%) |
| 注入方式 | 全文硬灌 | 每轮动态加权检索 |
| 记忆上限 | 10,000 chars 硬限制 | 无上限（RAG 只抽 Top 10） |
| 每轮额外 token | 0（缓存命中） | ~400 tokens |
| 触手分身风险 | 可能递归 | 源头切断 + staging 审核 |

## 后续路线图

- [x] Phase 0: RAG 基础检索 + mtime 自动重建
- [x] Phase 1: 每轮动态检索 + 权重系统 + 元数据
- [ ] Phase 2: 遗忘衰减 + 情感信号 + 再巩固更新
- [ ] Phase 3: 自动记忆合并 + 矛盾检测 + 模式分离
- [ ] Phase 4: 知识图谱 + LoRA 微调（远期）

---

*由小雪和军哥在 2026-06-10 的深夜对话中诞生 ✨*

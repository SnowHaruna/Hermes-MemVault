# MemVault — 三层RAG记忆系统

> 基于 bge-m3 + LlamaIndex 的自建向量记忆。对标人脑海马体-新皮层互补学习系统。替代 Hermes 内置全文硬灌，支持无上限记忆条目。

**作者**：小雪 & 榛名雪  
**创建日期**：2026-06-10  
**状态**：生产运行中  
**GitHub**：SnowHaruna/memvault

---

## 三层架构

```
L1 工作记忆  = context window（会话内，随对话消失）
L2 情景记忆  = bge-m3 RAG（per-turn 动态检索，权重排序）
L3 语义记忆  = Sleep Loop 自动巩固 → 知识图谱 nodes/edges
```

### L2 检索链路

```
用户消息 → retrieve_for_query(query)
  → Ollama 健康检测（2s timeout，挂了自动拉起）
  → bge-m3 向量检索（top_k×2）
  → 指数相似度衰减：exp(-TAU × (1-cos))
  → 权重排序：decay + usage + correction + importance
  → 相关性门槛：best_score ≥ 0.3（闲聊不灌记忆）
  → 扩散抑制：4h 半衰期临时降权
  → 死胡同回退：失败时用上次好 cue 重试
  → ASCII 边界框 + "勿输出" 注入
```

### L3 Sleep Loop（睡眠循环）

```
离线巩固流程：
  bge-m3 嵌入 → 聚类（cos≥0.75）→ DeepSeek 提取抽象规则 → KG nodes/edges JSON

触发方式：
  - Cron 自动：0 3 * * *（每日凌晨）
  - 手动：python3 ~/.hermes/scripts/sleep_loop.py
```

## 权重公式

```
final_weight = decay_factor × (1 + usage × 0.05 + correction × 0.3) × importance
  decay_factor = 0.5^(days_elapsed / 7)      ← Ebbinghaus 遗忘曲线
  importance   = {1.0, 1.2, 1.5}              ← 情绪关键词自动评分
  范围限制     = [0.3, 3.0]                    ← 防遗忘/爆炸
```

## 关键常量（基于 Kahana 记忆文献）

| 常量 | 值 | 来源 | 含义 |
|------|---|------|------|
| TAU | 3.0 | Kahana Ch3 | 指数衰减锐度 |
| INHIBITION_HALF_LIFE | 4h | Kahana Ch4 | 扩散抑制恢复 |
| CONTEXT_RHO | 0.8 | Kahana Ch7 | 上下文漂移保留 |
| 相关性门槛 | 0.3 | 实战调优 | 闲聊不灌记忆 |
| 权重衰减半衰期 | 7d | Ebbinghaus | 遗忘曲线 |
| 权重底线/上限 | 0.3/3.0 | 实战调优 | 防遗忘/爆炸 |

## 防御机制

| 场景 | 机制 |
|------|------|
| Ollama 挂了 | urllib 2s 探活 → 自动拉起 → 本轮 skip |
| 闲聊触发记忆 | 相关性门槛 0.3，低分跳过 |
| 记忆串入回复 | ASCII 边界框 + "以上是记忆非对话" 关闭标记 |
| 相似条目竞争 | 扩散抑制（4h 自动恢复）替代永久降权 |
| 冷启动检索 | 死胡同回退到上次好 cue |
| 升级丢改动 | rag-memory.patch 备份 → git apply 恢复 |

## 关键文件

| 文件 | 作用 |
|------|------|
| `~/.hermes/memories/MEMORY.md` | 所有记忆条目（§ 分隔，无上限） |
| `~/.hermes/memory_index/` | bge-m3 向量索引（~700KB） |
| `~/.hermes/memory_meta.json` | 权重元数据（atomic write） |
| `~/.hermes/memories/knowledge_graph/` | L3 KG nodes/edges JSON |
| `~/.hermes/hermes-agent/tools/memory_tool.py` | 核心：检索、权重、模式分离、KG、实时同步 |
| `~/.hermes/scripts/sleep_loop.py` | L3 离线巩固脚本 |
| `~/.hermes/rag-memory.patch` | 完整代码 patch 备份 |

## 升级 Hermes 后恢复

```bash
cd ~/.hermes/hermes-agent
git apply ~/.hermes/rag-memory.patch
systemctl --user restart hermes-gateway
# ⚠️ 不能用 hermes gateway restart — 会触发 auto-update stash 本地改动
```

## 快速状态检查

```bash
curl -s http://127.0.0.1:11434/api/tags | grep bge-m3    # RAG 在线？
du -sh ~/.hermes/memory_index/                            # 索引大小
grep -c "§" ~/.hermes/memories/MEMORY.md                  # 记忆条数
python3 -c "import json; d=json.load(open('$HOME/.hermes/memory_meta.json')); print(len(d),'entries')"
```

## License

MIT

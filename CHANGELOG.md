# Changelog

## v1.2 (2026-06-13)

### 新增
- 串线阈值实验（§10.3）：发现轻追问密度梯度（0%→15%→30%）
- MemVault v0.1 独立包记入（§11.2）：SQLite + FTS5 + 127 测试
- GitHub 仓库改名：SnowHaruna/Hermes-MemVault
- 公开身份统一：榛名雪（替换全部"军哥"引用）
- README.md 项目级重写（badges / install / quickstart）
- LICENSE / CHANGELOG / .gitignore 补齐

### 变更
- 嵌入模型：bge-m3 (1024维 MTEB 63.2) → qwen3-embedding:8b (2048维 MTEB 70.58)
- 体验报告日期更新至 06-13
- 附录 B 技术栈追加存储行

---

## v1.1 (2026-06-12)

### 新增
- Section 0「缘起」：state.db Session 串线根因分析
- 最终根因修复：memvault-restore.sh 自动结束旧 Session
- 首次论文研究：AI 记忆 2026 综述（触手）
- 第二次论文研究：Kahana 脑科学引入

### 变更
- RAG 替代全文灌入：bge-m3 + LlamaIndex → prompt 省 77%
- .hermes.md 挡住 AGENTS.md：省 ~17K token（40%）
- 权重公式理论化：Kahana Ch2-7 映射

---

## v1.0 (2026-06-11)

### 首次交付
- L0/L1/L2 三层记忆架构
- RAG 语义检索（Top-10 注入）
- 情绪自动标引
- 模式分离门控（相似条目降权 60%）
- KG 桥接（L1→L2）
- Sleep Loop 离线巩固（Cron 每夜 2:00）
- Phase 4 RDC（检索驱动上下文衰减）
- 边界框指令（防记忆串入回复）
- Ollama 容灾（自动探测 + 拉起 + 降级）
- 实时索引同步

### 清理
- ECC 系统全删
- Mem0 关闭
- MemPalace MCP 禁用
- 低频 skill 裁短
- memory_char_limit 10000 → 100000

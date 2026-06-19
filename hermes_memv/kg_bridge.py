"""
KG（知识图谱）桥接模块 — 从 L1 情景记忆抽象 L2 语义规则。

与 Hermes KG 系统双向桥接：
  1. Sleep Loop 产出规则 → 写入 Hermes KG
  2. 检索时附带 KG 规则 → 增强上下文理解
"""

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# KG 存储路径（与 Hermes 共享）
KG_INDEX_PATH = os.path.expanduser("~/.hermes/memory_index/graph_store.json")


@dataclass
class KGRule:
    """知识图谱中的一条语义规则。"""
    rule: str
    source_cluster: str  # 来源记忆簇 ID
    confidence: float = 1.0
    contradictions: List[str] = field(default_factory=list)


class KGBridge:
    """KG 桥接器 — 情景记忆 → 语义规则的升降通道。

    用法:
        bridge = KGBridge()
        bridge.add_rule("串线源于L0上下文溢出", cluster_id="sleep_loop_20260613")
        rules = bridge.query("串线")
        # -> [KGRule(...)]
    """

    def __init__(self, path: str = KG_INDEX_PATH):
        self._path = path
        self._rules: Dict[str, KGRule] = {}
        self._load()

    def _load(self):
        """从磁盘加载 KG。"""
        if os.path.exists(self._path):
            try:
                with open(self._path) as f:
                    data = json.load(f)
                for rule_id, rule_data in data.items():
                    self._rules[rule_id] = KGRule(**rule_data)
                logger.info(f"KG loaded: {len(self._rules)} rules")
            except Exception as e:
                logger.warning(f"KG load failed: {e}, starting fresh")

    def _save(self):
        """保存 KG 到磁盘。"""
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        data = {rid: {"rule": r.rule, "source_cluster": r.source_cluster,
                      "confidence": r.confidence, "contradictions": r.contradictions}
                for rid, r in self._rules.items()}
        with open(self._path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_rule(self, rule: str, cluster_id: str = "",
                 confidence: float = 1.0) -> str:
        """添加一条语义规则。返回 rule_id。"""
        import hashlib
        rule_id = hashlib.md5(rule.encode()).hexdigest()[:12]
        if rule_id in self._rules:
            self._rules[rule_id].confidence = max(
                self._rules[rule_id].confidence, confidence
            )
        else:
            self._rules[rule_id] = KGRule(
                rule=rule,
                source_cluster=cluster_id,
                confidence=confidence,
            )
        self._save()
        return rule_id

    def add_contradiction(self, rule_id: str, contradiction: str):
        """标记一条规则存在矛盾。"""
        if rule_id in self._rules:
            self._rules[rule_id].contradictions.append(contradiction)
            self._rules[rule_id].confidence *= 0.8
            self._save()

    def query(self, keyword: str) -> List[KGRule]:
        """关键词查询 KG 规则。"""
        keyword_lower = keyword.lower()
        return [r for r in self._rules.values()
                if keyword_lower in r.rule.lower()]

    def context_for_query(self, query: str) -> str:
        """为检索查询生成 KG 增强上下文。

        返回格式化的规则文本，可直接注入 LLM prompt。
        """
        rules = self.query(query)
        if not rules:
            return ""
        lines = ["🧠 KG:"]
        for r in rules[:3]:
            conf = f"({r.confidence:.0%})" if r.confidence < 1.0 else ""
            lines.append(f"  {r.rule} {conf}")
            if r.contradictions:
                lines.append(f"    ⚠️ 矛盾: {', '.join(r.contradictions[:2])}")
        return "\n".join(lines)

    @property
    def rule_count(self) -> int:
        return len(self._rules)

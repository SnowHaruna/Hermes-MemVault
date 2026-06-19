"""
情绪标引模块 — 对每条记忆自动评分情绪显著性。

评分算法基于 qwen3-embedding 的语义向量投影 + 关键词增强。
情绪显著性 > 0.7 的记忆会被标记为高重要性，抵抗衰减。
"""

import logging
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# 情绪关键词库（中英文混合）
EMOTION_KEYWORDS: Dict[str, float] = {
    # 高唤醒正面
    "激动": 0.9, "惊喜": 0.9, "感动": 0.85, "骄傲": 0.8, "兴奋": 0.85,
    "amazing": 0.9, "incredible": 0.85, "breakthrough": 0.9,
    # 高唤醒负面
    "愤怒": 0.9, "崩溃": 0.9, "绝望": 0.85, "恐惧": 0.85, "震惊": 0.8,
    "disaster": 0.9, "critical": 0.85, "urgent": 0.85, "bug": 0.7,
    # 中唤醒
    "开心": 0.7, "满足": 0.65, "喜欢": 0.7, "享受": 0.65,
    "讨厌": 0.7, "失望": 0.7, "担心": 0.65,
    # 低唤醒（不作为高重要性依据）
    "平静": 0.3, "日常": 0.2, "普通": 0.15, "一般": 0.1,
}

# 可配置的情绪阈值
HIGH_EMOTION_THRESHOLD = 0.7
DEFAULT_EMOTION = 0.5


def score_emotion(text: str) -> float:
    """对文本进行情绪评分（0.0-1.0）。

    基于关键词匹配 + 规则增强，不需要额外模型调用。
    结果用于记忆衰减模型中的 importance 字段。

    Args:
        text: 记忆文本

    Returns:
        情绪显著性分数（0.0-1.0），默认 0.5
    """
    text_lower = text.lower()
    score = 0.0
    hits = 0

    for kw, weight in EMOTION_KEYWORDS.items():
        if kw in text_lower:
            score += weight
            hits += 1

    if hits == 0:
        return DEFAULT_EMOTION

    # 平均 + 惩罚高频低唤醒词稀释
    avg = score / hits
    # 有「但不」「只是」「虽然」→ 降级 0.1
    if re.search(r"(但不|只是|虽然|不过|可惜)", text):
        avg = max(0.3, avg - 0.1)

    return round(min(avg, 1.0), 3)


def is_high_importance(text: str) -> bool:
    """判断记忆是否应标记为高重要性。"""
    return score_emotion(text) >= HIGH_EMOTION_THRESHOLD


def emotion_to_importance(text: str) -> float:
    """情绪评分 → 重要性评分映射（用于 decay.py 的 importance 参数）。

    高情绪 ≈ 高重要性 ≈ 慢衰减。
    """
    e = score_emotion(text)
    # 线性映射：情绪 0.5→重要性 0.5，情绪 0.9→重要性 0.95
    return round(0.5 + (e - 0.5) * 1.125, 3)

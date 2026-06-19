"""
qwen3-embedding:8b 适配器 — 实现 AbstractEmbedder 接口。

MTEB 70.58 (全球第一, 2026-06), 2048维, 32K上下文。
通过 Ollama 调用，代理已配（7890）。

相比朋友版 bge-m3 (MTEB 63.2, 1024维)：
  - 语义理解强 7.4 分
  - 支持指令微调（task-specific instructions）
  - 维度翻倍但检索几乎没有额外开销（Ollama一次性返回）
"""

import logging
import subprocess
from typing import List

from hermes_memv.embedding.base import AbstractEmbedder

logger = logging.getLogger(__name__)


class QwenEmbedder(AbstractEmbedder):
    """qwen3-embedding:8b 嵌入服务（Ollama）。

    用法:
        embedder = QwenEmbedder(model="qwen3-embedding:8b")
        vectors = embedder.embed(["Python bug", "数据库连接池"])
        # -> [[0.023, -0.417, ...], [0.891, 0.156, ...]]  # 2048维
    """

    def __init__(self, model: str = "qwen3-embedding:8b"):
        self._model = model
        self._dim = 2048
        self._available: bool | None = None

    @property
    def dim(self) -> int:
        return self._dim

    def is_available(self) -> bool:
        """检查 Ollama 中 qwen3-embedding 是否就绪。"""
        if self._available is not None:
            return self._available
        try:
            r = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=10
            )
            self._available = self._model in r.stdout
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            self._available = False
        return self._available

    def check_health(self) -> bool:
        """AbstractEmbedder 接口：健康检测。"""
        return self.is_available()

    def embed_query(self, query: str) -> List[float]:
        """单条查询嵌入。"""
        return self.embed([query])[0]

    def embed(self, texts: List[str], instruction: str = "") -> List[List[float]]:
        """调用 Ollama API 生成嵌入向量。

        Args:
            texts: 待嵌入文本列表
            instruction: 可选的指令前缀（qwen3-embedding 支持）

        Returns:
            嵌入向量列表，每个 2048 维
        """
        import json
        import urllib.request

        vectors = []
        for text in texts:
            payload = {
                "model": self._model,
                "prompt": text,
            }
            if instruction:
                payload["options"] = {"instruction": instruction}

            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/embeddings",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            try:
                resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
                vectors.append(resp["embedding"])
            except Exception as e:
                logger.error(f"Embedding failed for text[:50]={text[:50]!r}: {e}")
                raise

        return vectors

    def embed_batch(self, texts: List[str], instruction: str = "") -> List[List[float]]:
        """批量嵌入（当前逐条调用Ollama，后续可优化为批量API）。"""
        return self.embed(texts, instruction)

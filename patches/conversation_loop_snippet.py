# conversation_loop.py — RAG per-turn injection snippet
# 位置: agent/conversation_loop.py, line ~617
# 在 user message 准备注入时，添加 RAG 检索结果

if idx == current_turn_user_idx and msg.get("role") == "user":
    _injections = []
    # Built-in RAG: per-turn memory retrieval from vector index
    if agent._memory_store and agent._memory_enabled:
        try:
            _rag_text = agent._memory_store.retrieve_for_query(
                original_user_message or msg.get("content", "")
            )
            if _rag_text:
                _injections.append(_rag_text)
        except Exception:
            pass  # RAG is best-effort, never block the turn

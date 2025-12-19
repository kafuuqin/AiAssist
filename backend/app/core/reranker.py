from typing import List, Tuple
from sentence_transformers import CrossEncoder

class Reranker:
    """重排序器"""

    def __init__(self, model_name: str):
        self.model = CrossEncoder(model_name)

    def rerank(self,
               query: str,
               documents: List[str],
               top_k: int = 3) -> List[str]:
        """重排序文档"""
        if not documents:
            return []

        # 准备查询-文档对
        pairs = [(query, doc) for doc in documents]

        # 预测相关性分数
        scores = self.model.predict(pairs)

        # 按分数排序
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # 返回top_k个文档
        return [doc for doc, _ in scored_docs[:top_k]]

    def rerank_with_scores(self,
                           query: str,
                           documents: List[str]) -> List[Tuple[str, float]]:
        """返回带分数的重排序结果"""
        if not documents:
            return []

        pairs = [(query, doc) for doc in documents]
        scores = self.model.predict(pairs)

        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        return scored_docs
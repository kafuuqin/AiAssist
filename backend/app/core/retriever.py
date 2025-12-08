from typing import List, Tuple, Dict, Any
import numpy as np
from .embedding import EmbeddingManager

class Retriever:
    """检索器"""

    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager

    def retrieve(self,
                 query: str,
                 top_k: int = 5,
                 include_metadata: bool = False) -> List[Any]:
        """检索相关文档"""
        if not self.embedding_manager.collection:
            raise ValueError("向量数据库未初始化")

        # 生成查询嵌入
        query_embedding = self.embedding_manager.embed_text(query)

        # 执行查询
        results = self.embedding_manager.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        if include_metadata:
            return list(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ))
        else:
            return results['documents'][0]

    def similarity_search(self,
                          query: str,
                          top_k: int = 5,
                          threshold: float = 0.5) -> List[Tuple[str, float]]:
        """带相似度分数的检索"""
        results = self.retrieve(query, top_k, include_metadata=True)

        # 转换距离为相似度（余弦相似度）
        retrieved = []
        for doc, metadata, distance in results:
            similarity = 1 - distance  # ChromaDB返回的是距离
            if similarity >= threshold:
                retrieved.append((doc, similarity))

        retrieved.sort(key=lambda x: x[1], reverse=True)
        return retrieved
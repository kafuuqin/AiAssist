from typing import List, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
import chromadb
from chromadb.config import Settings

class EmbeddingManager:
    """嵌入管理器"""

    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)
        self.client = None
        self.collection = None

    def embed_text(self, text: str, normalize: bool = True) -> List[float]:
        """生成文本嵌入"""
        embedding = self.model.encode(text, normalize_embeddings=normalize)
        return embedding.tolist()

    def embed_batch(self, texts: List[str], normalize: bool = True) -> List[List[float]]:
        """批量生成嵌入"""
        embeddings = self.model.encode(texts, normalize_embeddings=normalize)
        return embeddings.tolist()

    def init_vector_db(self,
                       collection_name: str = "documents",
                       persist_directory: Optional[str] = None):
        """初始化向量数据库"""
        if persist_directory:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
        else:
            self.client = chromadb.EphemeralClient()

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_to_vector_db(self,
                         texts: List[str],
                         embeddings: List[List[float]],
                         metadatas: Optional[List[dict]] = None):
        """添加数据到向量数据库"""
        if not self.collection:
            self.init_vector_db()

        ids = [str(i) for i in range(len(texts))]

        if metadatas is None:
            metadatas = [{"text": text} for text in texts]

        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
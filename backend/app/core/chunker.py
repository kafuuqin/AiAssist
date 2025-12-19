from typing import List
import re

class DocumentChunker:
    """文档分块器"""

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_by_paragraph(self, content: str) -> List[str]:
        """按段落分块"""
        paragraphs = content.split("\n\n")
        return [p.strip() for p in paragraphs if p.strip()]

    def split_by_sentence(self, content: str) -> List[str]:
        """按句子分块"""
        sentences = re.split(r'[。！？!?]', content)
        return [s.strip() for s in sentences if s.strip()]

    def split_fixed_size(self, content: str) -> List[str]:
        """固定大小分块"""
        chunks = []
        start = 0

        while start < len(content):
            end = start + self.chunk_size
            chunk = content[start:end]

            if len(content) > end:
                # 找最近的句末作为分界点
                last_period = max(chunk.rfind('。'), chunk.rfind('.'),
                                  chunk.rfind('！'), chunk.rfind('!'),
                                  chunk.rfind('？'), chunk.rfind('?'))
                if last_period != -1:
                    end = start + last_period + 1
                    chunk = content[start:end]

            chunks.append(chunk.strip())
            start = end - self.overlap

        return [c for c in chunks if c]

    def split_document(self, file_path: str, strategy: str = "paragraph") -> List[str]:
        """分块主方法"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if strategy == "paragraph":
            return self.split_by_paragraph(content)
        elif strategy == "sentence":
            return self.split_by_sentence(content)
        elif strategy == "fixed":
            return self.split_fixed_size(content)
        else:
            raise ValueError(f"未知的分块策略: {strategy}")
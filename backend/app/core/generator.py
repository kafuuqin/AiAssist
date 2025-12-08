import json
import time
from typing import List, Dict, Any
import requests
from app.config import Config

class ZhipuAIClient:
    """智谱AI客户端"""

    def __init__(self, api_key: str = None, base_url: str = None):
        self.config = Config()
        self.api_key = api_key or self.config.ZHIPU_API_KEY
        self.base_url = base_url or self.config.ZHIPU_BASE_URL
        self.chat_url = f"{self.base_url}/chat/completions"

    def generate(self,
                 query: str,
                 contexts: List[str] = None,
                 history: List[Dict] = None,
                 model: str = None,
                 max_retries: int = None,
                 **kwargs) -> str:
        """生成回答（带重试机制）"""
        max_retries = max_retries or self.config.MAX_RETRIES
        retry_delay = self.config.INITIAL_RETRY_DELAY

        for attempt in range(max_retries):
            try:
                return self._single_generate(query, contexts, history, model, **kwargs)
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"第{attempt + 1}次尝试失败，{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise Exception(f"多次尝试后失败: {str(e)}")
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"第{attempt + 1}次尝试失败，{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise

    def _single_generate(self,
                         query: str,
                         contexts: List[str] = None,
                         history: List[Dict] = None,
                         model: str = None,
                         **kwargs) -> str:
        """单次生成"""
        model = model or self.config.LLM_MODEL

        # 构建消息列表
        messages = []

        # 添加系统提示
        if contexts:
            # 文档检索模式
            system_prompt = """你是一位专业的知识助手，专门回答基于提供文档的问题。
你的回答必须严格基于用户提供的文档片段，不能添加任何文档外的信息。
如果文档中没有相关信息，请明确说明无法回答。"""
        else:
            # 普通对话模式
            system_prompt = """你是一位友好的AI助手，可以进行普通的对话交流。
请注意：用户正在进行普通对话，没有提供任何文档。
请基于你的知识进行回答，不要提及任何文档相关内容。"""

        messages.append({"role": "system", "content": system_prompt})

        # 添加历史对话
        if history:
            # 过滤掉系统消息
            filtered_history = [msg for msg in history if msg.get("role") != "system"]
            messages.extend(filtered_history)

        # 添加当前查询
        if contexts:
            # 文档检索模式 - 构建包含上下文的查询
            context_text = "\n\n".join([
                f"【相关片段 {i+1}】\n{context}"
                for i, context in enumerate(contexts)
            ])

            final_query = f"""请基于以下文档片段回答用户问题：

{context_text}

用户问题：{query}

请记住：
1. 只使用提供的片段信息
2. 不要添加片段外的任何信息
3. 如果片段不相关，请说明无法基于文档回答

回答："""
        else:
            # 普通对话模式
            final_query = f"""用户问题：{query}

请作为普通AI助手回答，不要提及任何文档。"""

        messages.append({"role": "user", "content": final_query})

        # 合并配置参数
        params = self.config.LLM_PARAMS.copy()
        params.update(kwargs)

        payload = {
            "model": model,
            "messages": messages,
            **params
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.post(
            self.chat_url,
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False),
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API错误 {response.status_code}: {response.text}")
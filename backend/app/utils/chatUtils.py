import os
import sys
import re
from typing import List, Dict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import Config
from app.core.chunker import DocumentChunker
from app.core.embedding import EmbeddingManager
from app.core.retriever import Retriever
from app.core.reranker import Reranker
from app.core.generator import ZhipuAIClient

class ConversationManager:
    """对话管理器"""

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history = []

    def add_message(self, role: str, content: str):
        """添加消息到历史"""
        self.history.append({
            "role": role,
            "content": content
        })

        # 限制历史长度
        if len(self.history) > self.max_history * 2:  # *2因为包含user和assistant
            self.history = self.history[-self.max_history*2:]

    def get_history(self) -> List[Dict]:
        """获取历史对话"""
        return self.history.copy()

    def clear_history(self):
        """清空历史对话"""
        self.history = []

    def get_recent_context(self, num_exchanges: int = 3) -> str:
        """获取最近的对话上下文"""
        recent = self.history[-num_exchanges*2:] if num_exchanges*2 <= len(self.history) else self.history
        context_lines = []
        for msg in recent:
            speaker = "用户" if msg["role"] == "user" else "助手"
            context_lines.append(f"{speaker}: {msg['content']}")
        return "\n".join(context_lines)

class RAGSystem:
    """RAG系统主类"""

    def __init__(self):
        self.config = Config()

        # 初始化组件
        self.chunker = DocumentChunker()
        self.embedding_manager = EmbeddingManager(self.config.EMBEDDING_MODEL)
        self.retriever = Retriever(self.embedding_manager)
        self.reranker = Reranker(self.config.RERANKER_MODEL)
        self.generator = ZhipuAIClient()
        self.conversation = ConversationManager()

        # 定义需要检索的关键词模式
        self.doc_keywords = [
            # 人物相关
            "大雄", "静香", "胖虎", "人物", "角色", "主人公", "主角",

            # 时间和年龄
            "12岁", "童年", "小学", "时期", "阶段", "时间", "年份", "年龄",
            "三年", "五年", "两年", "战后", "晚年", "大学",

            # 地点和事件
            "战争", "避难", "乡下", "城市", "重建", "家园", "房屋", "学校",
            "社区", "图书馆", "夜校", "教室", "建筑", "规划",

            # 学习和知识
            "学习", "建筑", "知识", "考试", "100分", "成绩", "课程", "书籍",
            "抗震", "结构", "工程", "设计", "原理", "规划", "理论",
            "图书馆", "查阅", "自学", "报名", "参加", "土木", "专业",

            # 职业和成就
            "建筑师", "教授", "注册", "资格", "成就", "获奖", "奖项", "设计奖",
            "成就", "贡献", "工作", "职业", "生涯", "事业", "项目",

            # 具体行为和动作
            "帮助", "设计", "建造", "修复", "建议", "保留", "规划", "参与",
            "主导", "撰写", "编写", "创作", "教学", "传授", "培养",

            # 情感和动机
            "使命感", "责任感", "影响", "改变", "决定", "决心", "信念", "理念",
            "价值观", "反思", "感受", "体验", "经历", "故事",

            # 文档结构
            "总结", "概括", "概述", "内容", "故事", "情节", "发展",
            "什么", "哪些", "怎样", "如何", "为什么", "哪里", "何时",

            # 建筑相关
            "抗震", "安全", "可持续", "环保", "材料", "能源", "标准",
            "学校", "医院", "社区中心", "公共建筑", "房屋", "住宅",

            # 社会价值
            "社会", "责任", "帮助", "服务", "安全", "舒适", "人性化",
            "弱势群体", "环境", "保护", "可持续", "发展",
        ]

        # 定义通用对话关键词（不需要检索）
        self.general_keywords = [
            # 问候和礼貌
            "你好", "您好", "hi", "hello", "hey", "哈喽",
            "早上好", "中午好", "下午好", "晚上好", "晚安",
            "再见", "拜拜", "再会", "下次见", "告辞",
            "谢谢", "感谢", "多谢", "不客气", "没关系",
            "抱歉", "对不起", "不好意思", "请原谅",

            # 自我介绍
            "你叫什么", "你是谁", "你的名字", "介绍自己",
            "你能做什么", "你有什么功能", "你会什么",
            "你是什么", "你由谁", "你是什么AI",

            # 闲聊
            "今天天气", "现在几点", "今天日期",
            "心情", "感觉", "情绪", "状态",
            "哈哈", "呵呵", "嘿嘿", "嘻嘻", "笑",
            "ok", "好的", "可以", "行", "没问题",

            # 帮助和命令
            "帮助", "help", "怎么用", "如何使用",
            "清空", "重置", "重新开始", "新对话",
            "历史", "记录", "刚才", "之前",

            # 通用问题（不涉及文档）
            "你好吗", "你怎么样", "最近好吗",
            "吃饭", "睡觉", "休息", "工作", "学习",
            "建议", "推荐", "想法", "意见","叫什么"
        ]

        # 状态标志
        self.is_initialized = False
        self.chunks = []

    def initialize(self, doc_path: str = None, chunk_strategy: str = "paragraph"):
        """初始化系统"""
        print("正在初始化RAG系统...")

        # 加载和分块文档
        doc_path = doc_path or self.config.DOC_FILE
        if not os.path.exists(doc_path):
            raise FileNotFoundError(f"文档文件不存在: {doc_path}")

        print(f"加载文档: {doc_path}")
        self.chunks = self.chunker.split_document(doc_path, chunk_strategy)
        print(f"文档分块完成，共 {len(self.chunks)} 个片段")

        # 生成嵌入
        print("正在生成嵌入向量...")
        embeddings = self.embedding_manager.embed_batch(self.chunks)

        # 初始化向量数据库
        print("正在初始化向量数据库...")
        self.embedding_manager.init_vector_db()

        # 添加数据到向量数据库
        print("正在存储到向量数据库...")
        self.embedding_manager.add_to_vector_db(self.chunks, embeddings)

        self.is_initialized = True
        print("RAG系统初始化完成！")

    def needs_retrieval(self, query: str, history: List[Dict]) -> bool:
        """判断是否需要检索文档"""
        query_lower = query.lower()

        # 1. 先检查是否明确为通用对话
        for keyword in self.general_keywords:
            if keyword in query_lower:
                if self.config.VERBOSE:
                    print(f"检测到通用关键词: {keyword}")
                return False

        # 2. 检查是否包含文档相关关键词
        doc_keyword_found = False
        for keyword in self.doc_keywords:
            if keyword in query:
                doc_keyword_found = True
                if self.config.VERBOSE:
                    print(f"检测到文档关键词: {keyword}")
                break

        if not doc_keyword_found:
            # 如果没有文档关键词，大概率是通用对话
            return False

        # 3. 检查历史上下文
        recent_context = ""
        if history:
            recent_messages = history[-4:]  # 看最近2轮对话
            for msg in recent_messages:
                recent_context += msg["content"] + " "

        # 如果历史中有明确的文档讨论，即使当前查询不明确，也可能需要检索
        history_has_doc_content = any(
            keyword in recent_context.lower()
            for keyword in ["文档", "文章", "内容", "总结", "提到"]
        )

        # 4. 检查是否为特殊疑问句（更可能需要检索）
        is_special_question = any(
            query.startswith(q_word)
            for q_word in ["什么", "哪些", "怎样", "如何", "为什么", "哪里", "何时", "谁"]
        )

        # 5. 检查是否为指令式查询
        is_command = any(
            query.startswith(cmd)
            for cmd in ["总结", "概括", "分析", "解释", "描述", "说明"]
        )

        # 最终判断逻辑
        if is_command or (doc_keyword_found and is_special_question):
            return True
        elif doc_keyword_found and history_has_doc_content:
            return True
        else:
            # 默认不检索，避免误判
            return True

    def query(self, query: str, verbose: bool = False) -> str:
        """查询接口"""
        if not self.is_initialized:
            raise RuntimeError("系统未初始化，请先调用 initialize() 方法")

        # 添加用户消息到历史
        self.conversation.add_message("user", query)

        if verbose:
            print(f"\n{'='*50}")
            print(f"查询: {query}")
            print('-'*50)

        # 判断是否需要检索
        history = self.conversation.get_history()[:-1]  # 不包含当前问题

        needs_retrieval = self.needs_retrieval(query, history)

        if verbose:
            print(f"判断结果: {'需要检索文档' if needs_retrieval else '普通对话，不需要检索'}")

        if needs_retrieval:
            try:
                # 1. 检索
                retrieved = self.retriever.retrieve(
                    query,
                    top_k=self.config.RETRIEVAL_TOP_K
                )

                if verbose:
                    print(f"检索到 {len(retrieved)} 个相关片段")
                    for i, doc in enumerate(retrieved):
                        print(f"[{i}] {doc[:100]}...")

                # 2. 重排序
                reranked = self.reranker.rerank(
                    query,
                    retrieved,
                    top_k=self.config.RERANK_TOP_K
                )

                if verbose:
                    print(f"\n重排序后选择 {len(reranked)} 个片段")
                    for i, doc in enumerate(reranked):
                        print(f"[{i}] {doc[:100]}...")

                # 3. 生成回答（带检索内容）
                if verbose:
                    print("\n正在生成回答...")

                answer = self.generator.generate(
                    query=query,
                    contexts=reranked,
                    history=history
                )

            except Exception as e:
                if verbose:
                    print(f"检索过程出错: {str(e)}，转为普通对话模式")
                # 如果检索失败，转为普通对话
                answer = self.generator.generate(
                    query=query,
                    contexts=None,
                    history=history
                )

        else:
            # 直接生成回答（普通对话） - 明确告诉AI不要参考文档
            if verbose:
                print("\n正在生成回答（普通对话模式）...")

            # 构建明确的普通对话提示
            enhanced_query = f"""请注意：这是一个普通对话问题，请不要参考任何文档内容。

用户问题：{query}

请基于您的知识进行回答，不要提及文档相关内容："""

            answer = self.generator.generate(
                query=enhanced_query,
                contexts=None,  # 不提供检索内容
                history=history
            )

        # 添加助手回答到历史
        self.conversation.add_message("assistant", answer)

        if verbose:
            print(f"\n生成回答完成!")
            print('='*50)

        return answer

    def batch_query(self, queries: List[str], verbose: bool = False) -> List[str]:
        """批量查询"""
        answers = []
        for i, query in enumerate(queries):
            if verbose:
                print(f"\n处理第 {i+1}/{len(queries)} 个查询...")

            try:
                answer = self.query(query, verbose)
                answers.append(answer)
            except Exception as e:
                print(f"查询失败: {str(e)}")
                answers.append(f"查询失败: {str(e)}")

        return answers

    def clear_conversation(self):
        """清空对话历史"""
        self.conversation.clear_history()
        print("对话历史已清空")

    def show_conversation_history(self):
        """显示对话历史"""
        history = self.conversation.get_history()
        if not history:
            print("对话历史为空")
            return

        print("\n对话历史:")
        print("-" * 50)
        for i, msg in enumerate(history):
            speaker = "用户" if msg["role"] == "user" else "助手"
            print(f"{i+1}. {speaker}: {msg['content']}")
        print("-" * 50)

def main():
    """主函数"""
    # 创建RAG系统
    rag = RAGSystem()

    try:
        # 初始化系统
        rag.initialize()

        # 欢迎信息
        print("\n" + "="*60)
        print("欢迎使用智能对话系统!")
        print("系统特点:")
        print("1. 智能判断：自动区分文档查询和普通对话")
        print("2. 普通对话时：不会检索文档，仅作为AI助手")
        print("3. 文档查询时：检索相关文档片段后回答")
        print("4. 支持多轮对话，会记住对话历史")
        print("\n输入以下命令进行特殊操作:")
        print("   /clear  - 清空对话历史")
        print("   /history - 查看对话历史")
        print("   /quit   - 退出程序")
        print("="*60)

        # 交互式查询
        while True:
            print("\n" + "-"*50)
            query = input("请输入您的问题: ").strip()

            if not query:
                print("问题不能为空")
                continue

            # 处理特殊命令
            if query == '/quit':
                print("再见！")
                break
            elif query == '/clear':
                rag.clear_conversation()
                continue
            elif query == '/history':
                rag.show_conversation_history()
                continue
            elif query.startswith('/'):
                print(f"未知命令: {query}")
                continue

            try:
                answer = rag.query(query, verbose=True)
                print(f"\n回答: {answer}")
            except Exception as e:
                print(f"查询出错: {str(e)}")

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序出错: {str(e)}")

if __name__ == "__main__":
    main()
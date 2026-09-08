import time
import streamlit as st
from config.config import Config
# 处理数据库
from core.database import DatabaseManager
# 文档加载出来
from core.document_processor import DocumentProcessor
# 向量数据库
from core.vector_store import VectorStore
# rag处理逻辑
from core.rag_system import RAGSystem
import os

# 页面配置
st.set_page_config(
    page_title="四大名著剧情分析助手",
    page_icon='🤖',
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式:css的用处是控制页面上元素的样式
st.markdown("""
<style>
    /* 聊天容器 */
    .chat-container {
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 20px auto;
        max-width: 800px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    /* 头部样式 */
    .chat-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        text-align: center;
        border-radius: 12px 12px 0 0;
    }

    .chat-title {
        font-size: 24px;
        font-weight: 600;
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }

    .chat-subtitle {
        font-size: 14px;
        opacity: 0.9;
        margin-top: 5px;
    }

    /* 聊天消息区域 */
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background: #f8f9fa;
    }

    /* 消息样式 */
    .message {
        margin-bottom: 16px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }

    .message.user {
        flex-direction: row-reverse;
    }

    .message-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }

    .user-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    .assistant-avatar {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: white;
    }

    .message-content {
        max-width: 70%;
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 14px;
        line-height: 1.4;
    }

    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-bottom-right-radius: 4px;
    }

    .assistant-message {
        background: white;
        color: #333;
        border: 1px solid #e1e5e9;
        border-bottom-left-radius: 4px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }

    /* 流式输出动画 */
    .streaming-cursor::after {
        content: '▊';
        animation: blink 1s infinite;
        color: #667eea;
    }

    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }

    /* 文档卡片样式 */
    .doc-card {
        background: 000000;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
    }

    .doc-card:hover {
        border-color: #667eea;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    }

    /* 状态指示器 */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }

    .status-rag {
        background: #e3f2fd;
        color: #1976d2;
    }

    .status-normal {
        background: #f3e5f5;
        color: #7b1fa2;
    }

    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 自定义按钮样式 */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .chat-container {
            margin: 10px;
            height: 85vh;
        }

        .message-content {
            max-width: 85%;
        }
    }
</style>
""", unsafe_allow_html=True)

# 实现文件上传与处理
def upload_and_process_document(uploaded_file, doc_processor, vector_store, db_manager):
    with st.spinner(f"正在处理文档 {uploaded_file.name}..."):
        try:
            # 加载上传的文档
            documents = doc_processor.load_document(uploaded_file)
            # 创建父子文档块
            parent_docs, child_docs = doc_processor.create_parent_child_chunks(documents, uploaded_file.name)
            # 添加文档到向量存储
            parent_vector_ids, child_vector_ids = vector_store.add_documents(parent_docs, child_docs, 0)

            # 将文档存储到MySQL数据库中
            content = "\n".join([doc.page_content for doc in documents])
            print(parent_vector_ids)
            # 插入到数据库表中，一条记录会产生一个id
            doc_id = db_manager.save_document_with_chunks(
                filename=uploaded_file.name,
                file_path="",
                content=content,
                parent_docs=parent_docs,
                child_docs=child_docs,
                parent_vector_ids=parent_vector_ids,
                child_vector_ids=child_vector_ids
            )

            # 现在更新所有相关 chunk 的 metadata
            all_docs = parent_docs + child_docs
            all_ids = parent_vector_ids + child_vector_ids  # 假设 add_documents 返回的 ids 顺序对应 docs

            # 关键：批量设置 document_id
            for doc, vec_id in zip(all_docs, all_ids):
                doc.metadata['document_id'] = str(doc_id)

            vector_store.parent_vectorstore.update_documents(
                ids=parent_vector_ids,
                documents=parent_docs
            )
            vector_store.child_vectorstore.update_documents(
                ids=child_vector_ids,
                documents=child_docs
            )
            st.success(f"✅ 文档 '{uploaded_file.name}' 上传成功！")
            return True
        except Exception as e:
            st.error(f"❌ 文档处理失败: {str(e)}")
            return False

def display_message(role, content, docs=None):
    """显示静态消息"""
    message_class = "message user" if role == "user" else "message"
    avatar_class = "user-avatar" if role == "user" else "assistant-avatar"
    content_class = "user-message" if role == "user" else "assistant-message"
    avatar_icon = "👤" if role == "user" else "🤖"

    st.markdown(f"""
    <div class="{message_class}">
        <div class="message-avatar {avatar_class}">
            {avatar_icon}
        </div>
        <div class="message-content {content_class}">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)


# rag_system, "我们公司经营业务是什么", selected_doc_ids = [1],
def stream_response_generator(rag_system, message, selected_doc_ids, session_id, is_rag_mode=True):
    """生成流式响应的生成器函数"""
    if is_rag_mode:
        # RAG模式 - 需要修改RAGSystem以支持流式输出
        response, retrieved_docs = rag_system.chat_with_documents(
            message, selected_doc_ids, session_id
        )

        # 模拟流式输出（如果RAGSystem不支持流式，可以这样处理）
        print('模型响应:', response)
        # words = response.split()
        current_response = ""

        for i, word in enumerate(response):
            current_response += word
            yield current_response, retrieved_docs if i == len(response) - 1 else None
            time.sleep(0.05)  # 控制流式速度
    else:
        # 普通对话模式
        response = rag_system.normal_chat(message, session_id)

        # 模拟流式输出
        # words = response.split()
        current_response = ""

        for word in response:
            current_response += word
            yield current_response, None
            time.sleep(0.05)

def display_streaming_message(role, generator, docs_placeholder=None):
    """显示流式消息"""
    message_class = "message user" if role == "user" else "message"
    avatar_class = "user-avatar" if role == "user" else "assistant-avatar"
    content_class = "user-message" if role == "user" else "assistant-message"
    avatar_icon = "👤" if role == "user" else "🤖"

    # 创建消息容器的占位符
    message_placeholder = st.empty()
    final_content = ""
    retrieved_docs = None

    # 流式显示内容
    # print("generator->", generator)
    for content, docs in generator:
        final_content = content
        if docs is not None:
            retrieved_docs = docs

        # 添加流式光标效果
        display_content = content + " <span class='streaming-cursor'></span>"

        message_placeholder.markdown(f"""
        <div class="{message_class}">
            <div class="message-avatar {avatar_class}">
                {avatar_icon}
            </div>
            <div class="message-content {content_class}">
                {display_content}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 最终显示（移除光标）
    message_placeholder.markdown(f"""
    <div class="{message_class}">
        <div class="message-avatar {avatar_class}">
            {avatar_icon}
        </div>
        <div class="message-content {content_class}">
            {final_content}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 显示参考文档
    if retrieved_docs and role == "assistant" and docs_placeholder:
        with docs_placeholder:
            with st.expander("📚 参考来源", expanded=False):
                for i, doc in enumerate(retrieved_docs, 1):
                    st.markdown(f"""
                    <div class="doc-card">
                        <strong>📄 片段 {i}</strong><br>
                        {doc.page_content[:200]}{'...' if len(doc.page_content) > 200 else ''}
                    </div>
                    """, unsafe_allow_html=True)

    return final_content, retrieved_docs

# 初始化组件
# @st.cache_resource 热加载  需要的资源直接在第一次启动获取 (类似单例)
# 装饰器
@st.cache_resource
def init_system():
    config = Config()
    db_manager = DatabaseManager(config)
    doc_processor = DocumentProcessor(config)
    vector_store = VectorStore(config)
    rag_system = RAGSystem(config, db_manager, vector_store)
    return config, db_manager, doc_processor, vector_store, rag_system

def main():
    # 初始化系统
    config, db_manager, doc_processor, vector_store, rag_system = init_system()
    # 侧边栏
    with st.sidebar:
        st.markdown("### 📁 文档管理")

        # 文档上传
        uploaded_files = st.file_uploader(
            "上传知识库文档",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="支持 PDF、Word 和txt文件"
        )
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if st.button(f"📤 处理 {uploaded_file.name}", key=f"process_{uploaded_file.name}"):
                    # 当点击这个“按钮”的时候，就可以执行下面的内容，开始处理文件——索引的过程
                    if upload_and_process_document(uploaded_file, doc_processor, vector_store, db_manager):
                        # 页面刷新
                        st.rerun()

        st.markdown("---")

        # 已有文档
        st.markdown("### 📚 知识库")
        documents = db_manager.get_all_documents()

        if documents:
            doc_options = {f"{doc.filename}": doc.id for doc in documents} # {"西游记.txt":1,"刑事案件.txt":2}
            selected_docs = st.multiselect(
                "选择知识源",
                options=list(doc_options.keys()),
                help="选择后将基于文档内容回答问题"
            )
            selected_doc_ids = [doc_options[doc] for doc in selected_docs] # selected_doc_ids = [1,2]

            # 显示文档列表
            for doc in documents:
                st.markdown(f"""
                        <div class="doc-card">
                            <strong>📄 {doc.filename}</strong><br>
                            <small>📅 {doc.created_at.strftime('%Y-%m-%d %H:%M')}</small><br>
                            <small>📊 {doc.chunk_count} 个文档块</small>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("暂无文档，请先上传")
            selected_doc_ids = []

        total_docs = len(documents) if documents else 0
        st.metric("📊 文档数", total_docs)

        if st.button("🗑️ 清空对话"):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()

    # 主聊天界面
    st.markdown("""
    <div class="chat-container">
        <div class="chat-header">
            <div class="chat-title">
                🤖 智能文档检索助手
            </div>
            <div class="chat-subtitle">
                基于知识库的智能问答系统
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 状态显示 # selected_doc_ids = [1,2]
    col1, col2 = st.columns([2, 1])
    with col1:
        if selected_doc_ids:
            st.markdown(f"""
                <div class="status-indicator status-rag">
                    🔍 知识库模式 ({len(selected_doc_ids)} 个文档)
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="status-indicator status-normal">
                    💭 普通对话模式
                </div>
                """, unsafe_allow_html=True)

    # 初始化会话状态
    if 'session_id' not in st.session_state or st.session_state.session_id is None:
        st.session_state.session_id = rag_system.generate_session_id()

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # 聊天消息显示区域
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            # 欢迎消息
            st.markdown("""
            <div class="message">
                <div class="message-avatar assistant-avatar">🤖</div>
                <div class="message-content assistant-message">
                    👋 你好！我是你的AI智能助手。<br><br>
                    💡 <strong>我能做什么：</strong><br>
                    • 📚 基于你上传的文档回答问题<br>
                    • 💬 进行日常对话交流<br>
                    • 🔍 提供准确的信息检索<br><br>
                    请上传文档或直接开始对话吧！
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 显示历史消息
            for message in st.session_state.messages:
                display_message(
                    message["role"],
                    message["content"],
                    message.get("docs")
                )

        # 用户输入
    if prompt := st.chat_input("💬 输入你的问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        # 显示用户消息
        display_message("user", prompt)
        # 创建文档占位符
        docs_placeholder = st.empty()
        # 生成助手回复（流式）
        with st.spinner("🤔 思考中..."):
            if selected_doc_ids:
                # RAG模式流式输出 prompt:你好 # selected_doc_ids = [1]
                generator = stream_response_generator(
                    rag_system, prompt, selected_doc_ids,
                    st.session_state.session_id, is_rag_mode=True
                )
                final_content, retrieved_docs = display_streaming_message(
                    "assistant", generator, docs_placeholder
                )
                # 添加到消息历史
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_content,
                    "docs": retrieved_docs
                })
            else:
                # 普通对话模式流式输出
                generator = stream_response_generator(
                    rag_system, prompt, [],
                    st.session_state.session_id, is_rag_mode=False
                )

                final_content, _ = display_streaming_message("assistant", generator)

                # 添加到消息历史
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_content
                })

if __name__ == '__main__':
    main()
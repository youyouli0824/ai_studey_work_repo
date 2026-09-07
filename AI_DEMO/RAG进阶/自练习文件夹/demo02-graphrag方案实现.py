#本案例核心业务：
# 1.从西游记文本中，引导llm提取出所有的实体、关系等；
# 2.将提取出的实体、关系等，构建出一个图数据库，存入neo4j数据库中；
# 3.从neo4j数据库中，根据用户的问题，从中进行查询；
# 4.需要遵循graphrag的规范，即：用户的问题必须是图数据库中实体、关系的组合；
# 5.文本如下：《西游记》.txt
import os
from typing import List
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
#from base_llm import llm
from langchain_community.graphs.graph_document import (
    GraphDocument,
    Node as LangChainNode,
    Relationship as LangChainRelationship,
)
load_dotenv()

# neo4j的客户端对象
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

# 对于知识图谱实体的提取，温度应该低一些，要遵循事实，不能任意发挥
llm = ChatOpenAI(api_key=os.getenv("DASHSCOPE_API_KEY"),
                 base_url=os.getenv("DASHSCOPE_BASE_URL"),
                 model_name="qwen3.7-plus",
                 temperature=0.15)

# 2.设计实体/关系提取的提示词(核心)
extraction_prompt = ChatPromptTemplate.from_messages([
("system", """你是一个擅长从中文古典小说中提取知识图谱的专家。
请严格从以下文本中提取主要的**实体**和**关系**，重点关注《西游记》的相关内容。
实体类型建议（但不强制只用这些）：
  Person（人、神、妖、仙）、Place（地点、山、洞府、天庭）、Item（法宝、兵器、宝贝）、Event（事件）、Group（组织、派系）

关系类型建议（常用）：
  MASTER_OF, DISCIPLE_OF（师徒）、LOCATED_IN（位于）、OWNS（拥有）、USED_BY（使用）、ENEMY_OF（敌人）、BATTLE_WITH（战斗）、FROM（来自）、CREATED_BY（制造）、TRANSFORMED_INTO（变成）等

规则：
1. 只提取文本中明确出现或强烈暗示的信息，不要脑补。
2. 实体名称尽量使用原文最常见的叫法（例如：孙悟空 而非 美猴王，除非上下文只用了美猴王）。
3. 同一个实体在不同chunk中应尽量保持名称一致。
4. 输出**必须**是合法的JSON，不要包含任何解释、注释、markdown。
5. 如果某段文本实在没有可提取内容，返回空数组。

重要：每个节点 **必须** 有 "id" 字段，且 "id" 是实体的主要名称（例如 "孙悟空"、"菩提祖师"、"斜月三星洞"）。
如果有别名或中文名，可放在 properties 里的 "别称" 或 "中文名"，但 "id" 必须是最常用的叫法。

输出格式（**严格**遵守，不要多一个字）：
{{
  "nodes": [
    {{"id": "孙悟空", "type": "Person"}},
    {{"id": "菩提祖师", "type": "Person"}},
    {{"id": "斜月三星洞", "type": "Place"}}
  ],
  "relationships": [
    {{"source": "孙悟空", "target": "菩提祖师", "type": "DISCIPLE_OF"}},
    {{"source": "孙悟空", "target": "斜月三星洞", "type": "LEARNED_AT"}}
  ]
}}

- "id" 是必须的，且全局唯一（同一个实体不同chunk用相同id）
- type 尽量用：Person, Place, Item, Group
- 关系 type 用英文大写 + 下划线，如 DISCIPLE_OF, LOCATED_IN, OWNS, BATTLE_WITH
只返回纯JSON。
"""),("human", "文本：\n{text}\n请提取。")
])

extract_chain=extraction_prompt | llm | JsonOutputParser()

# 从文本中提取实体/关系
def extract_one_document(doc: Document) -> GraphDocument:
    #{'nodes': [{'id': '唐僧', 'type': 'Person'},...],'relationships': [{'source': '孙悟空', 'target': '唐僧', 'type': 'DISCIPLE_OF'}...]}
    raw=extract_chain.invoke({"text": doc.page_content})
    # 防御性判断，让代码更健壮
    if not isinstance(raw,dict):
        return GraphDocument(
            nodes=[],
            relationships=[],
            source=doc
        )

    # 提取node节点
    node_map={}
    nodes=[]
    for node in raw.get("nodes",[]):
        nid=node.get("id")
        if not nid:
            continue
        # 判断当前节点是否已存在
        if nid in node_map:
            continue
        node_type=node.get("type","Entity")
        # 封装每一个节点对象
        new_node=LangChainNode(id=nid,type=node_type,properties=node.get("properties",{}))
        # {"id":new_node}
        node_map[nid]=new_node
        nodes.append(new_node)

    # 提取关系
    relationships=[]
    for rel in raw.get("relationships",[]):
        rel_source=rel.get("source")
        rel_target=rel.get("target")
        rel_type=rel.get("type")

        # 判断当前关系是否已存在
        if not rel_source or not rel_target or not rel_type:
            continue

        # 防止出现孤立关系，也就是关系的源节点或目标节点不存在的情况
        if rel_source not in node_map or rel_target not in node_map:
            continue

        relation=LangChainRelationship(
            source=node_map[rel_source],
            target=node_map[rel_target],
            type=rel_type,
            properties=rel.get("properties",{}),
        )
        relationships.append(relation)

    return GraphDocument(
        nodes=nodes,
        relationships=relationships,
        source=doc
    )

# 插入到neo4j数据库
def insert_to_neo4j(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 文本切分(建议chunk不要太大)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["\n\n", "\n", "。", "，", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    documents = [Document(page_content=c) for c in chunks]
    print(f"共切分为 {len(documents)} 个chunk，开始提取图结构...")

    graph_documents: List[GraphDocument] = []
    # 每处理10块就打印一次进度，让长任务不至于像「死机」一样毫无反馈
    for i, doc in enumerate(documents, 1):
        if i % 10 == 0 or i == len(documents):
            print(f"  处理中... {i}/{len(documents)}")
        # 提取每一段文本的节点与关系，存入列表
        gd = extract_one_document(doc)
        if gd.nodes or gd.relationships:
            graph_documents.append(gd)

    print(f"提取到 {len(graph_documents)} 个有效的GraphDocument")

    # 执行create或者merge命令
    if graph_documents:
        print("开始执行插入操作")
        # 底层在调用merge命令
        graph.add_graph_documents(graph_documents,
                                  # 把原始文档也存入数据库
                              include_source=True,
                                  # 给每个新建的实体，添加一个额外的标签(__Entity__)，用于后续的查询
                              baseEntityLabel=False)
    else:
        print("没有提取到有效的GraphDocument")

# 从neo4j数据库中查询所有实体
def get_graghrag_chain():
    # 先刷新数据库的schema，确保所有节点和关系都被正确识别
    graph.refresh_schema()

    return GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        # 开启详细日志，方便调试
        verbose=True,
        # 可以执行危险请求，比如删除所有节点和关系
        allow_dangerous_requests=True,
        top_k=30
    )

if __name__ == "__main__":
    # 注意：当插入成功后，以下代码注释掉即可
    #insert_to_neo4j("西游记.txt")

    # 执行查询
    query_chain = get_graghrag_chain()
    questions = [
        "孙悟空的师父是谁？他在哪里学艺？",
        "花果山在哪里？",
        "为什么孙悟空被压在五行山下？",
    ]
    for q in questions:
        print(f'\n问题：{q}:')
        answer = query_chain.invoke({"query": q})
        print(f"\n回答：{answer}")

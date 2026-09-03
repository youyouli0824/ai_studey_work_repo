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

- "id" 是必须的，且全局唯一（同一个实体不同 chunk 用相同 id）
- type 尽量用：Person, Place, Item, Group
- 关系 type 用英文大写 + 下划线，如 DISCIPLE_OF, LOCATED_IN, OWNS, BATTLE_WITH
只返回纯 JSON。
"""),("human", "文本：\n{text}\n请提取。")
])

extract_chain=extraction_prompt | llm | JsonOutputParser()

text='''师徒俩继续向西行。一天，他们来到蛇盘山鹰愁涧，突然从涧中钻出一条白龙来，张着爪子向唐僧冲了过来，悟空慌忙背起唐僧，驾云就跑。那龙追不上悟空，就张开大嘴把白马给吞吃了，然后又钻进深涧了。
悟空把师父安顿在一个安全地方。转身回到涧边去牵马拿行李，发现马不见了，想着一定是被白龙吃了，就在涧边破口大骂∶“烂泥鳅，把我的马吐出来！”白龙听见有人骂他，气得眼睛都红了，跳出水面，张牙舞爪地向悟空扑来。
那龙根本不是悟空的对手，几个回合就累得浑身是汗，转身就逃到水里。悟空又骂了一阵，不见白龙出来，便使了个翻江倒海的本领，把这个清澈的涧水弄得泥沙翻滚，浑浊不清。
那龙在水里待不住了，就硬着头皮跳出来，和悟空打了起来，双方战了几十个回合，白龙实在打不过，摇身变成一条水蛇，钻进了草丛。悟空赶忙追过去，可是连蛇的影子都找不到，气得他把牙咬得乱响。
于是，悟空念咒语，把山神和土地都叫了出来，问他们白龙从哪里来的。山神和土地小心翼翼地说∶“这白龙是观音菩萨放在这儿等候你们，和你们一起取经的。”悟空一听，气得要找观音菩萨讲道理。
观音菩萨料事如神，驾云来到鹰愁涧，告诉悟空∶“这白龙原是西海龙王的儿子，犯了死罪，是我讲了个人情，让他给唐僧当马骑的。如果没这匹龙马，你们就去不了西天。”悟空急着说∶“他藏在水里不出来，怎么办？”
观音菩萨面带微笑，朝涧中喊了一声，那白龙立刻变成一个英俊的公子，来到菩萨跟前。菩萨说∶“小白龙，你师父已经来了！”边说边解下白龙脖上的夜明珠，用柳条蘸些甘露向他身上一挥，吹了口仙气，喊声“变”，白龙就变成了一匹白马。
观音菩萨叫悟空牵着白马去见唐僧，自己回南海落伽山去了。悟空牵着马，兴高采烈地来到唐僧跟前。唐僧一边用手摸着马头，一边说∶“好马，好马，你是在哪儿找的马？”悟空把经过说了一遍，唐僧连忙向南磕头，感谢观音菩萨。'''

result=extract_chain.invoke({"text": text})
print(result)




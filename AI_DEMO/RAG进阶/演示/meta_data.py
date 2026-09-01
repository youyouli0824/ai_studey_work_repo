#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from langchain_core.documents import Document
from langchain_classic.chains.query_constructor.schema import AttributeInfo

docs = [
    Document(
        page_content="作者A团队开发出基于深度学习的图像识别系统，在复杂场景下的识别准确率提升250%",
        metadata={"doc_id":"2wieur08wer8werer","year": 2025, "rating": 9.3, "genre": "AI", "author": "A"},
    ),
    Document(
        page_content="物联网技术成功应用于智能农业监控，作者B主导的项目实现农作物产量提升20%",
        metadata={"year": 2024, "rating": 9.5, "genre": "IoT", "author": "B"},
    ),
    Document(
        page_content="边缘计算平台实现实时数据处理突破，作者C构建的新型架构支持千万级并发计算",
        metadata={"year": 2023, "rating": 8.8, "genre": "Edge Computing", "author": "C"},
    ),
    Document(
        page_content="机器学习模型预测2025年股市趋势，作者A团队构建的模型准确率超95%",
        metadata={"year": 2024, "rating": 9.0, "genre": "Machine Learning", "author": "A"},
    ),
    Document(
        page_content="基于人工智能的心脏病诊断系统在临床应用中达到顶级专家水平，作者B获医疗科技创新奖",
        metadata={"year": 2025, "rating": 7.2, "genre": "AI", "author": "B"},
    ),
    Document(
        page_content="区块链技术在供应链管理中取得突破，作者C设计的新型协议提升供应链透明度30%",
        metadata={"year": 2024, "rating": 8.9, "genre": "Blockchain", "author": "C"},
    ),
    Document(
        page_content="云计算平台实现能效优化，作者A研发的智能调度系统使数据中心能耗降低50%",
        metadata={"year": 2024, "rating": 8.6, "genre": "Cloud", "author": "A"},
    ),
    Document(
        page_content="大数据分析助力环保监测，作者B团队实现污染源识别准确率提升30%",
        metadata={"year": 2025, "rating": 7.5, "genre": "Big Data", "author": "B"},
    )
]

# 需要告诉大模型，元数据里的这些字段的作用是什么
# 元数据字段定义（指导LLM如何解析查询条件）   工具
metadata_field_info = [
    AttributeInfo(
        name="genre",
        # 在metadata中，对英文适配度更高
        description="Technical domain of the article, options: ['AI', 'Blockchain', 'Cloud', 'Big Data']",
        type="string",
    ),
    AttributeInfo(
        name="year",
        description="Publication year of the article",
        type="integer",
    ),
    AttributeInfo(
        name="author",
        description="Author's name who signed the article",
        type="string",
    ),
    AttributeInfo(
        name="rating",
        description="Technical value assessment score (1-10 scale)",
        type="float"
    )
]


# 第1步：从 transformers 库导入 pipeline 工具
# pipeline 是 Hugging Face 提供的一站式推理接口
# 让 transformers 少打印提示信息，避免误以为是报错
import os
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
# 第2步：创建一个情感分析器
# 参数 'sentiment-analysis' 告诉 pipeline 我们要做什么任务
# 这行代码会自动下载一个预训练好的模型（第一次运行需要联网）
#classifier = pipeline('sentiment-analysis')
# 第3步：用情感分析器处理文本
# 传入一句话，模型会返回情感标签（POSITIVE/NEGATIVE）和置信度分数
#result = classifier("I love this course! It's amazing.")
# 第4步：打印结果
# 输出格式：[{'label': 'POSITIVE', 'score': 0.9998}]
# label 是判断结果，score 是模型对这个判断的自信程度（0~1之间）
#print(result)


# 问答任务：先本地加载模型和分词器（模型已缓存，避免每次联网检查导致等待）
MODEL = 'distilbert/distilbert-base-cased-distilled-squad'
tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
model = AutoModelForQuestionAnswering.from_pretrained(MODEL, local_files_only=True)
qa = pipeline('question-answering', model=model, tokenizer=tokenizer)
# 给定一段上下文和一个问题
context = "The Transformer architecture was introduced in 2017 by Google researchers."
question = "When was Transformer introduced?"
# 让模型从上下文中找到答案
result = qa(question=question, context=context)
print(result) # 输出: {'score': 0.98, 'start': 38, 'end': 42, 'answer': '2017'}

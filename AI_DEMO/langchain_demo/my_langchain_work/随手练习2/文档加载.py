from langchain_community.document_loaders import PyPDFLoader

loader=PyPDFLoader(r"AI_DEMO\langchain_demo\my_langchain_work\文档包\01-RAG基础.pdf")
pages=loader.load_and_split()
print(f"第0页：\n{pages[0]}")
pages[0].page_content
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = PyPDFLoader(r"AI_DEMO\langchain_demo\my_langchain_work\文档包\01-RAG基础.pdf")
pages=loader.load_and_split()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=100,
    length_function=len,
)

#print([page.page_content for page in pages if pages])

paragraphs = text_splitter.create_documents([page.page_content.replace('\n', '').replace(' ', '') for page in pages if pages])
print(paragraphs)
for para in paragraphs:
    print(para.page_content)
    print('-------', len(para.page_content))
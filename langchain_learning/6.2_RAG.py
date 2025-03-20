from langchain_community.document_loaders import GitLoader
from langchain_community.document_loaders import TextLoader
import os
from langchain_text_splitters import CharacterTextSplitter

# def file_filter(file_path: str) -> bool:
#     return file_path.endswith(".mdx")

# loader = GitLoader(
#     clone_url="https://github.com/langchain-ai/langchain",
#     repo_path="./langchain",
#     branch="master",    
#     file_filter=file_filter,
# )

# documents = loader.load()
# print(len(documents))

file_path = "langchain_learning/rag_docs/enquate.md"

# file_path が存在するか確認
if not os.path.exists(file_path):
    print(f"ファイルが存在しません: {file_path}")
    exit()
else:
    print(f"ファイルが存在します: {file_path}")

text_splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=1)
source_text = TextLoader(file_path, encoding='utf-8').load()
documents = text_splitter.split_documents(source_text)


from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_ollama.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="kun432/cl-nagoya-ruri-large:latest",
    base_url="http://localhost:11434",
)



try:
    db = Chroma.from_documents(documents, embeddings)
except Exception as e:
    print(e)




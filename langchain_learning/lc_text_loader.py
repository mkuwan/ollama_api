from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import pprint as pp
import os
from langchain_chroma import Chroma
import chromadb


text_splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=1)

embeddings = OllamaEmbeddings(
    model="kun432/cl-nagoya-ruri-large:latest",
    base_url="http://localhost:11434",
)


file_path = "langchain_learning/rag_docs/enquate.md"

# file_path が存在するか確認
if not os.path.exists(file_path):
    print(f"ファイルが存在しません: {file_path}")
    exit()
else:
    print(f"ファイルが存在します: {file_path}")


source_text = TextLoader(file_path, encoding='utf-8').load()
documents = text_splitter.split_documents(source_text)
print('\nソースデータの分割結果: \n')
pp.pprint(documents)

vector_store = Chroma(
    collection_name="enquate",
    embedding_function=embeddings,
    client=chromadb.PersistentClient(path="langchain_learning/rag_docs/chromadb/"),
)

vector_store.add_documents(
    documents=documents,
)


result = vector_store.similarity_search_with_score(query="配送", k=4)
print('\n結果: \n')
pp.pprint(result)
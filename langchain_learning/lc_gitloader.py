# pip install GitPython が必要です

# https://python.langchain.com/docs/integrations/document_loaders/

from langchain_community.document_loaders import GitLoader


def file_filter(file_path: str) -> bool:
    return file_path.endswith(".mdx")

loader = GitLoader(
    clone_url="https://github.com/langchain-ai/langchain",
    repo_path="./langchain",
    branch="master",
    file_filter=file_filter,
)

# この処理は非常に時間がかかるようなので待機してください
raw_docs = loader.load()
print(len(raw_docs))


# Document transformer
# pip install langchain-text-splitters が必要です
from langchain_text_splitters import CharacterTextSplitter

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)

splitted_docs = text_splitter.split_documents(raw_docs)
print(len(splitted_docs))



from langchain_ollama.embeddings import OllamaEmbeddings

embedding = OllamaEmbeddings(
    model="kun432/cl-nagoya-ruri-large:latest",
    base_url="http://localhost:11434",
)


# vector = embedding.embed_query("AWSのS3からデータを読み込むためのDocument loaderはありますか？")
# print(len(vector))
# print(vector)


# from langchain_chroma import Chroma

# db = Chroma.from_documents(
#     documents=splitted_docs,
#     embedding=embedding,
# )

# retriever = db.as_retriever()

# query = "AWSのS3からデータを読み込むためのDocument loaderはありますか？"

# context_docs = retriever.invoke(query)
# print(f"len = {len(context_docs)}")

# first_doc = context_docs[0]
# print(f"metadata = {first_doc.metadata}")

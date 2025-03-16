from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_core.documents import Document

embeddings = OllamaEmbeddings(
    model="kun432/cl-nagoya-ruri-large:latest",
    base_url="http://localhost:11434",
)


vector = embeddings.embed_query("AWSのS3からデータを読み込むためのDocument loaderはありますか？")
print(len(vector))
print(vector)


from langchain_chroma import Chroma

# "./rag_docs/enquate.md"　のファイルを読み込む
with open("langchain_learning/rag_docs/enquate.md", "r", encoding="utf-8") as f:
    content = f.read()



doc01 = Document(
                page_content=content,
                metadata={"source": "enquate.md"}
            )

docs = [doc01]

str_docs = [content]

# db = Chroma.from_documents(
#     documents=docs,
#     embedding=embeddings,
# )

# うまくいかない、エラーが出る
db = Chroma.from_texts(
    texts=str_docs,
    embedding=embeddings,
)

retriever = db.as_retriever()

query = "顧客対応についての回答は？"

context_docs = retriever.invoke(query)
print(f"len = {len(context_docs)}")

first_doc = context_docs[0]
print(f"metadata = {first_doc.metadata}")


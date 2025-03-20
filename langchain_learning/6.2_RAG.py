from langchain_community.document_loaders import GitLoader

def file_filter(file_path: str) -> bool:
    return file_path.endswith(".mdx")

loader = GitLoader(
    clone_url="https://github.com/langchain-ai/langchain",
    repo_path="./langchain",
    branch="master",    
    file_filter=file_filter,
)

documents = loader.load()
print(len(documents))

# for doc in documents:
#     print(doc.page_content)


from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_ollama.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="kun432/cl-nagoya-ruri-large:latest",
    base_url="http://localhost:11434",
)



counnt = 0
while True:
    try:
        db = Chroma.from_documents(documents, embeddings)
    except Exception as e:
        print(e)
        counnt += 1
        if counnt > 5:
            break



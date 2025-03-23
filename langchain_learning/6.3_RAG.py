from langchain_community.document_loaders import GitLoader
from langchain_community.document_loaders import TextLoader
import os
from langchain_text_splitters import CharacterTextSplitter
import pprint as pp
import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_ollama.embeddings import OllamaEmbeddings
from typing import Iterator
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.documents import Document
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import chain
import time
import re
import pprint as pp
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from operator import itemgetter
import json
from langchain_community.retrievers import TavilySearchAPIRetriever
import fitz
import pymupdf4llm
from tqdm import tqdm
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)
from pathlib import Path
from uuid import uuid4
from pydantic import BaseModel, Field


with open(".local_pass.json") as f:
    config = json.load(f)  # 1回だけ読み込む
    TAVILY_API_KEY = config["TAVILY_API_KEY"]
    LANGSMITH_API_KEY = config["LANGSMITH_API_KEY"]
    LANGSMITH_PROJECT = config["LANGSMITH_PROJECT"]
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT


embeddings = OllamaEmbeddings(
    model="mxbai-embed-large",
    base_url="http://localhost:11434",
)

model = ChatOpenAI(
    # model="mistral:latest",
    # model="llama3.2",
    model="phi3",
    temperature=0.2,
    base_url="http://localhost:11434/v1/",
    api_key="ollama",
)

def get_markdown_image_path(markdown: str) -> str:
    """Markdownの画像のパスを調整します。

    Args:
        markdown (str): markdownのテキスト。
        output_path (str): 修正後の画像のパス。

    Returns:
        str: 調整されたmarkdownのテキスト。
    """
    #　![]ではじまり　)で終わる文字列を取得する 1つめのみ
    image_texts = re.findall(r"!\[.*?\)", markdown)

   
    for image_text in image_texts:
        # `![]`や括弧を削除して画像パスを抽出
        image_path = re.sub(r"!\[.*?\(", "", image_text)  # `.*?`で任意の文字列を非貪欲にマッチ
        image_path = re.sub(r"\)", "", image_path)       # 閉じ括弧を削除
        print(image_path)

        # imaage_pathの中で最後の/より前の文字列を取得
        directory = image_path.rpartition('/')[0]
        print(f"direcotry: {directory}")
        return directory
    

def adjust_markdown_image_path(markdown: str, output_path: str = "./images/") -> str:
    """Markdownの画像のパスを調整します。

    Args:
        markdown (str): markdownのテキスト。
        output_path (str): 修正後の画像のパス。

    Returns:
        str: 調整されたmarkdownのテキスト。
    """
    # 画像のパスを修正
    image_directory = get_markdown_image_path(markdown)

    md_image = f"![]({image_directory}"
    adjusted_md_image = f"![]({output_path}"

    return markdown.replace(md_image, adjusted_md_image)
       
    

# https://qiita.com/camcam/items/ae9ac4860968389804bd　を参考に作成
def extract_and_restructure_pdf(
    pdf_path: str,
    file_name: str,
    output_md_path: str,
    output_raw_text_path: str,
    first_page: Optional[int] = 1,
    last_page: Optional[int] = None,
    max_retries: int = 3,
    retry_delay: int = 2,
    use_llm: bool = False,
) -> None:  
    """PDFの内容を抽出して整形し、Markdownと生テキストファイルに保存します。

    Args:
            pdf_path (str): 処理するPDFファイルのパス。
            file_name (str): 処理するPDFファイルのファイル名。
            output_md_path (str): 整形結果を保存するMarkdownファイルのパス。
            output_raw_text_path (str): 抽出された生テキストを保存するファイルのパス。
            first_page (Optional[int]): 処理を開始するページ番号（1始まり）。デフォルトは1。
            last_page (Optional[int]): 処理を終了するページ番号。デフォルトは最終ページ。
            max_retries (int): LLM呼び出しの最大リトライ回数。デフォルトは3。
            retry_delay (int): LLM呼び出し失敗時のリトライ間隔（秒）。デフォルトは2秒。
    """    
        
    try:
        print("# PDFを開く")
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        print("# ページ範囲の計算")
        first_page = first_page or 1
        last_page = last_page or total_pages

        raw_texts = []  # 生テキストを保存するリスト
        markdown_results = []  # 整形後のテキストを保存するリスト

        os.makedirs(output_md_path, exist_ok=True)
        os.makedirs(Path(output_md_path).joinpath("images"), exist_ok=True)
        os.makedirs(output_raw_text_path, exist_ok=True)

        print("# PDFページを順に処理")
        for page_num in tqdm(range(first_page - 1, last_page), desc="Processing PDF Pages"):
            page = doc[page_num]
            extracted_text = page.get_text("text")  # テキスト抽出

            # print(f"# PDFページ:= {page_num + 1}")

            if use_llm:
                # LLMへの指示を作成
                messages = [
                    SystemMessage(content=(
                        "あなたは優れたアシスタントです。以下に与えられるテキストはPDFから抽出された内容であり、体裁が崩れている可能性があります。\n\n"
                        "以下の指示に従って、テキストの整形を行ってください:\n\n"
                        "1. 句読点や改行の位置を適切に整え、誤字脱字を修正してください（文脈に基づく範囲内で）。\n"
                        "2. 元のテキストに含まれる情報を削除しないでください。\n"
                        "3. 表形式のデータは可能な限り元のレイアウトを維持してください。\n"
                        "4. グラフの軸の数値関係を確認し、適切に説明してください。\n\n"
                        "最終結果はMarkdown形式で出力してください。"
                    )),
                    HumanMessage(content=f"## ページ {page_num + 1}\n\n### 抽出されたテキスト:\n\n{extracted_text}")
                ]
                
                # LLMを使用して整形
                for attempt in range(max_retries):
                    try:
                        response = model.invoke(messages)
                        markdown_results.append(response.content)
                        break
                    except Exception as e:
                        print(f"Error during OpenAI API call for page {page_num + 1} (attempt {attempt + 1}): {e}")
                        if attempt == max_retries - 1:
                            print(f"Failed after max retries for page {page_num + 1}.")
                        time.sleep(retry_delay)

            # 抽出されたテキストを保存
            raw_texts.append(f"## ページ {page_num + 1}\n{extracted_text}")


        if use_llm:
            output_markdown = "\n\n".join(markdown_results)
        else:
            output_markdown = pymupdf4llm.to_markdown(
                doc=pdf_path,
                write_images=True,
                image_path=Path(output_md_path).joinpath("images"),
                image_format="jpg",
                dpi=150,
                show_progress=True,
            )
            output_markdown = adjust_markdown_image_path(output_markdown, output_path="./images/")

        # 整形結果をMarkdownで保存
        markdown_path = Path(output_md_path).joinpath(f"{file_name}.md")
        with open(markdown_path, "w", encoding="utf-8") as md_file:
            # md_file.write("\n\n".join(markdown_results))
            md_file.write(output_markdown)
        print(f"整形結果がMarkdownファイルに保存されました: {markdown_path}")

        # 生テキストをファイルに保存
        text_path = Path(output_raw_text_path).joinpath(f"{file_name}.txt")
        with open(text_path, "w", encoding="utf-8") as raw_file:
            raw_file.write("\n\n".join(raw_texts))
        print(f"抽出されたテキストが保存されました: {text_path}")

    except Exception as e:
        print(f"Error processing PDF: {e}")


def create_vector_store(collection_name: str) -> Chroma:
    """ドキュメントのリストをChromaに変換します。

    Args:
        embeddings (OllamaEmbeddings): OllamaEmbeddingsのインスタンス。

    Returns:
        Chroma: Chromaのインスタンス。
    """
    # Chromaクライアントの初期化
    client = chromadb.PersistentClient(path="./langchain_learning/rag/chroma")
    
    # コレクションが既に存在する場合は作成しない
    if collection_name in client.list_collections():
        print(f"Collection '{collection_name}' already exists. Skipping creation.")
        return Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            client=client,
        )

    documents = []
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=10)
    for root, dirs, files in os.walk("./langchain_learning/rag/java_docs/output_md"):
        for file in files:
            if file.endswith(".md"):
                print(os.path.join(root, file))
                source_text = TextLoader(os.path.join(root, file), encoding='utf-8').load()
                documents.extend(text_splitter.split_documents(source_text))

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        client=client,    
    )

    vector_store.add_documents(
        documents=documents,
    )

    return vector_store


def recreate_vector_store(collection_name: str) -> Chroma:
    """既存のChromaコレクションを削除して再作成します。

    Args:
        collection_name (str): 再作成するコレクションの名前。

    Returns:
        Chroma: 再作成されたChromaのインスタンス。
    """
    # Chromaクライアントの初期化
    client = chromadb.PersistentClient(path="./langchain_learning/rag/chroma")
    
    # 既存のコレクションを削除
    if collection_name in client.list_collections():
        print(f"Collection '{collection_name}' exists. Deleting it for recreation.")
        client.delete_collection(collection_name)

    return create_vector_store(collection_name)


def get_vector_store(collection_name) -> Chroma:
    """Chromaのインスタンスを取得します。

    Args:
        collection_name (str): コレクションの名前。

    Returns:
        Chroma: Chromaのインスタンス。
    """
    client = chromadb.PersistentClient(path="./langchain_learning/rag/chroma")

    if collection_name in client.list_collections():
        return Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            client=client,
        )
    else:
        print(f"Collection '{collection_name}' does not exist. Please create it first.")
        return None


    

def hyphthetical_doc_embeddings(question: str, vector_store: Chroma) -> None:
    """
    HyDE（Hypothetical Document Embeddings） 
    シンプルなRAGの構成では、ユーザーの質問に対して埋め込みベクトルの類似度の高いドキュメントを検索します。
    しかし、実際に検索したいのは、質問に類似するドキュメントではなく、回答に類似するドキュメントです。
    そこで、HyDE（Hypothetical Document Embeddings）注3という手法があります。
    HyDEでは、ユーザーの質問に対してLLMに仮説的な回答を推論させ、その出力を埋め込みベクトルの類似度検索に使用します。

    Args:
        question (str): ユーザーの質問

    Returns:
        None
    """
    
    # documents = []
    # text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=10)
    # for root, dirs, files in os.walk("./langchain_learning/rag/java_docs/output_md"):
    #     for file in files:
    #         if file.endswith(".md"):
    #             print(os.path.join(root, file))
    #             source_text = TextLoader(os.path.join(root, file), encoding='utf-8').load()
    #             documents.extend(text_splitter.split_documents(source_text))

    # try:
    #     vector_store = Chroma.from_documents(documents, embeddings)
    # except Exception as e:
    #     print("エラーが発生しました")
    #     print(e)

    retriever = vector_store.as_retriever()

    hypothetical_prompt = ChatPromptTemplate.from_template(
    """
    次の質問に回答する一文を書いてください。sourceを必ず記載してください。

    質問:
    {question}
    """)

    prompt = ChatPromptTemplate.from_template('''\
    以下の文脈だけを踏まえて質問に回答してください。
    
    文脈:"""
    {context}
    """

    質問:"""
    {question}
    """
    ''')

    hyphthetical_chain = hypothetical_prompt | model | StrOutputParser()

    hyde_rag_chain = ({
        "question": RunnablePassthrough(),
        "context": hyphthetical_chain | retriever,
    } | prompt | model | StrOutputParser())

    for chunk in hyde_rag_chain.stream(question):
        print(chunk, end="", flush=True)

    
def plural_query_prompt(question: str, vector_store: Chroma) -> None:
    """複数の質問を入力するプロンプトを表示します。

    Args:
        query (str): ユーザーの質問。

    Returns:
        None
    """
    class QueryGenerationOutput(BaseModel):
        queries: List[str] = Field(..., description="検索クエリのリスト")

    query_generation_prompt = ChatPromptTemplate.from_template("""\
    質問に対してベクターデータベースから関連文書を検索するために、
    3つの異なる検索クエリを生成してください。
    距離ベースの類似性詮索の限界を克服するために、
    ユーザーの質問に対して複数の視点を提供することが目標です。
                                                               
    質問:
    {question}
    """)

    query_generation_chain = (
        query_generation_prompt
         | model.with_structured_output(QueryGenerationOutput)
         | (lambda x: x.queries)
    )

    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_template('''\
    以下の文脈だけを踏まえて質問に回答してください。
    
    文脈:"""
    {context}
    """

    質問:"""
    {question}
    """
    ''')

    multi_query_rag_chain = ({
        "question": RunnablePassthrough(),
        "context": query_generation_chain | retriever.map(),
    } | prompt | model | StrOutputParser())

    for chunk in multi_query_rag_chain.stream(question):
        print(chunk, end="", flush=True)


if __name__ == '__main__':
    is_create_from_pdf = False

    if is_create_from_pdf:
        # Java_docsフォルダのpdfファイルを処理します
        # 整形結果の保存先
        output_base_path = Path("./langchain_learning/rag/java_docs/output_md")  
        # 抽出されたテキストの保存先
        output_raw_text_base_path = Path("./langchain_learning/rag/java_docs/output_raw")  

        # # 出力ディレクトリの作成
        os.makedirs(output_base_path, exist_ok=True)
        os.makedirs(output_raw_text_base_path, exist_ok=True)

        # doc_base_path 配下のフォルダとファイルを再帰的に取得
        doc_base_path = Path("./langchain_learning/java_docs")
        for root, dirs, files in doc_base_path.walk():
            for file in files:
                print(root.joinpath(file))
                # PDF処理の実行
                extract_and_restructure_pdf(
                    pdf_path=root.joinpath(file),
                    file_name=Path(file).stem, # 拡張子を除いたファイル名
                    output_md_path=output_base_path,  # .joinpath(file).with_suffix('.md'),
                    output_raw_text_path=output_raw_text_base_path,  # .joinpath(file).with_suffix('.txt'),
                    first_page= None,  # 最初のページから処理
                    last_page= None,    # 最後のページまで処理
                    use_llm=False,  # LLMを使用しない
                )
        
        vector_store = create_vector_store("java_docs_index")

        result = vector_store.similarity_search_with_score(query="Javaのインターフェースとは何ですか？", k=4)
        pp.pprint(result)

        # vector_store = recreate_vector_store("java_docs_index")
        # result = vector_store.similarity_search_with_score(query="Javaのインターフェースとは何ですか？", k=4)
        # pp.pprint(result)


    vector_store = get_vector_store("java_docs_index")
    
    print(f"{"*"*10} ベクターストアの取得 {"*"*10}")
    hyphthetical_doc_embeddings("Javaのインターフェースとは何ですか？", vector_store)


    print(f"{"*"*10} 複数の検索クエリを使用した場合 {"*"*10}")
    plural_query_prompt("Javaのクラスとは何ですか？", vector_store)
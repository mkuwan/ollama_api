from markitdown import MarkItDown
from bs4 import BeautifulSoup
import requests
import io
import tempfile
from openai import OpenAI

def get_html_from_url(url):
    # ウェブサイトのHTMLを取得
    response = requests.get(url)
    response.raise_for_status()  # エラーチェック

    # BeautifulSoupを使用してHTMLを解析
    soup = BeautifulSoup(response.text, 'html.parser')

    # <script>, <path>, <style>タグを削除
    for script in soup(["script", "path", "style"]):
        script.decompose()

    # BeautifulSoupで解析したHTMLを,メモリ上でtemp.htmlとして保存、それをmarkdownに変換します
    # with open("/temp.html", "w", encoding="utf-8") as file:
    #     file.write(str(soup))

    # # メモリ上にHTMLファイルを作成
    # html_file_in_memory = io.StringIO(str(soup))

    # print(html_file_in_memory.read())  # 内容を読み取る
    

    # # Get the title 
    # title = soup.title.string
    # # Get the body
    # body = soup.body    
    # # Get the text
    # text = body.get_text()
    html_content = str(soup)

    return html_content

def exchange_html_to_md(html_content):
    # MarkItDownを使用してHTMLをMarkdownに変換
    mid = MarkItDown()
    markdown_content = mid.convert(html_content, input_format="html")

    return markdown_content

def iroiro():
    url = "https://www.ibm.com/jp-ja/topics/prompt-chaining"
    # ウェブサイトのHTMLを取得
    response = requests.get(url)
    response.raise_for_status()  # エラーチェック

    # BeautifulSoupを使用してHTMLを解析
    soup = BeautifulSoup(response.text, 'html.parser')

    # <script>, <path>, <style>タグを削除
    for tags in soup(["script", "path", "style"]):
        tags.decompose()

    # 一時ファイルを作成してHTMLコンテンツを書き込む
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_file:
        temp_file.write(str(soup).encode('utf-8'))
        temp_file_path = temp_file.name

    # MarkItDownを使用してHTMLをMarkdownに変換
    ollama_client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )
    # model="llava"
    # md = MarkItDown(llm_client=ollama_client, llm_model=model)
    # image_file_path = "N:\\python_projects\\ollama_api\\images\\1672327766467.jpg"
    # result = md.convert(image_file_path)

    model="llama3.1"
    md = MarkItDown(llm_client=ollama_client, llm_model=model)
    result = md.convert(temp_file_path)

    print(result.text_content)  # 変換されたMarkdownを表示

    # 一時ファイルを削除
    import os
    print(f"Delete the temporary file: {temp_file_path}")
    os.remove(temp_file_path)



if __name__ == "__main__":
    # url = "https://www.ibm.com/jp-ja/topics/prompt-chaining"
    # html = get_html_from_url(url)
    # # print(markdown)
    # if html is not None:
    #     print(f"{"*" * 10} Convert the HTML to markdown {"*" * 10}")
    #     md_text = exchange_html_to_md(html)
    #     print(md_text)
    # else:
    #     print("Failed to get the HTML from the URL.")
    iroiro()
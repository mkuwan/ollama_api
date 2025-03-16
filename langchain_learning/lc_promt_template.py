# https://python.langchain.com/docs/concepts/prompt_templates/

from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from typing import List
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import base64
from io import BytesIO
from PIL import Image


# PromptTemplate
def use_prompt_template():
    prompt_template = PromptTemplate.from_template("Tell me joke about {topic}")

    prompt = prompt_template.invoke({"topic": "chickens"})
    
    print(prompt)


# ChatPromptTemplate
def use_chat_prompt_template():
    
    chat_prompt_template = ChatPromptTemplate([
        ("system", "You are a helpful assistant"),
        ("user", "Tell me a joke about {topic}")
    ])

    chat_prompt = chat_prompt_template.invoke({"topic": "chickens"})
    
    print(chat_prompt)


# MessagesPlaceholder
def use_messages_placeholder():
    prompt_template = ChatPromptTemplate([
        ("system", "You are a helpful assistant"),
        MessagesPlaceholder("msgs")
    ])

    messages = prompt_template.invoke({"msgs": [HumanMessage(content="hi!")]})

    print(messages)



def convert_to_base64(pil_image):
    """
    Convert PIL images to Base64 encoded strings

    :param pil_image: PIL image
    :return: Re-sized Base64 string
    """

    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")  # You can change the format if needed
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


def analyze_image():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "user",
                [
                    {"type": "text", "text": "画像を日本語で説明してください。"},
                    {"type": "image_url", "image_url": {"url": "{image_b64}"}},
                ],
            ),
        ]
    )
    # image_url = "https://raw.githubusercontent.com/yoshidashingo/langchain-book/main/assets/cover.jpg"

    file_path = "./images/1672327766467.jpg"
    pil_image = Image.open(file_path)
    image_b64 = convert_to_base64(pil_image)

    prompt_value = prompt.invoke({"image_b64": image_b64})

    chat = ChatOllama(
        model="llama3.2-vision:latest",
        temperature=0,
        base_url="http://localhost:11434"
    )
    response = chat.invoke(prompt_value)
    print(response.content)



if __name__ == "__main__":
    print(f"{"*" * 10} PromptTemplate {"*" * 10}")
    use_prompt_template()

    print(f"{"*" * 10} ChatPromptTemplate {"*" * 10}")
    use_chat_prompt_template()

    print(f"{"*" * 10} MessagesPlaceholder {"*" * 10}")
    use_messages_placeholder()

    print(f"{"*" * 10} analyze_image {"*" * 10}")
    analyze_image()

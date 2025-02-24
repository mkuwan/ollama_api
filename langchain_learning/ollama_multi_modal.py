# https://python.langchain.com/docs/integrations/chat/ollama/

import base64
from io import BytesIO

from IPython.display import HTML, display
from PIL import Image
from langchain_ollama import OllamaLLM
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

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


def plt_img_base64(img_base64):
    """
    Display base64 encoded string as image

    :param img_base64:  Base64 string
    """
    # Create an HTML img tag with the base64 string as the source
    image_html = f'<img src="data:image/jpeg;base64,{img_base64}" />'
    # Display the image by rendering the HTML
    display(HTML(image_html))


file_path = "./images/1672327766467.jpg"
pil_image = Image.open(file_path)
image_b64 = convert_to_base64(pil_image)
# plt_img_base64(image_b64)



print("*" * 10, "OllamaLLM", "*" * 10)
llm = OllamaLLM(model="llava")

llm_with_image_context = llm.bind(images=[image_b64])
response = llm_with_image_context.invoke("What is this image?")
print(response)





print("*" * 10, "ChatOllama", "*" * 10)
model = ChatOllama(
    model="llama3.2-vision",
    base_url="http://localhost:11434",
    temperature=0.2,
)

def prompt_func(data):
    text = data["text"]
    image = data["image"]

    image_part = {
        "type": "image_url",
        "image_url": f"data:image/jpeg;base64,{image}",
    }

    content_parts = []

    text_part = {"type": "text", "text": text}

    content_parts.append(image_part)
    content_parts.append(text_part)

    return [HumanMessage(content=content_parts)]


from langchain_core.output_parsers import StrOutputParser

chain = prompt_func | model | StrOutputParser()

for chunk in chain.stream({"text": "What is this image?", "image": image_b64}):
    print(chunk, end='', flush=True)
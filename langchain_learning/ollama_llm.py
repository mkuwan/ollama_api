# https://python.langchain.com/docs/integrations/llms/ollama/

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


template = """
Question: {question}
Answer: ステップバイステップで考えます"""

prompt = ChatPromptTemplate.from_template(template)

model = OllamaLLM(
    base_url="http://localhost:11434",
    model="llama3.2"
    )

chain = prompt | model

response = chain.invoke({"question": "What is LangChain?"})

print(response)
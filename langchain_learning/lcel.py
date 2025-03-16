# LCELとは
# LangChain Expression Language（LCEL）は、LangChainの出力を表現するための言語です。

# LangChain Expression Language（LCEL）は、LangChainでのChainの記述方法です。
# LCELではプロンプトやLLMを「|」でつなげて書き、処理の連鎖（Chain）を実装します。
# 2023年10月頃から、LangChainではLCELを使う実装が標準的となりました。

# LangChainでは、Prompt template・LLM/Chat model・Output parserを連結して、
# Chainとして一連の処理を実行するのが基本となります。



from typing import Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables.base import RunnableSerializable


# *******************************************
# 出力のフォーマットを指定します
# RecipeクラスのインスタンスをPydanticOutputParserに渡して、フォーマット指示を取得します
#
# 実際にはPydanticOutputParserを直接使うよりも簡単なため、
# 「with_structured_output」を使うことをおすすめします。
# *******************************************
class Recipe(BaseModel):
    ingredients: list[str] = Field(description="ingredients of the dish")
    steps: list[str] = Field(description="steps to make the dish")
    notes: list[str] = Field(description="notes for the steps to make the dish")

output_parser = PydanticOutputParser(pydantic_object=Recipe)


# *******************************************
# プロンプトを生成します
# *******************************************
prompt = ChatPromptTemplate.from_messages(
    [
        ("system","ユーザーが入力した料理のレシピを考えてください。日本語で回答してください。\n\n {format_instructions}"),
        ("human", "{dish}"),
    ]
)

# *******************************************
# 出力のフォーマット指示をプロンプトに追加します
# *******************************************
prompt_with_format_instructions = prompt.partial(
    format_instructions=output_parser.get_format_instructions()
)




# *******************************************
# 出力形式をjsonに指定してChatOllamaを生成します
# *******************************************
chat = ChatOllama(
        model="mistral:latest",
        temperature=0,
        base_url="http://localhost:11434",
        format="json",
    )


# *******************************************
# プロンプトとChatをChiain、output_paserでつなげて、処理の連鎖（Chain）を実装します
# {dish}にチキンカレーを入力してプロンプトを生成します
# *******************************************
chain: RunnableSerializable[dict, Any] = prompt_with_format_instructions | chat | output_parser
response = chain.invoke({"dish": "チキンカレー"})
print(type(response))
print(response)




print(f"{'*'*10} PydanticOutputParserではなくwith_structured_outputを使用する {'*'*10}")
# 実際にLangChainでLLMに構造化データを出力させるときは、
# PydanticOutputParserを直接使うよりも簡単なため、
# 「with_structured_output」を使うことをおすすめします。
prompt2 = ChatPromptTemplate.from_messages(
    [
        ("system","ユーザーが入力した料理のレシピを考えてください。日本語で回答してください。"),
        ("human", "{dish}"),
    ]
)
chain2 = prompt2 | chat.with_structured_output(Recipe)
response2 = chain2.invoke({"dish": "キーマカレー"})
print(type(response2))
print(response2)
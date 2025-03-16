# Output parserを使う例
# ポイントは次の2つです。 
# - Recipeクラスの定義をもとに、出力形式を指定する文字列が自動的に作られた 
# - LLMの出力を簡単にRecipeクラスのインスタンスに変換できた 
# 
# このようにとても便利なOutput parserですが、
# LLMが不完全なJSONを返してきたりするとエラーになってしまいます。
# JSONなどの構造化データをLLMに安定的に出力させるには、
# Chat Completions APIのJSONモードのような機能を使ったり、
# Function callingを応用することが有用です。
# LangChainでFunction callingを応用して構造化データを出力する方法は、
# 後ほどwith_structured_outputのコラムで紹介します。



from pydantic import BaseModel, Field

class Recipe(BaseModel):
    # ingredients: list[str] = Field(description="ingredients of the dish")
    # steps: list[str] = Field(description="steps to make the dish")
    材料: list[str] = Field(description="ingredients of the dish")
    手順: list[str] = Field(description="steps to make the dish")
    注意事項: list[str] = Field(description="notes for the steps to make the dish")



# Outputのフォーマットを指定します
# RecipeクラスのインスタンスをPydanticOutputParserに渡して、フォーマット指示を取得します
from langchain_core.output_parsers import PydanticOutputParser

output_parser = PydanticOutputParser(pydantic_object=Recipe)

format_instructions = output_parser.get_format_instructions()


# レシピのフォーマット指示を表示します
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system","ユーザーが入力した料理のレシピを考えてください。日本語で回答してください。\n\n" \
                "{format_instructions}"
        ),
        ("human", "{dish}"),
    ]
)

# レシピのフォーマット指示{format_instructions}をプロンプトに追加します
prompt_with_format_instructions = prompt.partial(
    format_instructions=format_instructions
)

# {dish}にチキンカレーを入力してプロンプトを生成します
prompt_value = prompt_with_format_instructions.invoke(
    {"dish": "チキンカレー"}
)

# print(f"{"*"*10} チキンカレー {"*"*10}")
# print("=== role: system ===")
# print(prompt_value.messages[0].content)
# print("=== role: user ===")
# print(prompt_value.messages[1].content)

# ********** チキンカレー **********
# === role: system ===
# ユーザーが入力した料理のレシピを考えてください。

# The output should be formatted as a JSON instance that conforms to the JSON schema below.

# As an example, for the schema {"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}
# the object {"foo": ["bar", "baz"]} is a well-formatted instance of the schema. The object {"properties": {"foo": ["bar", "baz"]}} is not well-formatted.

# Here is the output schema:
# ```
# {"properties": {"ingredients": {"description": "ingredients of the dish", "items": {"type": "string"}, "title": "Ingredients", "type": "array"}, "steps": {"description": "steps to make the dish", "items": {"type": "string"}, "title": "Steps", "type": "array"}}, "required": ["ingredients", "steps"]}
# ```
# === role: user ===
# チキンカレー

from langchain_ollama import ChatOllama

chat = ChatOllama(
    model="mistral:latest",
    temperature=0,
    base_url="http://localhost:11434"
)

response = chat.invoke(prompt_value)
print(response.content)
# ```
# {
#   "材料": ["チキン", "カレー粉", "油", "塩", "ソイソース", "ミルク", "パウダー", "ベジタブル（オプション）"],
#   "手順": [
#     "チキンをカレー粉に漬ける",
#     "油にチキンを焼く",
#     "ソイソース、ミルク、パウダーを混ぜてチキンに漬ける",
#     "ベジタブル（オプション）を加えて炊き終わる"
#   ],
#   "注意事項": [
#     "チキンは前回の冷凍状態から直接使用しないでください",
#     "カレー粉に水を少し加えて漬けると、チキンが溶けたり粘ったりすることがあります。その場合は、水を少し取り除きながら漬けることで修正できます"
#   ]
# }
# ```

# for chunk in chat.stream(prompt_value):
#     print(chunk.content, end="", flush=True)


# このように実装すると、Pydanticのモデルのインスタンスを得ることができます。
recipe = output_parser.invoke(response)
print(type(recipe))
print(recipe)
# <class '__main__.Recipe'>
# 材料=['チキン', 'カレー粉', '油', '塩', 'ソイソース', 'ミルク', 'パウダー', 'ベジタブル（オプション）'] 
# 手順=['チキンをカレー粉に漬ける', '油にチキンを焼く', 'ソイソース、ミルク、パウダーを混ぜてチキンに漬ける', 'ベジタブル（オプション）を加 えて炊き終わる'] 
# 注意事項=['チキンは前回の冷凍状態から直接使用しないでください', 'カレー粉に水を少し加えて漬けると、チキ ンが溶けたり粘ったりすることがあります。その場合は、水を少し取り除きながら漬けることで修正できます']



# StrOutputParserは、LLMの出力をテキストに変換するために使用します。
# たとえば、ChatOpenAIをinvokeすると、AIMessageが得られます。
# AIMessageに対してStrOutputParserをinvokeすると、テキストを取り出すことができます。
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser

str_output_parser = StrOutputParser()
message = AIMessage(content="Hello, 私はAIアシスタントです。")
text = str_output_parser.invoke(message)
print(type(text))
print(text)

# このサンプルコードだけを見ると、「わざわざStrOutputParserを使わなくても、
# ai_message.contentと書いてテキストを取り出せばいいのではないか」と思うかもしれません。
# しかし、StrOutputParserは次節で解説するLangChain Expression Language（LCEL）の
# 構成要素として重要な役割を果たします。
# LangChain Expression Language（LCEL）を学ぶと、
# StrOutputParserがなぜ存在するのか理解できるはずです。




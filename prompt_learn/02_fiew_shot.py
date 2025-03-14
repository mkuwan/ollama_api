# Few-Shot Prompting 
# プロンプトにいくつか実際の質問と回答例のペアを記載する手法
# https://www.ibm.com/jp-ja/topics/few-shot-learning

from ollama_chat import OllamaChatMessage

ollama = OllamaChatMessage(model="llama3.2", second=0.01)

# ラベリング
# ある文章があった場合に、その内容に対してラベリングを行うことで、その文章の内容を理解しやすくすることができます
# 例
# ある文章に対して、その文章が「スポーツ」に関するものであるか、「政治」に関するものであるかをラベリングすることで、その文章の内容を理解しやすくすることができます
## One/Few Shot

what_is_this = "イチゴ"
message = f"""{what_is_this}は何ですか？"""
for chunk in ollama.response_from_message_stream(message):
    print(chunk, end="", flush=True)

print("\n")

message = f"""
りんご => フルーツ
きゃべつ => 野菜

それでは{what_is_this}はなんですか？
"""

for chunk in ollama.response_from_message_stream(message):
    print(chunk, end="", flush=True)

# カテゴライズ
# ある文章をカテゴリーに分類することで、その文章の内容を理解しやすくすることができます


# フィルタリング
# ある文章をフィルタリングすることで、その文章の内容を理解しやすくすることができます







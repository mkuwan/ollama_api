# Zero-Shot Prompting 
# つまり普通のプロンプトです　Q&Aの例文を書いて、それに対して回答を求める

from ollama_chat import OllamaChatMessage
import time

ollama = OllamaChatMessage(second=0.01)


message = "zero-shot promptについて説明してください"
for chunk in ollama.response_from_message_stream(message):
    # # 1文字ずつ表示
    # for char in chunk:
    #     print(char, end="", flush=True)
    #     time.sleep(0.2)
    print(chunk, end="", flush=True)
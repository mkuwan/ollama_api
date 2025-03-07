# Zero-Shot Prompting 
# つまり普通のプロンプトです

from ollama_chat import OllamaChatMessage
import time

ollama = OllamaChatMessage()

message = "zero-shot promptについて説明してください"
for chunk in ollama.response_from_message_stream(message):
    # # 1文字ずつ表示
    # for char in chunk:
    #     print(char, end="", flush=True)
    #     time.sleep(0.2)
    print(chunk, end="", flush=True)
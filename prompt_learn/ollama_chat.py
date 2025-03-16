from ollama import chat
from ollama import ChatResponse
import time


class OllamaChatMessage:
    def __init__(self, model = "llama3.2", second: float = 0.01):
        # modelが文字列で指定されている場合はそのままmodelに代入
        if isinstance(model, str) and model != "":
            self.model = model

        self.second = second
        if second > 0 and second < 0.1:
            self.second = second
        elif second > 0.1:
            self.second = 0.1
        elif second < 0:
            self.second = 0.0
        else:
            self.second = 0.0
        

    def response_from_message(self, message: str) -> ChatResponse:
        response: ChatResponse = chat(
            model=self.model,
            messages=[
                {
                    'role': 'user',
                    'content': message,
                }
            ], 
            stream=False,
        )
        
        return response.message.content


    def response_from_message_stream(self, message: str):      

        response: ChatResponse = chat(
            model=self.model,
            messages=[
                {
                    'role': 'user',
                    'content': message,
                }
            ], 
            stream=True,
        )
        
        for chunk in response:
            # yield chunk['message']['content']
            for char in chunk['message']['content']:
                time.sleep(self.second)
                yield char
            


if __name__ == '__main__':
    ollama = OllamaChatMessage()

    message = "3 * 12 - 6 + 70 = ?"
    response = ollama.response_from_message(message)
    print(response)

    # 3 seconds delay
    time.sleep(3)
    
    print("Stream:")
    for chunk in ollama.response_from_message_stream(message):
        # print(chunk, end="", flush=True)
        # time.sleep(0.01)
        # 1文字ずつ表示
        for char in chunk:
            print(char, end="", flush=True)
            time.sleep(0.01)
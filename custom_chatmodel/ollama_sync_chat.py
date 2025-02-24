import requests
import json

API_SERVER_URL = "http://localhost:11434/api/chat"


def send_message(message):
    headers = {
        'Content-Type': 'application/json'
    }
    json_data = {
        # "model": "hf.co/mmnga/cyberagent-DeepSeek-R1-Distill-Qwen-14B-Japanese-gguf:latest",
        "model": "llama3.2",
        "messages": [{
            "role": "user",
            "content": message
        }]
    }

    response = requests.post(API_SERVER_URL, headers=headers, json=json_data)
    # response.raise_for_status()

    print("*" * 20)
    print(response.text.splitlines()[-1])
    print("*" * 20)

    return response.text


def format_response(response_text):
    messages = []
    for line in response_text.splitlines():
        response_json = json.loads(line)
        messages.append(response_json['message']['content'])
    combined_message = ''.join(messages)
    return combined_message


if __name__ == "__main__":
    message = "アジャイルについて300文字で教えてください"
    response_json = send_message(message)
    formatted_response = format_response(response_json)
    print(formatted_response)
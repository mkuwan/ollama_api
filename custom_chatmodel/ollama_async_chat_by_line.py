import requests
import json
import asyncio
import aiohttp

API_SERVER_URL = "http://localhost:11434/api/chat"

async def send_message_async(message):
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

    async with aiohttp.ClientSession() as session:
        async with session.post(API_SERVER_URL, headers=headers, json=json_data) as response:
            async for line in response.content:
                yield line.decode('utf-8')

async def format_response_async(message):
    async for response_text in send_message_async(message):
        response_json = json.loads(response_text)
        print(response_json['message']['content'], end='')

if __name__ == "__main__":
    message = "昔ながらの開発スタイルでウォーターフォールで行われているプロセスがあります。これをアジャイルに変革していきたいです。その方法を教えてください"
    asyncio.run(format_response_async(message))
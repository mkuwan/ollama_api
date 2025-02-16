import aiohttp
import asyncio
import json

API_SERVER_URL = "http://localhost:11434/api/chat"

async def send_message(session, message):
    headers = {
        'Content-Type': 'application/json'
    }
    json_data = {
        "model": "llama3.2",
        "messages": [{
            "role": "user",
            "content": message
        }]
    }

    async with session.post(API_SERVER_URL, headers=headers, json=json_data) as response:
        async for line in response.content:
            yield line.decode('utf-8')

async def format_response(response_stream):
    async for line in response_stream:
        response_json = json.loads(line)
        yield response_json['message']['content']

async def main():
    message = "昔ながらの開発スタイルでウォーターフォールで行われているプロセスがあります。これをアジャイルに変革していきたいです。その方法を教えてください"
    async with aiohttp.ClientSession() as session:
        response_stream = send_message(session, message)
        async for part in format_response(response_stream):
            print(part, end='')

if __name__ == "__main__":
    asyncio.run(main())
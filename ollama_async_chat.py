import requests
import json
import asyncio
import aiohttp

# APIサーバーのURL
# chatは文脈踏まえた対話
# messagesでメッセージを送ります listで複数のメッセージを送ることで対話を行います

API_SERVER_URL = "http://localhost:11434/api/chat"

# 非同期でメッセージを送信する関数
async def send_message_async(message):
    headers = {
        'Content-Type': 'application/json'  # リクエストのヘッダー
    }
    json_data = {
        "model": "llama3.2",    # 使用するモデル
        "messages": [{
            "role": "user",  # メッセージの役割（ユーザー）
            "content": message  # ユーザーからのメッセージ内容
        }]
    }

    # 非同期でHTTPセッションを作成
    async with aiohttp.ClientSession() as session:
        # 非同期でPOSTリクエストを送信
        async with session.post(API_SERVER_URL, headers=headers, json=json_data) as response:
            # レスポンスの内容を非同期で1行ずつ処理
            async for line in response.content:
                yield line.decode('utf-8')  # レスポンスの行をデコードして返す


# 非同期でレスポンスをフォーマットする関数
async def format_response_async(message):
    # 非同期でメッセージを送信し、レスポンスを受け取る
    async for response_text in send_message_async(message):
        response_json = json.loads(response_text)  # レスポンスをJSONとして読み込む
        # レスポンスの内容を1文字ずつ出力
        for char in response_json['message']['content']:
            print(char, end='', flush=True)  # 文字を出力してフラッシュする


if __name__ == "__main__":
    # 送信するメッセージ
    message = "アジャイルついて教えてください。"
    # 非同期関数を実行
    asyncio.run(format_response_async(message))
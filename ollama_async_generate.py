import json
import asyncio
import aiohttp

# generate は単発の質問 
# promptで質問を送ります

# APIサーバーのURL
API_SERVER_URL = "http://localhost:11434/api/generate"

# 非同期でメッセージを送信する関数
async def send_message_async(prompt):
    headers = {
        'Content-Type': 'application/json'  # リクエストのヘッダー
    }
    json_data = {
        "model": "llama3.2",  # 使用するモデル
        "prompt": prompt,  # ユーザーからのプロンプト内容
        "stream": True  # ストリーミングを有効にする
    }

    # 非同期でHTTPセッションを作成
    async with aiohttp.ClientSession() as session:
        # 非同期でPOSTリクエストを送信
        async with session.post(API_SERVER_URL, headers=headers, json=json_data) as response:
            # レスポンスの内容を非同期で1行ずつ処理
            async for line in response.content:
                yield line.decode('utf-8')  # レスポンスの行をデコードして返す

# 非同期でレスポンスをフォーマットする関数
async def format_response_async(prompt):
    # 非同期でメッセージを送信し、レスポンスを受け取る
    async for response_text in send_message_async(prompt):
        response_json = json.loads(response_text)  # レスポンスをJSONとして読み込む
        # レスポンスの内容を1文字ずつ出力
        for char in response_json['response']:
            print(char, end='', flush=True)  # 文字を出力してフラッシュする

if __name__ == "__main__":
    # 送信するプロンプト
    prompt = "AIの使い方を教えてください。"
    # 非同期関数を実行
    asyncio.run(format_response_async(prompt))
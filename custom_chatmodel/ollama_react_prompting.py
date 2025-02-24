import requests
import json
import asyncio
import aiohttp

# APIサーバーのURL
API_SERVER_URL = "http://localhost:11434/api/chat"

# 非同期でメッセージを送信する関数
async def send_message_async(message):
    headers = {
        'Content-Type': 'application/json'  # リクエストのヘッダー
    }
    json_data = {
        "model": "llama3.2",  # 使用するモデル
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
    try:
        # 非同期でメッセージを送信し、レスポンスを受け取る
        async for response_text in send_message_async(message):
            response_json = json.loads(response_text)  # レスポンスをJSONとして読み込む
            # レスポンスの内容を1文字ずつ出力
            for char in response_json['message']['content']:
                print(char, end='', flush=True)  # 文字を出力してフラッシュする
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        

if __name__ == "__main__":
    # ReActプロンプトのサンプル例
    message = """
    あなたは知識豊富なアシスタントです。以下の質問に答えてください。

    質問: 日本の首都はどこですか？
    回答: 日本の首都は東京です。

    質問: 富士山の高さはどれくらいですか？
    回答: 富士山の高さは約3776メートルです。

    質問: 日本の人口はどれくらいですか？
    回答: 日本の人口は約1億2600万人です。

    質問: 日本の通貨は何ですか？
    回答: 日本の通貨は円です。

    質問: 日本の国旗の色は何ですか？
    回答: 日本の国旗は白地に赤い円です。

    質問: 日本の首相は誰ですか？
    回答: 現在の日本の首相は岸田文雄です。

    質問: 日本の主要な輸出品は何ですか？
    回答: 日本の主要な輸出品は自動車、電子機器、機械などです。

    質問: 日本の主要な観光地はどこですか？
    回答: 日本の主要な観光地には東京、京都、大阪、富士山、北海道などがあります。

    質問: 日本の主要な産業は何ですか？
    回答: 日本の主要な産業は自動車産業、電子産業、機械産業などです。

    質問: 日本の主要な宗教は何ですか？
    回答: 日本の主要な宗教は仏教と神道です。
    """

    # 非同期関数を実行
    asyncio.run(format_response_async(message))
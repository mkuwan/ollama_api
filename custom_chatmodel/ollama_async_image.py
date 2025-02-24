import json
import asyncio
import aiohttp
import os
import base64

# APIサーバーのURL
API_SERVER_URL = "http://localhost:11434/api/generate"

# 非同期で画像を送信する関数
async def send_image_async(image_path):
    headers = {
        'Content-Type': 'application/json'  # リクエストのヘッダー
    }
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    json_data = {
        "model": "llava",  # 使用するモデル
        "prompt": "explain this image",  # プロンプト
        "images": [image_data],  # base64エンコードされた画像データ
        "stream": False  # ストリーミングを無効にする
    }

    # 非同期でHTTPセッションを作成
    async with aiohttp.ClientSession() as session:
        # 非同期でPOSTリクエストを送信
        async with session.post(API_SERVER_URL, headers=headers, json=json_data) as response:
            return await response.json()  # レスポンスをJSONとして返す

# 非同期で翻訳を送信する関数
# llavaモデルは日本語が苦手なため、英語で出力してから日本語に翻訳する
async def send_translation_async(text):
    headers = {
        'Content-Type': 'application/json'  # リクエストのヘッダー
    }
    json_data = {
        "model": "llama3.2",  # 使用するモデル
        "prompt": f"Translate the following text to Japanese: {text}",  # 翻訳プロンプト
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
async def format_response_async(image_path):
    response_json = await send_image_async(image_path)  # 非同期でメッセージを送信し、レスポンスを受け取る
    english_response = response_json['response']  # 英語のレスポンスを取得
    print("English Response:", english_response)  # 英語のレスポンスを出力

    print("\nJapanese Translation:")
    # 非同期で翻訳を送信し、レスポンスを受け取る
    async for response_text in send_translation_async(english_response):
        response_json = json.loads(response_text)  # レスポンスをJSONとして読み込む
        # 日本語の翻訳を1文字ずつ非同期で出力
        for char in response_json['response']:
            print(char, end='', flush=True)  # 文字を出力してフラッシュする
            # await asyncio.sleep(0.03)  # 少し待機してから次の文字を出力

if __name__ == "__main__":
    # 画像フォルダ内の画像ファイルを取得
    image_folder = "images"
    image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]

    # 各画像について説明を取得
    for image_path in image_files:
        print(f"Processing image: {image_path}")
        asyncio.run(format_response_async(image_path))
        print("\n")

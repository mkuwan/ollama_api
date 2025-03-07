# prompt-chaining

# Peer Worker Platformがこれに該当すると思います。


from ollama_chat import OllamaChatMessage

ollama = OllamaChatMessage(model="llama3.1", second=0.04)


prompt01 = """
Q: あるクラスに20人の生徒がいます。そのうち12人が数学のテストに合格しました。合格率は何パーセントですか？
"""

print(f"{"*" * 10} Prompt 01 {"*" * 10}")
response01 = ""
for chunk in ollama.response_from_message_stream(prompt01):
    print(chunk, end="", flush=True)
    response01 += chunk

prompt02 = f"""
{prompt01} に対して、あなたの最初の回答は {response01} でした。

回答の仕方を考えてみましょう。
A: 一歩ずつ考えてみましょう。
1. クラスには20人の生徒がいます。
2. そのうち12人がテストに合格しました。
3. 合格率は (12 / 20) * 100 です。
4. 計算すると、合格率は 60% です。
あなたの思考プロセスと回答を確認してください。
"""

print()
print(f"{"*" * 10} Prompt 02 {"*" * 10}")
response02 = ""
for chunk in ollama.response_from_message_stream(prompt02):
    print(chunk, end="", flush=True)
    response02 += chunk

prompt03 = f"""
{prompt01}
{prompt02}
{response02}

それでは、次の問題を解いてください。

Q: そのクラスの合格率が60%であることがわかりました。次に、合格した生徒のうち、さらに8人が追加の課題を完了しました。追加の課題を完了した生徒の割合は何パーセントですか？
A: 一歩ずつ考えてみましょう。
1. 合格した生徒は12人です。
2. そのうち8人が追加の課題を完了しました。
3. 追加の課題を完了した生徒の割合は (8 / 12) * 100 です。
4. 計算すると、割合は何%でしょうか(小数点がある場合小数点以下2桁で四捨五入してください)。
"""

print()
print(f"{"*" * 10} Prompt 03 {"*" * 10}")
response03 = ""
for chunk in ollama.response_from_message_stream(prompt03):
    print(chunk, end="", flush=True)
    response03 += chunk

prompt04 = f"""
これまでの問題を通じて、合格率と追加の課題の完了率について考えることができました。

これまでの問題と回答を振り返ると以下の通りです。
1. {prompt01}
2. {response01}
3. {prompt02}
4. {response02}
5. {prompt03}
6. {response03}

それでは、次の問題に取り組んでください。

Q: そのクラス不合格率は何%？
"""

print()
print(f"{"*" * 10} Prompt 04 {"*" * 10}")
response04 = ""
for chunk in ollama.response_from_message_stream(prompt04):
    print(chunk, end="", flush=True)
    response04 += chunk
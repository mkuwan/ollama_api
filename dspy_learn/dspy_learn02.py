# https://www.jiang.jp/posts/20240223_dspy_introduce/

# DSPyはStanford大学が開発したLLMのプロンプトとウェイトを自動的に最適化できるフレームワークです。
# DSPyは概念的にPyTorchに似ています。
# プログラムでモジュールを定義し、使うPromptをモデルのウェイトとして扱い、学習データで最適なPromptを学習させます。
# DSPyの中ではこの学習のステップを「Compile」と呼んでいます。
# この方法の良い点としてはPromptが裏側に隠れており、変動があるときには表の定義を変え、
# 再度コンパイルするだけで、プログラムが自動的に最適化されます。
# 自分で一々Promptをチューニングしなくでも良いことです。


# 今回の説明に使うデータはアマゾンのレビューのポジネガ分析データです。 
# ポジネガのラベルは数字で表現され、0はポジティブ、1はニュートラル、2はネガティブです。
#  学習データとテストデータをそれぞれ50件ずつサンプリングしました。
import datasets
import warnings
import dspy
from litellm import completion
import pprint as pp

# warnings.filterwarnings('ignore')

# dataset = datasets.load_dataset("tyqiangz/multilingual-sentiments", "japanese")
# train_set = dataset["train"].shuffle(seed=50).select(range(50))
# test_set = dataset["test"].shuffle(seed=50).select(range(50))

# def print_with_newline(text, max_length=40):
#     if len(text) <= max_length:
#         print(text)
#     else:
#         print(text[:max_length])
#         print_with_newline(text[max_length:], max_length)

# sample = train_set[0]
# print("===レビュー===")

# print_with_newline(sample["text"])
# print("===ラベル===")
# print(sample["label"])


lm = dspy.LM(
        model='ollama/llama3.2',
        api_key='ollama',
        api_base="http://localhost:11434",
        max_tokens=2500,
        temperature=0.1,
        # num_retries=3
    )
dspy.configure(lm = lm)

# sentiment_classifier = dspy.Predict('sentence -> sentiment')
# prediction = sentiment_classifier(sentence="博多ラーメンがめちゃくちゃまずい")

# # pp.pprint(prediction)

# lm.inspect_history(n=1)

class BasicSentimentClassifier(dspy.Signature):
    """アマゾンの商品レビューに対する感情分析を行い、数字の{0, 1, 2} をアウトプットする。 0: ポジティブ, 1: ニュートラル, 2: ネガティブ"""

    text = dspy.InputField(desc="アマゾンの商品レビュー")
    answer = dspy.OutputField(
        desc="数字で表現した感情分析の結果",
    )
classify = dspy.ChainOfThought(BasicSentimentClassifier)
classify(text="博多ラーメンがめちゃくちゃうまいです。今回は一風堂を買いました")
lm.inspect_history(n=1)
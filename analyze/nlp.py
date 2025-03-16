## pip install pandas scikit-learn textblob

import pandas as pd
from ollama import chat
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation



# 顧客フィードバックデータの収集
feedback_data = {
    "アンケート結果": [
        {"質問": "製品の品質についてどう思いますか？", "回答": "非常に満足（30%）、満足（40%）、普通（20%）、不満（10%）", "コメント": [
            "製品のデザインが気に入っていますが、耐久性に不安があります。",
            "音質が良いが、バッテリーの持ちが悪いです。",
            "素材が高品質で、長持ちしそうです。",
            "細部の仕上げが甘いと感じました。",
            "期待以上の性能で満足しています。"
        ]},
        {"質問": "顧客対応についてどう思いますか？", "回答": "非常に満足（25%）、満足（35%）、普通（25%）、不満（15%）", "コメント": [
            "対応が迅速で助かりました。",
            "サポートの対応が冷たく感じました。",
            "親切で丁寧な対応に感謝しています。",
            "問い合わせに対する返答が遅かったです。",
            "問題解決までのプロセスがスムーズでした。"
        ]},
        {"質問": "配送のスピードについてどう思いますか？", "回答": "非常に満足（20%）、満足（30%）、普通（30%）、不満（20%）", "コメント": [
            "配送が予定より早くて驚きました。",
            "配送が遅れて困りました。",
            "迅速な配送に満足しています。",
            "配送中に商品が破損していました。",
            "配送状況の追跡ができて安心しました。"
        ]},
        {"質問": "製品の価格についてどう思いますか？", "回答": "非常に満足（15%）、満足（25%）、普通（40%）、不満（20%）", "コメント": [
            "価格が高いが、品質に見合っている。",
            "もう少し手頃な価格であれば嬉しい。",
            "コストパフォーマンスが良いと感じました。",
            "割引があればもっと良いです。",
            "価格に対して機能が充実しています。"
        ]}
    ],
    "オンラインレビュー": [
        "製品の品質は良いが、カスタマーサポートが遅い。",
        "配送が遅れて困った。改善してほしい。",
        "製品は期待通りだったが、対応が冷たい感じがした。",
        "新しいモデルの機能が素晴らしいが、価格が高い。",
        "購入後のサポートが充実していない。",
        "デザインがスタイリッシュで気に入っています。",
        "操作が簡単で、すぐに使いこなせました。",
        "説明書がわかりにくい。",
        "カスタマーサポートの対応が遅い。",
        "色のバリエーションが少ない。",
        "性能が期待以上で満足しています。",
        "動作が遅いと感じることがあります。",
        "サポートの対応が冷たく感じました。",
        "価格が高いので、購入を迷いました。",
        "友人に勧められて購入しましたが、満足しています。"
    ],
    "ソーシャルメディアのコメント": [
        "新しい製品が気に入ったけど、配送が遅かった。",
        "サポートに問い合わせたけど、返事が遅かった。",
        "品質は良いけど、もう少し対応が良ければ完璧。",
        "友人に勧められて購入しましたが、満足しています。",
        "価格が高いので、購入を迷いました。",
        "新しい製品のデザインが気に入っています。",
        "サポートに問い合わせたけど、対応が遅かった。",
        "使いやすさは良いけど、説明書がわかりにくい。",
        "デザインがスタイリッシュで、友人にも勧めました。",
        "配送が遅れて困りました。",
        "購入後のサポートが充実していない。",
        "操作が簡単で、すぐに使いこなせました。",
        "説明書がわかりにくい。",
        "カスタマーサポートの対応が遅い。",
        "色のバリエーションが少ない。",
        "性能が期待以上で満足しています。",
        "動作が遅いと感じることがあります。",
        "サポートの対応が冷たく感じました。",
        "価格が高いので、購入を迷いました。",
        "友人に勧められて購入しましたが、満足しています。"
    ]
}

# データ前処理
def preprocess_feedback(feedback_data):
    comments = []
    for category in feedback_data.values():
        for item in category:
            if isinstance(item, dict):
                comments.extend(item["コメント"])
            else:
                comments.append(item)
    return comments

comments = preprocess_feedback(feedback_data)

sys_prompt = """
# ユーザーのコメントのセンチメンタル分析を行います。
# positive, neutral, negative のいずれかを返します。
# 余計な文字はつけず、必ずこの3単語の英文字のみで返してください。
# スペルミスに注意してください。単語の省略はしないでください。
# 余計な文字(-, _)が含まれないように注意してください。
"""
# 自然言語処理: 感情分析
def sentiment_analysis(comments):
    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    for comment in comments:
        response = chat(
            model="llama3.2", 
            messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": comment}],
            options={'temperature': 0.0}
            )
        print(response.message)
        sentiment = response.message.content
        if "positive" in sentiment:
            sentiments["positive"] += 1
        elif "neutral" in sentiment:
            sentiments["neutral"] += 1
        elif "negative" in sentiment:
            sentiments["negative"] += 1
        else:
            print(f"Error: Invalid sentiment - {sentiment}")
    return sentiments

sentiments = sentiment_analysis(comments)

# 自然言語処理: トピックモデリング
def topic_modeling(comments, num_topics=5):
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(comments)
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(X)
    topics = lda.components_
    feature_names = vectorizer.get_feature_names_out()
    topic_keywords = []
    for topic in topics:
        keywords = [feature_names[i] for i in topic.argsort()[:-11:-1]]
        topic_keywords.append(keywords)
    return topic_keywords

topic_keywords = topic_modeling(comments)

# 自然言語処理: キーワード抽出
def keyword_extraction(comments):
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(comments)
    keywords = vectorizer.get_feature_names_out()
    keyword_counts = X.sum(axis=0).tolist()[0]
    keyword_freq = dict(zip(keywords, keyword_counts))
    return keyword_freq

# キーワード抽出の実行
keyword_freq = keyword_extraction(comments)


# 結果の表示
print("Sentiments:", sentiments)
print("Topic Keywords:", topic_keywords)
print("Keyword Frequency:", keyword_freq)

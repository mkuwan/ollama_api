# RAG From Scratch

https://github.com/langchain-ai/rag-from-scratch

LLM（大規模言語モデル）は、大量ではあるものの固定されたデータコーパスで訓練されており、プライベートな情報や最新の情報について推論する能力が制限されています。この制約を緩和する方法の一つとしてファインチューニングがありますが、事実の記憶にはあまり適しておらず、コストがかかる場合があります。そこで、外部データソースから取得したドキュメントを使用して、LLMの生成をインコンテキスト学習で補強する「検索強化生成（RAG）」が、LLMの知識ベースを拡張するための人気かつ強力なメカニズムとして登場しました。これらのノートブックは、インデックス作成、検索、生成の基本から始めて、RAGをゼロから理解するためのビデオプレイリストに対応しています。

![alt text](rag_from_scratch.png)


この図では、Indexing・Query Translation・Routing・Query Construction・Retrieval・Generationという6ヵ所に、それぞれさまざまな手法があることがまとめられています。もちろん手法によってはこれらの複数ヵ所に工夫を施すものもあります。しかし、このように拡張できるポイントを整理することで、さまざまな手法を比較したり理解したりしやすくなります。 他にも、RAGの拡張ポイントをまとめた論文の例として、次の2つがあります。 
- Gao et al. （2023）「Retrieval-Augmented Generation for Large Language Models: A Survey」https://arxiv.org/abs/2312.10997 
- Akkiraju et al. （2024）「FACTS About Building Retrieval Augmented Generation-based Chatbots」https://arxiv.org/abs/2407.07858


西見 公宏; 吉田 真吾; 大嶋 勇樹. LangChainとLangGraphによるRAG・AIエージェント［実践］入門 エンジニア選書 (pp.298-299). 株式会社技術評論社. Kindle 版. 

import dspy
from litellm import completion
import pprint as pp

# https://dspy.ai/#__tabbed_1_4
lm = dspy.LM('ollama/llama3.2',
              api_key='ollama',
              api_base="http://localhost:11434")

dspy.configure(lm=lm)

# https://dspy.ai/#__tabbed_1_4
# Math
math = dspy.ChainOfThought("question -> answer: float")
response = math(question="Two dice are tossed. What is the probability that the sum equals two?")
print(f"{"*" * 10} Math {"*" * 10}")
pp.pprint(response)


# RAG
def search_wikipedia(query: str) -> list[str]:
    results = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')(query, k=3)
    response = [x['text'] for x in results]
    print(f"{"*" * 10} search_wikipedia {"*" * 10}")
    pp.pprint(response)
    return response

rag = dspy.ChainOfThought('context, question -> response')

question = "What's the name of the castle that David Gregory inherited?"
response = rag(context=search_wikipedia(question), question=question)
print(f"{"*" * 10} RAG {"*" * 10}")
pp.pprint(response)

print(f"{"*" * 10} inspect_history {"*" * 10}")
lm.inspect_history(n=1)
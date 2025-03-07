# https://python.langchain.com/docs/integrations/chat/ollama/
# ChatOllamaはBaseChatModelを継承しています
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.prompts import ChatPromptTemplate
from typing import List
from langchain_core.tools import tool


def tool_calling():
    print(f"{"*" * 10} Tool Calling {"*" * 10}")

    @tool
    def validate_user(user_id: int, address: List[str]) -> bool:
        """Validate user using historical addresses.

        Args:
            user_id (int): the user ID.
            address (List[str]): Previous addresses as a list of strings.

        Returns:
            bool: result of the validation.
        """
        print(f"validate_user User ID: {user_id}")
        return True
    
    chatModel = ChatOllama(
        model="llama3.2",
        temperature=0,
        base_url="http://localhost:11434",
        # other params...
    ).bind_tools([validate_user])

    result = chatModel.invoke(
        "Could you validate user 123? They previously lived at "
        "123 Fake St in Boston MA and 234 Pretend Boulevard in "
        "Houston TX."
    )

    print(result)
    # resultの中身は以下のようになります
        # content='' 
        # additional_kwargs={} 
        # response_metadata={
        #     'model': 'llama3.2', 
        #     'created_at': '2025-02-18T10:55:25.735432705Z', 
        #     'done': True, 
        #     'done_reason': 'stop', 
        #     'total_duration': 574655661, 
        #     'load_duration': 15862375, 
        #     'prompt_eval_count': 236, 
        #     'prompt_eval_duration': 3000000, 
        #     'eval_count': 34, 
        #     'eval_duration': 554000000, 
        #     'message': Message(
        #         role='assistant', 
        #         content='', 
        #         images=None, 
        #         tool_calls=None
        #     )
        # } 
        # id='run-2746eb4d-45d1-4581-bf06-53d8bf682a47-0' 
        # tool_calls=[
        #     {
        #         'name': 'validate_user', 
        #         'args': {
        #             'address': ['123 Fake St', '234 Pretend Boulevard'], 
        #             'user_id': 123
        #         }, 
        #         'id': '7540d0f9-5792-4184-8e26-fbefba55e503', 
        #         'type': 'tool_call'
        #     }
        # ] 
        # usage_metadata={
        #     'input_tokens': 236, 
        #     'output_tokens': 34, 
        #     'total_tokens': 270
        # }

if __name__ == "__main__":
    tool_calling()

import asyncio
import aiohttp
import requests
import json
import time
from typing import Any, Dict, Iterator, List, Optional, AsyncIterator

from langchain_core.callbacks import (
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
)
from langchain_core.messages.ai import UsageMetadata
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from pydantic import Field

class OllamaChatModel(BaseChatModel):
    """A custom chat model that echoes the first `parrot_buffer_length` characters
    of the input.

    When contributing an implementation to LangChain, carefully document
    the model including the initialization parameters, include
    an example of how to initialize the model and include any relevant
    links to the underlying models documentation or API.

    Example:

        .. code-block:: python

            model = OllamaChatModel(parrot_buffer_length=2, model="bird-brain-001")
            result = model.invoke([HumanMessage(content="hello")])
            result = model.batch([[HumanMessage(content="hello")],
                                 [HumanMessage(content="world")]])
    """

    model_name: str = Field(alias="model")
    end_point: str = Field(alias="end_point")
    """The name of the model"""
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout: Optional[int] = None
    stop: Optional[List[str]] = None
    max_retries: int = 2

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Override the _generate method to implement the chat model logic.

        This can be a call to an API, a call to a local model, or any other
        implementation that generates a response to the input prompt.

        Args:
            messages: the prompt composed of a list of messages.
            stop: a list of strings on which the model should stop generating.
                  If generation stops due to a stop token, the stop token itself
                  SHOULD BE INCLUDED as part of the output. This is not enforced
                  across models right now, but it's a good practice to follow since
                  it makes it much easier to parse the output of the model
                  downstream and understand why generation stopped.
            run_manager: A run manager with callbacks for the LLM.
        """

        print("Generating")

        # Replace this with actual logic to generate a response from a list of messages.
        last_message = messages[-1]
        message_contents = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                message_contents.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                message_contents.append({"role": "assistant", "content": msg.content})

        headers = {
            'Content-Type': 'application/json'
        }
        json_data = {
            "model": self.model_name,
            "messages": message_contents,
            "stream": False
        }

        response = requests.post(self.end_point, headers=headers, json=json_data)
        messages = []
        for line in response.text.splitlines():
            response_json = json.loads(line)
            messages.append(response_json['message']['content'])
        combined_message = ''.join(messages)

        meta_data = response.text.splitlines()[-1]
        meta_json = json.loads(meta_data)
        ct_input_tokens = meta_json.get("prompt_eval_count", 0)
        ct_output_tokens = meta_json.get("eval_count", 0)

        message = AIMessage(
            content=combined_message,
            additional_kwargs={},  # Used to add additional payload to the message
            response_metadata={  # Use for response metadata
                "time_in_seconds": 3,
            },
            usage_metadata={
                "input_tokens": ct_input_tokens,
                "output_tokens": ct_output_tokens,
                "total_tokens": ct_input_tokens + ct_output_tokens,
            },
        )

        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Stream the output of the model.

        This method should be implemented if the model can generate output
        in a streaming fashion. If the model does not support streaming,
        do not implement it. In that case streaming requests will be automatically
        handled by the _generate method.

        Args:
            messages: the prompt composed of a list of messages.
            stop: a list of strings on which the model should stop generating.
                  If generation stops due to a stop token, the stop token itself
                  SHOULD BE INCLUDED as part of the output. This is not enforced
                  across models right now, but it's a good practice to follow since
                  it makes it much easier to parse the output of the model
                  downstream and understand why generation stopped.
            run_manager: A run manager with callbacks for the LLM.
        """

        print("Streaming")

        headers = {
            'Content-Type': 'application/json'  # リクエストのヘッダー
        }
        message_contents = [
            {"role": "user", "content": msg.content} if isinstance(msg, HumanMessage) else {"role": "assistant", "content": msg.content}
            for msg in messages
        ]
        json_data = {
            "model": self.model_name,
            "messages": message_contents,
            "stream": True
        }

        response = requests.post(self.end_point, headers=headers, json=json_data)

        

        for line in response.iter_lines(decode_unicode=True):
            response_json = json.loads(line)
            content = response_json['message']['content']
            time.sleep(0.01)
            usage_metadata = UsageMetadata(
                {
                    "input_tokens": len(content),
                    "output_tokens": 1,
                    "total_tokens": len(content) + 1,
                }
            )
            
            chunk = ChatGenerationChunk(
                message=AIMessageChunk(
                    content=content, 
                    usage_metadata=usage_metadata)
                )
            if run_manager:
                run_manager.on_llm_new_token(content, chunk=chunk)
            yield chunk


    # async def _astream(
    #     self,
    #     messages: List[BaseMessage],
    #     stop: Optional[List[str]] = None,
    #     run_manager: Optional[CallbackManagerForLLMRun] = None,
    #     **kwargs: Any,
    # ) -> AsyncIterator[ChatGenerationChunk]:
    #     """Async stream the output of the model.

    #     This method should be implemented if the model can generate output
    #     in a streaming fashion. If the model does not support streaming,
    #     do not implement it. In that case streaming requests will be automatically
    #     handled by the _generate method.

    #     Args:
    #         messages: the prompt composed of a list of messages.
    #         stop: a list of strings on which the model should stop generating.
    #               If generation stops due to a stop token, the stop token itself
    #               SHOULD BE INCLUDED as part of the output. This is not enforced
    #               across models right now, but it's a good practice to follow since
    #               it makes it much easier to parse the output of the model
    #               downstream and understand why generation stopped.
    #         run_manager: A run manager with callbacks for the LLM.
    #     """

    #     print("Async Streaming")

    #     async def send_message_async():
    #         headers = {
    #             'Content-Type': 'application/json'  # リクエストのヘッダー
    #         }
    #         message_contents = [
    #             {"role": "user", "content": msg.content} if isinstance(msg, HumanMessage) else {"role": "assistant", "content": msg.content}
    #             for msg in messages
    #         ]
    #         json_data = {
    #             "model": self.model_name,
    #             "messages": message_contents,
    #             "stream": True
    #         }

    #         async with aiohttp.ClientSession() as session:
    #             async with session.post(self.end_point, headers=headers, json=json_data) as response:
    #                 async for line in response.content:
    #                     yield line.decode('utf-8')

    #     async for response_text in send_message_async():
    #         response_json = json.loads(response_text)
    #         # レスポンスの内容を1文字ずつ出力
    #         content = response_json['message']['content']
    #         usage_metadata = UsageMetadata(
    #             {
    #                 "input_tokens": len(content),
    #                 "output_tokens": 1,
    #                 "total_tokens": len(content) + 1,
    #             }
    #         )
    #         chunk = ChatGenerationChunk(
    #             message=AIMessageChunk(content=content, usage_metadata=usage_metadata)
    #         )
    #         if run_manager:
    #             await run_manager.on_llm_new_token(content, chunk=chunk)
    #         yield chunk


    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "echoing-chat-model-advanced"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters.

        This information is used by the LangChain callback system, which
        is used for tracing purposes make it possible to monitor LLMs.
        """
        return {
            "model_name": self.model_name,
            "end_point": self.end_point,
        }

async def main():
    API_CHAT = "http://localhost:11434/api/chat"
    model = OllamaChatModel(model="llama3.2", end_point=API_CHAT)
    messages = [
        HumanMessage(content="こんにちは"),
        AIMessage(content="こんにちは！何が聞きたいですか？"),
        HumanMessage(content="アジャイルについて300文字で教えてください"),
    ]
    
    print("*"*10, "generateを呼び出す", "*"*10)
    response = model.invoke(messages)
    print(response.content, end='', flush=True)


    print("*"*10, "streamを呼び出す", "*"*10)
    for chunk in model.stream(messages):
        print(chunk.content, end='', flush=True)


    print("*"*10, "astreamを呼び出す", "*"*10)
    async for chunk in model.astream(messages):
        print(chunk.content, end='', flush=True)

if __name__ == "__main__":
    asyncio.run(main())


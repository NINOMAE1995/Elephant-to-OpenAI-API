import httpx
from fastapi import Request

from adapters.base_adapter import BaseAdapter


class ElephantAdapter(BaseAdapter):
    def __init__(self, proxy):
        self.last_time = None
        if proxy:
            self.proxies = {
                'http://': proxy,
                'https://': proxy,
            }
        else:
            self.proxies = None

    @staticmethod
    def convert_data(chatbot_id, conversation_id, messages):
        elephant_messages = messages[:-1]
        return {
            'chatbot_id': chatbot_id,
            'conversation_id': conversation_id,
            'messages': elephant_messages,
            'query': messages[-1]['content'],
        }

    async def chat(self, request: Request):
        openai_params = await request.json()
        headers = request.headers
        stream = openai_params.get("stream")
        messages = openai_params.get("messages")
        # model = openai_params.get("model")
        model = "gpt-4-turbo"

        chatbot_id = self.get_request_api_key(headers)

        async with httpx.AsyncClient(http2=False, timeout=120.0, proxies=self.proxies) as client:

            headers = {
                'Origin': 'https://bot.elephant.ai',
                'Referer': 'https://bot.elephant.ai/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
            }

            response = await client.post(
                'https://embed.elephant.ai/api/v1/create-conversation',
                headers=headers,
                json=
                {
                    'chatbot_id': chatbot_id,
                    'source': 'iFrame',
                },
            )
            if response.is_error:
                raise Exception(f"Error: {response.status_code}")
            conversation_id = response.json()['conversation_id']
            print('conversation_id:', conversation_id)

            json_data = self.convert_data(chatbot_id=chatbot_id, conversation_id=conversation_id, messages=messages)
            print('json_data:', json_data)

            response = await client.post(
                url='https://embed.elephant.ai/api/v1/send-message',
                headers=headers,
                json=json_data,
            )
            if response.is_error:
                raise Exception(f"Error: {response.status_code}")

            result_json = response.json()
            print('result_json:', result_json)
            answer = result_json['answer']

            if not stream:
                yield self.to_openai_response(model, answer)
            else:
                yield self.to_openai_response_stream_begin(model=model)
                yield self.to_openai_response_stream(model=model, content=answer)
                yield self.to_openai_response_stream_end(model=model)
                yield "[DONE]"

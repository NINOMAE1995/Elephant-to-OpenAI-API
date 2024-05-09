# Elephant to OpenAI API

## 获取 Chatbot ID
从 [Elephant.ai](https://elephant.ai/) 创建机器人会生成 Chatbot ID

## 调用示例
```python
import openai

openai.api_base = "http://localhost:8000/v1"
# API Key 为 Chatbot ID
openai.api_key = "xxx-xxx-xxx-xxx-xxx"

response = openai.ChatCompletion.create(
    model='gpt-4-turbo',
    messages=[
        {'role': 'user', 'content': "hi"},
    ],
    temperature=1,
    stream=False
)

print(response)

```



[BILIBILI](https://space.bilibili.com/1485535) | [爱发电](https://afdian.net/a/ninomae)

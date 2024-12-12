from openai import AsyncOpenAI

from mywebrtcServer.config import AI_CONFIG

# 配置OpenAI
client = AsyncOpenAI(base_url=AI_CONFIG["base_url"],
                     api_key=AI_CONFIG["api_key"])


async def generate_summary(text: str) -> None:
    response = await client.chat.completions.create(model=AI_CONFIG["model"],
                                                    messages=[{
                                                        "role":
                                                        "system",
                                                        "content":
                                                        "请对以下内容进行总结："
                                                    }, {
                                                        "role": "user",
                                                        "content": text
                                                    }],
                                                    stream=True)

    async for chunk in response:
        yield chunk.choices[0].delta.content

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


# 详细总结
async def generate_detail_summary(text: str):
    print('成功开始')
    try:
        response = await client.chat.completions.create(
            model=AI_CONFIG["model"],
            messages=[{
                "role":
                "system",
                "content":
                """
                        请对以下内容进行详细的总结分析，要求：
                        1. 使用 Markdown 格式输出
                        2. 包含主要内容、关键点、背景信息等
                        3. 分点列出重要观点
                        4. 添加适当的标题和分隔符
                        5. 可以适当延伸想象，描述清楚场景。想象一下分别在某个时间段，物品处于拍摄者的什么方位。这一点可以模拟场景：
                            用户是一个盲人，其他人拍摄视频分享给他，你需要在描述的同时让用户对物体的空间位置有所感知。
                        
                    """
            }, {
                "role": "user",
                "content": text
            }],
            stream=True)
        print('成功反应', response)
        async for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except Exception as e:
        print('API 调用报错', e)
        return

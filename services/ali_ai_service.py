import dashscope
import os
from fastapi import HTTPException, Response
from fastapi.responses import StreamingResponse

# 全局对话上下文，用于存储对话历史
message = []


# 读取本地文件
def read_audio_file(file_path: str):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, "rb") as file:
        content = file.read()
        print(f"文件内容类型: {type(content)}")  # 应该是 <class 'bytes'>
        return content


# 初次对话时调用
async def transcribe_audio_ali(file_path: str):
    global message
    message = [{
        "role":
        "user",
        "content": [
            {
                "audio": file_path
            },
            {
                "text":
                "请帮我识别这个视频内的全部对话内容，我们将基于这些对话内容进行后续的问答，因此我希望你能理解内容后给出一句简短的引导语。例如：似乎你正在谈论XXX问题，我了解到xxxx，你可以询问我关于xxx的问题。",
                # "text": "请简要描述这段对话的内容和情况。",
            }
        ]
    }]

    response = dashscope.MultiModalConversation.call(
        model="qwen-audio-turbo-latest",
        messages=message,
        stream=True,
        incremental_output=True,
        result_format="message")
    # for chunk in response:
    #     print(chunk)
    print('阿里云回复', response)

    async def generate_response():
        for chunk in response:
            # 检查 chunk 是否包含 choices
            if isinstance(chunk, dict) and 'choices' in chunk:
                # 遍历 choices，取出 message 的内容
                for choice in chunk['choices']:
                    if 'message' in choice and 'content' in choice['message']:
                        content_list = choice['message']['content']
                        # 遍历 content 列表并获取其中的 text 字段
                        for content in content_list:
                            if 'text' in content:
                                # 将文本内容编码成字节流返回
                                yield content['text'].encode('utf-8')
            else:
                # 如果 chunk 不符合预期格式，直接返回 chunk 内容
                yield str(chunk).encode('utf-8')

    return StreamingResponse(generate_response(),
                             media_type="text/plain;chatset=utf-8")

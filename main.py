from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
import os
import asyncio
from pydantic import BaseModel
from datetime import datetime
import tempfile
from typing import List, Optional

from mywebrtcServer.services.ai_service import ChatMessage, chat_with_model, generate_mindmap, generate_summary, generate_detail_summary
from mywebrtcServer.services.ali_ai_service import transcribe_audio_ali
from mywebrtcServer.services.stt_service import transcribe_audio, stop_transcription

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义一个全局变量来确定当前的转录任务
transcription_task = None


class TextRequest(BaseModel):
    text: str


# 转录接口
@app.post("/api/upload")
async def upload_file(file: UploadFile = File()):
    print('我的接口')
    global transcription_task
    try:
        # 先在本地存档上传的文件
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        # 创建转录任务
        transcription_task = asyncio.create_task(transcribe_audio(file_path))

        try:
            transcription = await transcription_task
            transcription_task = None
            # 如果转录成功了直接返回结果
            return {"transcription": transcription}

        except asyncio.CancelledError:
            # 确保任务被正确取消
            if not transcription_task.cancelled():
                transcription_task.cancel()
            transcription_task = None
            # 返回特定的状态码和信息
            return JSONResponse(status_code=499,
                                content={
                                    'status':
                                    'interrupted',
                                    "detail":
                                    "Transcription interrupted,asyncio error1"
                                })
    except asyncio.CancelledError:
        return JSONResponse(status_code=499,
                            content={
                                'status': 'interrupted',
                                "detail":
                                "Transcription interrupted,asyncio error"
                            })
    # 兜底错误
    except Exception as e:
        if transcription_task and not transcription_task.cancelled():
            transcription_task.cancel()
        transcription_task = None
        raise HTTPException(status_code=400, detail=str(e))


# 停止转录
@app.post("/api/stop-transcribe")
async def stopupload_file():
    global transcription_task
    try:
        # 如果当前有任务正在转录，那么需要中断他
        stop_transcription()

        if transcription_task is not None and not transcription_task.cancelled(
        ):
            transcription_task.cancel()
            try:
                asyncio.run(asyncio.wait_for(transcription_task, timeout=0.5))
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass  # 如果任务超时，忽略异常，任务可能仍在处理，但我们已经取消了它
            transcription_task = None
        return {"status": "success", "message": "Transcription stopped"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 生成总结
@app.post("/api/summary")
async def get_summary(request: TextRequest):

    async def generateFn():
        async for chunk in generate_summary(request.text):
            yield chunk

    return StreamingResponse(generateFn(), media_type="text/plain")


# 导出总结
class SummaryRequest(BaseModel):
    text: str
    type: str


@app.post("/api/export/summary")
async def export_summary(request: SummaryRequest):
    summary = request.text
    type = request.type
    try:
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"summary_{timestamp}_{type}.md"
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".md",
                                         delete=False) as temp_file:
            temp_file.write(summary.encode("utf-8"))
            temp_file.flush()

            return FileResponse(path=temp_file.name,
                                filename=filename,
                                media_type="text/markdown",
                                background=None)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 生成详细总结
class DetailSummaryRequest(BaseModel):
    text: str


@app.post("/api/detailSummary")
async def get_detail_summary(request: TextRequest):

    async def generateDetailFn():
        async for chunk in generate_detail_summary(request.text):
            yield chunk

    return StreamingResponse(generateDetailFn(), media_type="text/plain")


# 生成思维导图
@app.post("/api/mindmap")
async def get_mindmap(request: TextRequest):
    try:
        mindmap_json = await generate_mindmap(request.text)
        return {"mindmap": mindmap_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 对话


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context: str


@app.post("/api/chat")
async def chat(request: ChatRequest):

    async def generate():
        async for chunk in chat_with_model(request.messages, request.context):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/api/transcribe_ali")
async def chat(file: UploadFile = File()):
    print('我的接口')
    global transcription_task
    try:
        # 先在本地存档上传的文件
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        print('??')
        # 创建转录任务
        # transcription_task = asyncio.create_task(
        #     transcribe_audio_ali(file_path))
        # print('执行成功', transcription_task)
        try:
            
            transcription = await transcribe_audio_ali(file_path)
            
            # transcription = await transcription_task
            # transcription_task = None
            # 如果转录成功了直接返回结果
            # return {"transcription": transcription}
            
            return transcription
        
            # 不能这么写，这么写是直接返回了整个流式任务给前端，应该是要把内容处理成ReadableStream格式fanhui
            # return StreamingResponse(transcription_task,
            #                          media_type="text/plain; charset=utf-8")
            # async def generate_transcription_steam():
            #     async for chunk in transcribe_audio_ali(file_path):
            #         yield chunk  # 逐个数据块返回

            # return StreamingResponse(generate_transcription_steam(),
            #                          media_type="text/plain; charset=utf-8")

        except asyncio.CancelledError:
            # 确保任务被正确取消
            if not transcription_task.cancelled():
                transcription_task.cancel()
            transcription_task = None
            # 返回特定的状态码和信息
            return JSONResponse(status_code=499,
                                content={
                                    'status':
                                    'interrupted',
                                    "detail":
                                    "Transcription interrupted,asyncio error1"
                                })

    except asyncio.CancelledError:
        # 确保任务被正确取消
        if not transcription_task.cancelled():
            transcription_task.cancel()
        transcription_task = None
        # 返回特定的状态码和信息
        print('错误')
        return JSONResponse(status_code=499,
                            content={
                                'status':
                                'interrupted',
                                "detail":
                                "Transcription interrupted,asyncio error2"
                            })

    # 兜底错误
    except Exception as e:
        print('兜底错误')
        if transcription_task and not transcription_task.cancelled():
            transcription_task.cancel()
        transcription_task = None
        raise HTTPException(status_code=500, detail=str(e))

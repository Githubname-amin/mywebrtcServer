from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import asyncio

from mywebrtcServer.services.stt_service import transcribe_audio

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
                                    "Transcription interrupted,asyncio error"
                                })
    except asyncio.CancelledError:
        return JSONResponse(status_code=499,
                            content={
                                'status': 'interrupted',
                                "detail":
                                "Transcription interrupted,asyncio error"
                            })

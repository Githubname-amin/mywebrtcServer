from faster_whisper import WhisperModel
from mywebrtcServer.config import STT_CONFIG
import asyncio

model = WhisperModel(STT_CONFIG["whisper_model"], device="cuda")

# 全局变量来跟踪转录状态
should_stop = False
# 添加一个变量来跟踪当前转录的文件路径
current_file = None


async def transcribe_audio(file_path: str) -> list:
    global should_stop, current_file
    should_stop = False
    current_file = file_path
    try:
        segments_generator = model.transcribe(file_path, beam_size=10)
        transcription = []
        segments, info = segments_generator

        for segment in segments:
            if should_stop:
                current_file = None
                raise asyncio.CancelledError("Transcription cancelled")

            transcription.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })

            # 使用 await asyncio.sleep(0) 给事件循环一个机会来检查停止信号
            await asyncio.sleep(0)

        current_file = None
        return transcription

    except asyncio.CancelledError:
        should_stop = True
        current_file = None
        raise
    finally:
        should_stop = False
        current_file = None


# 用于外界终端当前转录任务
def stop_transcription() -> None:
    global should_stop
    should_stop = True

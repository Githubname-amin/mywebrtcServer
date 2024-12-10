# AI Service Configuration
# 通过配置文件来自定义 OpenAI (或支持OpenAI接口规范的)的模型。
AI_CONFIG = {
    "base_url": "https://open.bigmodel.cn/api/paas/v4/",
    "api_key":
    "7ecd4f215557fbfdd5c9f120ef703579.Qc14xlR8blQdGKj3",  # 替换为你的 API 密钥
    "model": "glm-4-flash"
}

# STT Service Configuration
# 通过配置文件来自定义 Whisper 模型的大小。模型大小会影响转录的准确度和速度：
# tiny: 最快但准确度最低
# base: 平衡速度和准确度
# small/medium: 更高的准确度，但需要更多资源
# large: 最高准确度，但需要最多资源
STT_CONFIG = {
    "whisper_model": "tiny"  # 可选值: tiny, base, small, medium, large
}

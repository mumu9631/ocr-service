"""
PaddleOCR食品标签识别服务
部署于Railway.app
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import base64
import io
from PIL import Image
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="食品标签OCR识别服务",
    description="基于PaddleOCR的预包装食品标签文字识别API",
    version="1.0.0"
)

# 配置CORS（允许小程序跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OCR识别器实例（全局单例，避免重复加载模型）
ocr_engine = None


class OCRResult(BaseModel):
    """OCR识别结果"""
    text: str
    confidence: float
    box: List[List[float]]


class OCRResponse(BaseModel):
    """OCR响应"""
    success: bool
    message: str
    data: Optional[List[OCRResult]] = None
    raw_text: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化OCR引擎"""
    global ocr_engine
    try:
        from app.utils.ocr_engine import OCREngine
        logger.info("正在初始化PaddleOCR引擎...")
        ocr_engine = OCREngine()
        logger.info("PaddleOCR引擎初始化成功")
    except Exception as e:
        logger.error(f"OCR引擎初始化失败: {str(e)}")


@app.get("/")
async def root():
    """健康检查接口"""
    return {
        "service": "食品标签OCR识别服务",
        "status": "running",
        "model_loaded": ocr_engine is not None
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy" if ocr_engine else "unhealthy",
        "model_loaded": ocr_engine is not None
    }


@app.post("/ocr/text", response_model=OCRResponse)
async def recognize_text(image_base64: str):
    """
    识别图片中的所有文字（接收Base64编码的图片）

    参数:
        image_base64: Base64编码的图片字符串（不含data:image前缀）

    返回:
        OCRResponse: 包含识别结果和原始文本
    """
    if not ocr_engine:
        raise HTTPException(status_code=503, detail="OCR引擎未初始化")

    try:
        # 解码Base64图片
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))

        # 执行OCR识别
        results = ocr_engine.recognize(image)

        # 提取原始文本（所有文字合并）
        raw_text = "\n".join([item["text"] for item in results])

        logger.info(f"OCR识别成功，共识别到 {len(results)} 个文本块")

        return OCRResponse(
            success=True,
            message="识别成功",
            data=[OCRResult(**item) for item in results],
            raw_text=raw_text
        )

    except Exception as e:
        logger.error(f"OCR识别失败: {str(e)}")
        return OCRResponse(
            success=False,
            message=f"识别失败: {str(e)}",
            data=None,
            raw_text=None
        )


@app.post("/ocr/upload", response_model=OCRResponse)
async def recognize_uploaded_file(file: UploadFile = File(...)):
    """
    识别上传的图片文件

    参数:
        file: 上传的图片文件

    返回:
        OCRResponse: 包含识别结果和原始文本
    """
    if not ocr_engine:
        raise HTTPException(status_code=503, detail="OCR引擎未初始化")

    try:
        # 读取上传的文件
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # 执行OCR识别
        results = ocr_engine.recognize(image)

        # 提取原始文本
        raw_text = "\n".join([item["text"] for item in results])

        logger.info(f"文件上传OCR识别成功，共识别到 {len(results)} 个文本块")

        return OCRResponse(
            success=True,
            message="识别成功",
            data=[OCRResult(**item) for item in results],
            raw_text=raw_text
        )

    except Exception as e:
        logger.error(f"文件上传OCR识别失败: {str(e)}")
        return OCRResponse(
            success=False,
            message=f"识别失败: {str(e)}",
            data=None,
            raw_text=None
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

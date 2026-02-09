"""
PaddleOCR引擎封装
"""

import logging
from typing import List, Dict
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class OCREngine:
    """PaddleOCR引擎类"""

    def __init__(self):
        """初始化OCR引擎"""
        try:
            from paddleocr import PaddleOCR

            # 使用轻量级模型，适合云环境部署
            self.ocr = PaddleOCR(
                use_angle_cls=True,      # 使用方向分类器
                lang="ch",                # 中文识别
                use_gpu=False,            # Railway环境使用CPU
                show_log=False,           # 关闭日志输出
                # 使用默认模型（首次运行会自动下载）
                # 如需离线部署，可指定det_model_dir和rec_model_dir
            )
            logger.info("PaddleOCR引擎加载成功")

        except Exception as e:
            logger.error(f"PaddleOCR加载失败: {str(e)}")
            raise

    def recognize(self, image: Image.Image) -> List[Dict]:
        """
        识别图片中的文字

        参数:
            image: PIL Image对象

        返回:
            List[Dict]: 识别结果列表，每个元素包含:
                - text: 识别的文字
                - confidence: 置信度
                - box: 文本框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        """
        try:
            # 转换PIL Image到numpy array（BGR格式）
            img_array = np.array(image)

            # RGB转BGR（OpenCV格式）
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = img_array[:, :, ::-1]

            # 执行OCR识别
            result = self.ocr.ocr(img_array, cls=True)

            # 如果没有识别结果
            if not result or not result[0]:
                logger.warning("未识别到任何文字")
                return []

            # 提取文本块信息
            text_blocks = []
            for line in result[0]:
                box = line[0]  # 坐标框
                text_info = line[1]  # (text, confidence)

                text_blocks.append({
                    "text": text_info[0],
                    "confidence": float(text_info[1]),
                    "box": [[float(x[0]), float(x[1])] for x in box]
                })

            logger.info(f"识别到 {len(text_blocks)} 个文本块")
            return text_blocks

        except Exception as e:
            logger.error(f"OCR识别失败: {str(e)}")
            return []

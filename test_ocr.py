#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR服务本地测试脚本
测试OCR识别功能是否正常
"""

import base64
import requests
import sys
from pathlib import Path


def image_to_base64(image_path):
    """将图片转换为Base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def test_ocr_service(image_path, service_url="http://localhost:8000/ocr/text"):
    """
    测试OCR服务

    参数:
        image_path: 图片路径
        service_url: OCR服务URL
    """
    print(f"正在测试图片: {image_path}")
    print(f"OCR服务地址: {service_url}")
    print("-" * 50)

    # 检查文件是否存在
    if not Path(image_path).exists():
        print(f"[ERROR] File not found - {image_path}")
        return False

    try:
        # 转换图片为Base64
        print("Reading image...")
        image_base64 = image_to_base64(image_path)
        print(f"Image read successfully (size: {len(image_base64)} characters)")

        # 调用OCR服务
        print("Calling OCR service...")
        response = requests.post(
            service_url,
            json={"image_base64": image_base64},
            timeout=30
        )

        # 检查响应
        if response.status_code == 200:
            result = response.json()

            if result.get('success'):
                print(f"\n[SUCCESS] OCR recognition successful!")
                print(f"Total text blocks detected: {len(result.get('data', []))}\n")

                # 打印每个文本块
                for idx, item in enumerate(result.get('data', []), 1):
                    print(f"[{idx}] {item['text']}")
                    print(f"    Confidence: {item['confidence']*100:.1f}%")
                    print(f"    Position: {item['box']}")
                    print()

                # 打印原始文本
                print("---------- Raw Text ----------")
                print(result.get('raw_text', ''))
                print("-" * 50)

                return True
            else:
                print(f"[ERROR] OCR recognition failed: {result.get('message')}")
                return False
        else:
            print(f"[ERROR] HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("[ERROR] Request timeout (30 seconds)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to OCR service ({service_url})")
        print("Please ensure the service is running: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python test_ocr.py <图片路径> [服务URL]")
        print("示例: python test_ocr.py test.jpg")
        print("示例: python test_ocr.py test.jpg https://your-app.railway.app/ocr/text")
        sys.exit(1)

    image_path = sys.argv[1]
    service_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000/ocr/text"

    # 测试OCR服务
    success = test_ocr_service(image_path, service_url)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

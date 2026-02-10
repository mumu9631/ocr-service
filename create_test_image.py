#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建OCR测试图片
生成一个简单的食品标签图片用于测试
"""

from PIL import Image, ImageDraw, ImageFont
import os

# 创建测试图片
def create_test_food_label():
    # 图片尺寸
    width, height = 600, 400

    # 创建白色背景
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # 尝试使用系统字体
    try:
        # Windows系统字体
        font_large = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 32)
        font_medium = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 24)
        font_small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
    except:
        # 如果找不到中文字体，使用默认字体
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 绘制食品标签内容
    y_pos = 30

    # 食品名称
    draw.text((50, y_pos), "食品名称: 原味饼干", fill='black', font=font_large)
    y_pos += 60

    # 配料表
    draw.text((50, y_pos), "配料表: 小麦粉、白砂糖、食用植物油", fill='black', font=font_medium)
    y_pos += 40
    draw.text((50, y_pos), "鸡蛋、食用盐、膨松剂", fill='black', font=font_medium)
    y_pos += 50

    # 净含量
    draw.text((50, y_pos), "净含量: 200克", fill='black', font=font_medium)
    y_pos += 40

    # 营养成分
    draw.text((50, y_pos), "营养成分表:", fill='black', font=font_medium)
    y_pos += 30
    draw.text((70, y_pos), "能量: 2000千焦", fill='black', font=font_small)
    y_pos += 25
    draw.text((70, y_pos), "蛋白质: 8.0克", fill='black', font=font_small)
    y_pos += 25
    draw.text((70, y_pos), "脂肪: 15.0克", fill='black', font=font_small)
    y_pos += 25
    draw.text((70, y_pos), "碳水化合物: 60.0克", fill='black', font=font_small)
    y_pos += 25
    draw.text((70, y_pos), "钠: 400毫克", fill='black', font=font_small)

    # 保存图片
    output_path = os.path.join(os.path.dirname(__file__), 'test_food_label.png')
    img.save(output_path)
    print(f"Test image created: {output_path}")
    return output_path

if __name__ == '__main__':
    create_test_food_label()

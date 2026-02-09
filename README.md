# 食品标签OCR识别服务

基于PaddleOCR的预包装食品标签文字识别API服务，部署在Railway.app上。

## 功能特性

- ✅ 支持中文食品标签识别
- ✅ 返回文本位置和置信度
- ✅ Base64和文件上传两种方式
- ✅ 格式化输出所有识别文字

## 部署步骤

### 1. 准备Railway账号

访问 [railway.app](https://railway.app/) 注册账号

### 2. 创建新项目

```bash
# 安装Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
cd ocr-service
railway init

# 部署
railway up
```

### 3. 或通过GitHub部署（推荐）

1. 将此目录推送到GitHub仓库
2. 在Railway控制台选择"Deploy from GitHub repo"
3. 选择此仓库
4. Railway会自动检测Python项目并部署

### 4. 环境变量配置（可选）

在Railway控制台添加环境变量：

```
PORT=8000
LOG_LEVEL=INFO
```

## API接口

### 健康检查

```
GET /health
```

### OCR识别（Base64）

```
POST /ocr/text
Content-Type: application/json

{
  "image_base64": "base64编码的图片字符串"
}
```

### OCR识别（文件上传）

```
POST /ocr/upload
Content-Type: multipart/form-data

file: <图片文件>
```

## 响应示例

```json
{
  "success": true,
  "message": "识别成功",
  "data": [
    {
      "text": "原味混合坚果礼盒",
      "confidence": 0.98,
      "box": [[100, 50], [300, 50], [300, 100], [100, 100]]
    }
  ],
  "raw_text": "原味混合坚果礼盒\n配料表：扁桃仁、核桃仁..."
}
```

## 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload

# 测试接口
curl -X POST http://localhost:8000/ocr/text \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "..."}'
```

## 性能优化

- 首次启动会下载PaddleOCR模型（约10MB）
- 模型会缓存在容器中，后续请求响应更快
- 建议配置Railway的最低内存为512MB

## 注意事项

- Railway免费套餐每月有$5额度
- 建议设置健康检查避免超时
- 生产环境建议配置具体域名CORS

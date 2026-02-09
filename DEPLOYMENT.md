# PaddleOCR食品标签识别服务 - 完整部署指南

## 📋 方案概述

本方案采用**Python FastAPI服务 + Railway.app部署**的方式，为微信小程序提供食品标签OCR识别能力。

### 技术架构

```
微信小程序
    ↓ (Base64图片)
Railway.app OCR服务 (PaddleOCR)
    ↓ (JSON识别结果)
格式化输出
```

---

## 🚀 部署步骤

### 步骤1: 准备代码

```bash
# 进入OCR服务目录
cd ocr-service

# 查看文件结构
ls -la
```

**目录结构**:
```
ocr-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI主应用
│   └── utils/
│       ├── __init__.py
│       └── ocr_engine.py    # PaddleOCR引擎封装
├── requirements.txt         # Python依赖
├── railway.json            # Railway配置
├── Procfile                # 启动命令
└── README.md               # 使用说明
```

### 步骤2: 推送代码到GitHub

```bash
# 初始化Git仓库（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: PaddleOCR service"

# 推送到GitHub（替换为你的仓库地址）
git remote add origin https://github.com/your-username/food-label-ocr.git
git push -u origin main
```

### 步骤3: 部署到Railway.app

#### 方式A: 通过Railway控制台（推荐）

1. 访问 [railway.app](https://railway.app/) 并登录
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 授权并选择刚推送的仓库
5. Railway会自动检测Python项目并开始部署

#### 方式B: 通过Railway CLI

```bash
# 安装Railway CLI
npm install -g @railway/cli

# 登录Railway
railway login

# 初始化项目
cd ocr-service
railway init

# 部署
railway up
```

### 步骤4: 等待部署完成

- 首次部署需要下载PaddleOCR模型（约10-20MB），可能需要2-5分钟
- 在Railway控制台可以看到部署日志
- 部署成功后会显示类似: `https://your-app-name.railway.app`

### 步骤5: 测试服务

```bash
# 健康检查
curl https://your-app-name.railway.app/health

# 应返回:
# {"status":"healthy","model_loaded":true}
```

---

## 🔧 配置小程序

### 步骤1: 修改OCR服务地址

编辑 `miniprogram/utils/ocrService.js`:

```javascript
// 修改为你的Railway服务地址
const OCR_SERVICE_URL = 'https://your-app-name.railway.app/ocr/text';
```

### 步骤2: 配置服务器域名（重要）

在微信公众平台配置服务器域名:

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入"开发" → "开发管理" → "开发设置"
3. 在"服务器域名"中，将你的Railway域名添加到:
   - **request合法域名**: `https://your-app-name.railway.app`

**注意**:
- 开发阶段可以勾选"不校验合法域名"进行测试
- 正式发布必须配置合法域名

### 步骤3: 测试小程序

1. 在微信开发者工具中打开项目
2. 进入"拍照识别"页面
3. 拍摄或选择食品标签图片
4. 查看控制台输出的识别结果

---

## 📊 查看识别结果

### 在小程序控制台查看

识别成功后，控制台会输出格式化的结果:

```
========== OCR识别结果 ==========
共识别到 18 个文本块

[1] 原味混合坚果礼盒
    置信度: 98.0%
    位置: [[100,50],[300,50],[300,100],[100,100]]

[2] 配料表：扁桃仁、核桃仁、腰果仁、榛子仁、开心果仁、夏威夷果
    置信度: 95.0%
    位置: [[50,120],[350,120],[350,170],[50,170]]

...

---------- 原始文本 ----------
原味混合坚果礼盒
配料表：扁桃仁、核桃仁、腰果仁、榛子仁、开心果仁、夏威夷果
净含量：500g
生产日期：2025-04-10
...
================================
```

### 识别结果数据结构

```javascript
{
  success: true,
  message: "识别成功",
  data: [
    {
      text: "原味混合坚果礼盒",
      confidence: 0.98,
      box: [[100, 50], [300, 50], [300, 100], [100, 100]]
    },
    // ... 更多文本块
  ],
  raw_text: "原味混合坚果礼盒\n配料表：..."
}
```

---

## 💰 成本估算

### Railway.app定价

| 套餐 | 价格 | 配置 | 适用场景 |
|------|------|------|----------|
| Free | $0/月 | 512MB RAM, $5额度/月 | 开发测试 |
| Pay As You Go | 按使用计费 | $5/月起 | 小规模应用 |

**预估成本**:
- 开发阶段: 免费（$5额度足够）
- 生产环境: 约$5-10/月（取决于调用次数）

### 优化成本建议

1. **启用缓存**: 相同图片不重复识别
2. **压缩图片**: 识别前压缩到合适大小（建议宽度1500-2000px）
3. **自动休眠**: Railway免费套餐会自动休眠无流量的服务

---

## 🔍 故障排查

### 问题1: 部署失败

**症状**: Railway控制台显示部署错误

**解决方案**:
1. 检查 `requirements.txt` 版本兼容性
2. 查看Railway部署日志
3. 确保Python版本为3.8+

### 问题2: 小程序请求失败

**症状**: 提示"OCR服务调用失败"

**解决方案**:
1. 检查Railway服务是否正常部署: `/health`
2. 确认小程序中配置的服务地址正确
3. 检查微信服务器域名配置
4. 开发阶段确保勾选了"不校验合法域名"

### 问题3: 识别准确率低

**症状**: 识别结果不完整或有误

**解决方案**:
1. 确保拍摄时光线充足
2. 标签文字尽量清晰对齐
3. 避免反光和模糊
4. 可以尝试多次拍摄

### 问题4: 响应速度慢

**症状**: 识别耗时超过10秒

**解决方案**:
1. 压缩图片大小（建议<2MB）
2. 升级Railway套餐（更多CPU/内存）
3. 使用更快的OCR模型（PP-OCRv4-mobile）

---

## 📈 性能优化

### 1. 图片预处理

在小程序端压缩图片:

```javascript
// 压缩图片后再上传
wx.compressImage({
  src: imagePath,
  quality: 80,
  success: (res) => {
    // 使用压缩后的图片
    this.processImage(res.tempFilePath);
  }
});
```

### 2. 模型优化

使用轻量级模型:

```python
# 在 ocr_engine.py 中配置
self.ocr = PaddleOCR(
    det_model_dir=None,  # 使用轻量级检测模型
    rec_model_dir=None,  # 使用轻量级识别模型
    use_angle_cls=False, # 关闭方向分类器提升速度
    lang="ch"
)
```

### 3. 结果缓存

缓存识别结果:

```javascript
// 使用图片hash作为key
const imageHash = getImageHash(imageBase64);
const cached = wx.getStorageSync(`ocr_${imageHash}`);
if (cached) {
  return cached;
}
```

---

## 🎯 后续扩展

### 1. 结构化提取

在当前OCR文字识别的基础上，添加字段提取逻辑:

```javascript
// 从OCR结果中提取13项强制标示内容
function extractStructuredFields(ocrData) {
  return {
    name: extractFoodName(ocrData),
    ingredients: extractIngredients(ocrData),
    nutrition: extractNutrition(ocrData),
    // ... 更多字段
  };
}
```

### 2. 数据库存储

将识别结果存储到云数据库:

```javascript
// 保存识别历史
wx.cloud.database().collection('ocrHistory').add({
  data: {
    image: imageBase64,
    result: ocrResult,
    createTime: new Date()
  }
});
```

### 3. 批量识别

支持多张图片连续识别:

```javascript
// 批量处理
for (const image of images) {
  const result = await ocrService.recognizeText(image);
  results.push(result);
}
```

---

## 📞 技术支持

如有问题，请查看:
- Railway文档: https://docs.railway.app/
- PaddleOCR文档: https://github.com/PaddlePaddle/PaddleOCR
- FastAPI文档: https://fastapi.tiangolo.com/

---

## ✅ 部署检查清单

- [ ] 代码已推送到GitHub
- [ ] Railway项目已创建并部署成功
- [ ] `/health` 接口返回正常
- [ ] 小程序中OCR服务地址已更新
- [ ] 微信服务器域名已配置（正式环境）
- [ ] 测试识别功能正常
- [ ] 控制台输出格式化结果

---

**部署完成后，你就可以开始使用真实的OCR识别功能了！** 🎉

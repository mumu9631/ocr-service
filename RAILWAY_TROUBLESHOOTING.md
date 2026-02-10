# Railway 部署故障排查指南

本文档记录了在 Railway.app 上部署 PaddleOCR 服务时遇到的问题及解决方案。

## 📌 问题摘要

部署失败的核心原因是 **Python 版本不兼容**。

- **Railway 默认**: Python 3.12
- **PaddlePaddle 要求**: Python 3.8-3.11（不兼容 3.12）
- **解决方案**: 使用 `runtime.txt` 强制指定 Python 3.10.14

---

## 🔧 问题1: pip install 失败 (exit code: 1)

### 错误日志
```
ERROR: failed to build: failed to solve: process "/bin/bash -ol pipefail -c python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt" did not complete successfully: exit code: 1
Dockerfile:20
```

### 根本原因
PaddlePaddle 2.6.2 及以下版本 **不支持 Python 3.12**。Railway 默认使用最新 Python 版本，导致依赖安装失败。

### 解决步骤

#### 步骤 1: 创建 `runtime.txt` 文件
在 `ocr-service/` 目录下创建 `runtime.txt`:

```bash
cd ocr-service
echo "python-3.10.14" > runtime.txt
```

文件内容:
```
python-3.10.14
```

#### 步骤 2: 优化 `requirements.txt`
将严格版本约束 (`==`) 改为宽松约束 (`>=`)，允许 pip 解析兼容版本:

**修改前**:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
paddlepaddle==2.6.2
paddleocr==2.7.0.3
opencv-python-headless==4.8.1.78
```

**修改后**:
```txt
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
pydantic>=2.5.0
paddlepaddle>=2.5.0
paddleocr>=2.7.0
opencv-python-headless>=4.8.0
pillow>=10.0.0
numpy>=1.24.0
```

#### 步骤 3: 推送到 GitHub
```bash
cd ocr-service
git add runtime.txt requirements.txt
git commit -m "Fix: Pin Python version for PaddlePaddle compatibility"
git push origin main
```

#### 步骤 4: 触发 Railway 重新部署
- Railway 会自动检测到推送并开始部署
- 或在 Railway 控制台手动点击 "Redeploy"

---

## 🔧 问题2: Nix 包错误 (undefined variable 'libglib')

### 错误日志
```
error: undefined variable 'libglib'
at /app/.nixpacks/nixpkgs-bc8f8d1be58e8c8383e683a06e1e1e57893fff87.nix:19:19
```

### 根本原因
自定义 `nixpacks.toml` 配置文件中使用了不存在的 Nix 包名 `libglib`。

### 解决方案
**删除 `nixpacks.toml` 文件**，使用 Railway 默认 Python provider。

```bash
cd ocr-service
rm nixpacks.toml
git add -A
git commit -m "Remove custom nixpacks.toml to use default provider"
git push origin main
```

---

## 🔧 问题3: OpenCV 缺少 OpenGL 库 (libGL.so.1)

### 错误日志
```
ERROR:app.utils.ocr_engine:PaddleOCR加载失败: libGL.so.1: cannot open shared object file: No such file or directory
ERROR:app.main:OCR引擎初始化失败: libGL.so.1: cannot open shared object file: No such file or directory
```

### 根本原因
`opencv-python-headless` 依赖 OpenGL 库 (`libGL.so.1`)，但 Railway 默认环境没有安装。

### 解决方案
创建正确的 `nixpacks.toml` 文件，添加 OpenGL 系统依赖。

#### 步骤 1: 创建 `nixpacks.toml`

在 `ocr-service/` 目录下创建 `nixpacks.toml`:

```bash
cd ocr-service
cat > nixpacks.toml << 'EOF'
[phases.setup]
nixPkgs = ["python310", "libGL", "libglvnd"]

[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
EOF
```

文件内容:
```toml
[phases.setup]
nixPkgs = ["python310", "mesa", "freeglut"]

[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

#### 关键配置说明
- `mesa` - Mesa 3D 图形库（开源 OpenGL 实现，包含 libGL.so）
- `freeglut` - OpenGL Utility Toolkit（提供 GLU 和 GLUT）

**包名说明**:
- ❌ `libGL`, `libglvnd`, `xorg.libGL`, `glib` - 这些不是正确的或不必要的 Nix 包名
- ✅ `mesa` 是 Nix 中正确的 OpenGL 库包名，已包含 libGL.so.1
- ✅ `freeglut` 提供额外的 OpenGL 工具函数

**简化配置原则**:
- 只安装必要的包，减少依赖冲突
- `mesa` 包已经包含了 OpenCV 需要的 OpenGL 库

#### 步骤 2: 推送到 GitHub
```bash
cd ocr-service
git add nixpacks.toml
git commit -m "Fix: Add OpenGL library dependency for OpenCV"
git push origin main
```

#### 关键配置说明
- `libGL` - OpenGL 核心库
- `libglvnd` - OpenGL vendor-neutral dispatch 库
- 这两个库是 OpenCV 运行所必需的

**为什么现在需要 nixpacks.toml?**
- Railway 的默认 Python provider **不包含** OpenGL 库
- `opencv-python-headless` 运行时需要 `libGL.so.1`
- 必须通过 `nixpacks.toml` 明确指定系统依赖

---

## ✅ 最终配置

### 必需文件
```
ocr-service/
├── runtime.txt          # ⭐ 必需：指定 Python 版本
├── nixpacks.toml        # ⭐ 必需：指定系统依赖（OpenGL）
├── requirements.txt     # ⭐ 必需：Python 依赖
├── railway.json         # 可选：Railway 配置
├── Procfile            # 可选：启动命令（railway.json 已配置）
└── app/
    └── main.py         # FastAPI 应用入口
```

### 关键配置

**runtime.txt** (必需):
```
python-3.10.14
```

**nixpacks.toml** (必需):
```toml
[phases.setup]
nixPkgs = ["python310", "mesa", "freeglut"]

[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

**railway.json** (推荐):
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

**requirements.txt** (关键依赖):
```txt
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
pydantic>=2.5.0
paddlepaddle>=2.5.0
paddleocr>=2.7.0
opencv-python-headless>=4.8.0
pillow>=10.0.0
numpy>=1.24.0
```

---

## 🚀 部署验证

### 1. 检查部署状态
访问 Railway 控制台，确认：
- Build 状态: ✅ Success
- Python 版本: 3.10.14
- 所有依赖安装成功

### 2. 测试健康检查
```bash
curl https://your-app-name.railway.app/health
```

应返回:
```json
{"status":"healthy","model_loaded":true}
```

### 3. 测试 OCR 功能
使用 `test_ocr.py` 测试完整的 OCR 功能:
```bash
cd ocr-service
python test_ocr.py
```

---

## 📚 版本兼容性参考

| Python 版本 | PaddlePaddle 兼容性 | 推荐使用 |
|------------|-------------------|---------|
| 3.8.x      | ✅ 支持            | ⭐⭐⭐ |
| 3.9.x      | ✅ 支持            | ⭐⭐⭐ |
| 3.10.x     | ✅ 支持            | ⭐⭐⭐⭐ (推荐) |
| 3.11.x     | ✅ 支持            | ⭐⭐⭐ |
| 3.12.x     | ❌ 不支持           | ❌ |

**推荐**: Python 3.10.14 (稳定且兼容性好)

---

## 🔗 相关链接

- [Railway 文档](https://docs.railway.app/)
- [PaddleOCR 安装指南](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_ch/installation.md)
- [Python 版本兼容性](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/requirements.txt)

---

## 📝 更新日志

**2025-02-10**:
- 初始版本
- 记录 Python 版本兼容性问题
- 记录 Nix 包配置问题
- 记录 OpenGL 库缺失问题（问题3）
- 提供完整解决方案

---

**下次遇到部署问题时，请按以下顺序检查**:
1. ✅ `runtime.txt` 存在且指定 Python 3.10.14
2. ✅ `nixpacks.toml` 存在且包含 OpenGL 依赖
3. ✅ `requirements.txt` 使用宽松版本约束
4. ✅ Railway 日志显示 OCR 模型加载成功


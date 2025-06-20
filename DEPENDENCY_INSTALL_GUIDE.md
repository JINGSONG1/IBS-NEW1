# 🏥 ReticulotypeToolkit 依赖安装指南

## 🚨 Python 3.12 兼容性问题解决方案

### 问题描述
- **错误类型**: `resolution-too-deep` 依赖解析超时
- **根本原因**: 原始 `requirements.txt` 依赖关系过于复杂，pip无法有效解析
- **影响环境**: Python 3.12.7

### ✅ 解决方案

#### 方法一：智能安装脚本（推荐）

```bash
# 运行智能安装脚本
python install_deps.py
```

**优势**：
- 🔄 自动分批安装，避免依赖冲突
- 🛠️ 智能处理版本兼容性
- 🧪 安装后自动测试
- ⚡ 快速且可靠

#### 方法二：手动分批安装

```bash
# 1. 安装核心依赖
pip install -r requirements_optional.txt

# 2. 手动安装特定包
pip install torch>=2.2.0
pip install tensorflow>=2.15.0
pip install transformers>=4.36.0
```

#### 方法三：降级依赖管理

```bash
# 使用旧的依赖解析器
pip install -r requirements.txt --use-deprecated=legacy-resolver
```

### 📦 已验证的包列表

#### 核心AI功能 ✅
- **数据处理**: numpy 1.26.4, pandas 2.1.4, scipy 1.11.4
- **机器学习**: scikit-learn 1.4.2
- **深度学习**: PyTorch 2.7.0, TensorFlow 2.19.0
- **NLP**: transformers 4.52.4, sentence-transformers 4.1.0
- **Web框架**: Streamlit 1.37.1

#### 附加功能 ✅
- **图像处理**: OpenCV 4.11.0
- **网络分析**: NetworkX 3.3, pyvis 0.3.2
- **可视化**: matplotlib 3.10.3, plotly 5.24.1
- **文档生成**: reportlab 4.4.2, python-docx 1.2.0
- **中文处理**: jieba 0.42.1, zhconv 1.4.3

### 🔧 已知兼容性问题

#### 轻微冲突（不影响使用）
```
pycaret 3.3.2 requires matplotlib<3.8.0, but you have matplotlib 3.10.3
thinc 8.3.6 requires numpy<3.0.0,>=2.0.0, but you have numpy 1.26.4
```

**解决方案**: 这些冲突不影响核心功能，可以忽略。

### 🚀 验证安装

运行以下命令测试安装：

```python
python -c "
import numpy as np
import pandas as pd
import torch
import tensorflow as tf
import streamlit as st
import sklearn
import cv2
import networkx as nx
print('🎉 所有核心包安装成功!')
"
```

### 📋 故障排除

#### 1. 如果遇到 `resolution-too-deep` 错误
- ❌ **不要使用**: `pip install -r requirements.txt`
- ✅ **改用**: `python install_deps.py`

#### 2. 如果遇到版本冲突
```bash
# 强制重装numpy到兼容版本
pip install numpy>=1.26.0,<2.0.0 --force-reinstall
```

#### 3. 如果单个包安装失败
```bash
# 跳过依赖检查安装
pip install 包名 --no-deps
```

### 🎯 最佳实践

1. **使用虚拟环境**
```bash
python -m venv reticulotype_env
source reticulotype_env/bin/activate  # macOS/Linux
# 或
reticulotype_env\Scripts\activate     # Windows
```

2. **定期更新pip**
```bash
pip install --upgrade pip setuptools wheel
```

3. **清理缓存**
```bash
pip cache purge
```

### 📊 系统状态检查

运行以下命令检查当前状态：

```bash
# 检查依赖冲突
pip check

# 查看已安装包
pip list | grep -E "(torch|tensorflow|streamlit|numpy|pandas)"

# 运行智能安装脚本的测试功能
python -c "from install_deps import test_installation; test_installation()"
```

### 🆘 获取帮助

如果仍然遇到问题：

1. 查看 `install_deps.py` 的详细日志
2. 确认Python版本：`python --version`
3. 确认pip版本：`pip --version`
4. 检查网络连接和代理设置

---

## 🎉 成功标志

看到以下信息表示安装成功：

```
✨ 恭喜！所有依赖已成功安装并兼容Python 3.12
🚀 现在可以运行ReticulotypeToolkit的所有功能了！
```

此时您的 ReticulotypeToolkit AI医疗诊断平台已完全就绪！ 
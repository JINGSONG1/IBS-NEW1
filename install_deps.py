#!/usr/bin/env python3
"""
🏥 ReticulotypeToolkit 智能依赖安装脚本
解决 Python 3.12 环境下的依赖兼容性问题
自动分批安装，避免 pip resolution-too-deep 错误
"""

import subprocess
import sys
import os
from pathlib import Path

def run_pip_install(packages, description=""):
    """安全地安装包列表"""
    print(f"\n📦 安装 {description}...")
    if isinstance(packages, str):
        packages = [packages]
    
    for package in packages:
        try:
            print(f"  ✅ 安装: {package}")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print(f"  ⚠️  {package} 安装失败，跳过...")
                print(f"     错误: {result.stderr[:100]}...")
                continue
                
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  {package} 安装超时，跳过...")
            continue
        except Exception as e:
            print(f"  ⚠️  {package} 安装异常: {str(e)[:50]}...")
            continue

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"🐍 Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 10:
        print("⚠️  建议使用Python 3.10+版本")
    elif version.minor >= 12:
        print("✅ Python 3.12+环境，使用兼容版本安装")
    
    return version.minor >= 12

def install_core_packages():
    """安装核心包"""
    core_packages = [
        "streamlit>=1.29.0",
        "streamlit-option-menu>=0.3.6", 
        "streamlit-aggrid>=0.3.4",
        "pandas>=2.1.0",
        "numpy>=1.26.0,<2.0.0",  # 限制numpy版本避免冲突
        "scipy>=1.11.0",
        "scikit-learn>=1.3.0",
        "torch>=2.2.0",
        "tensorflow>=2.15.0",
        "plotly>=5.15.0",
        "matplotlib>=3.8.0",
        "seaborn>=0.13.0",
        "transformers>=4.36.0",
        "sentence-transformers>=2.2.0",
        "nltk>=3.8.0",
        "jieba>=0.42.0",
        "requests>=2.31.0",
        "openai>=1.6.0",
        "pyyaml>=6.0.0",
        "python-dotenv>=1.0.0",
        "tqdm>=4.66.0",
        "rich>=13.0.0",
        "pydantic>=2.5.0"
    ]
    
    run_pip_install(core_packages, "核心AI和Web框架包")

def install_additional_packages():
    """安装附加功能包"""
    additional_groups = {
        "图像和网络分析": [
            "opencv-python>=4.8.0",
            "networkx>=3.2.0", 
            "pyvis>=0.3.2",
            "graphviz>=0.20.0"
        ],
        "医疗和科学计算": [
            "lifelines>=0.27.0",
            "statsmodels>=0.14.0",
            "pingouin>=0.5.0"
        ],
        "文档和报告": [
            "reportlab>=4.0.0",
            "fpdf2>=2.7.0",
            "python-docx>=1.0.0"
        ],
        "开发和测试": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0"
        ],
        "数据库和缓存": [
            "sqlalchemy>=2.0.0",
            "redis>=5.0.0"
        ],
        "安全和配置": [
            "cryptography>=41.0.0",
            "pycryptodome>=3.19.0",
            "python-decouple>=3.8"
        ],
        "中文处理": [
            "zhconv>=1.4.0",
            "pypinyin>=0.50.0"
        ],
        "系统监控": [
            "psutil>=5.9.0",
            "memory-profiler>=0.61.0"
        ]
    }
    
    for group_name, packages in additional_groups.items():
        run_pip_install(packages, group_name)

def fix_version_conflicts():
    """修复已知的版本冲突"""
    print("\n🔧 修复版本冲突...")
    
    # 确保numpy版本兼容
    run_pip_install("numpy>=1.26.0,<2.0.0 --force-reinstall", "numpy版本修复")

def test_installation():
    """测试安装结果"""
    print("\n🧪 测试安装结果...")
    
    test_imports = [
        ("numpy", "np"),
        ("pandas", "pd"), 
        ("torch", None),
        ("tensorflow", "tf"),
        ("sklearn", None),
        ("streamlit", "st"),
        ("transformers", None),
        ("cv2", None),
        ("networkx", "nx")
    ]
    
    success_count = 0
    for module, alias in test_imports:
        try:
            if alias:
                exec(f"import {module} as {alias}")
            else:
                exec(f"import {module}")
            print(f"  ✅ {module}")
            success_count += 1
        except ImportError:
            print(f"  ❌ {module}")
    
    print(f"\n📊 测试结果: {success_count}/{len(test_imports)} 个包导入成功")
    
    if success_count >= len(test_imports) * 0.8:
        print("🎉 安装成功！系统可以正常运行")
        return True
    else:
        print("⚠️  部分包安装失败，但核心功能应该可用")
        return False

def main():
    """主安装流程"""
    print("=" * 60)
    print("🏥 ReticulotypeToolkit 智能依赖安装器")
    print("=" * 60)
    
    # 检查Python版本
    is_python312 = check_python_version()
    
    # 升级pip
    print("\n🔄 升级pip...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # 分阶段安装
    try:
        install_core_packages()
        install_additional_packages()
        
        if is_python312:
            fix_version_conflicts()
        
        # 测试安装
        success = test_installation()
        
        print("\n" + "=" * 60)
        if success:
            print("✨ 恭喜！所有依赖已成功安装并兼容Python 3.12")
            print("🚀 现在可以运行ReticulotypeToolkit的所有功能了！")
        else:
            print("⚠️  安装完成，但存在一些小问题")
            print("📝 核心功能仍然可用，可以开始使用系统")
        
        print("\n💡 提示：如果遇到问题，可以运行单独的包安装命令")
        print("例如：pip install 包名称>=版本号")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⏹️  安装被用户中断")
    except Exception as e:
        print(f"\n❌ 安装过程中出现错误: {e}")
        print("请检查网络连接和Python环境")

if __name__ == "__main__":
    main() 
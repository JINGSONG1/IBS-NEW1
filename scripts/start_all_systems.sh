#!/bin/bash

# 🚀 ReticulotypeToolkit v2.0 - 启动所有系统
# 一键启动11个医疗AI平台系统

echo "🏥 启动 ReticulotypeToolkit v2.0 - Latest Complete Edition"
echo "=================================================="

# 检查依赖
echo "📋 检查系统依赖..."
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit 未安装，请运行: pip install -r requirements.txt"
    exit 1
fi

# 检查Python版本
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "🐍 Python 版本: $python_version"

# 创建日志目录
mkdir -p logs
echo "📁 日志目录已创建: logs/"

# 启动系统函数
start_system() {
    local port=$1
    local script=$2
    local name=$3
    
    echo "🚀 启动 $name (Port $port)..."
    streamlit run platforms/$script --server.port $port --server.headless true > logs/${script%.*}_$port.log 2>&1 &
    
    # 等待系统启动
    sleep 2
    
    # 检查系统是否正常启动
    if pgrep -f "streamlit.*$port" > /dev/null; then
        echo "✅ $name 启动成功 - http://localhost:$port"
    else
        echo "❌ $name 启动失败，请检查日志: logs/${script%.*}_$port.log"
    fi
}

# 启动所有系统
echo ""
echo "🔥 开始启动所有系统..."
echo "================================"

start_system 8502 "quick_ai_deployment.py" "快速AI部署系统"
start_system 8503 "modern_ai_medical_platform.py" "现代AI医疗平台"
start_system 8504 "english_ai_medical_platform.py" "英文AI医疗平台"
start_system 8505 "enhanced_english_ai_platform.py" "增强英文AI平台"
start_system 8506 "fixed_emr_display.py" "修复EMR显示系统"
start_system 8507 "ultra_simple_emr.py" "超简EMR生成器"
start_system 8508 "tcm_western_integration.py" "中西医结合系统"
start_system 8509 "doctor_retention_optimization.py" "医生留存优化"
start_system 8510 "complete_doctor_retention_system.py" "完整医生留存系统"
start_system 8511 "super_strategy_inductor.py" "超级策略推导器"
start_system 8513 "doctor_ai_dashboard.py" "医生AI仪表板"

echo ""
echo "🎉 所有系统启动完成！"
echo "================================"
echo ""
echo "📊 系统访问地址:"
echo "  • Port 8502: 快速AI部署系统      - http://localhost:8502"
echo "  • Port 8503: 现代AI医疗平台      - http://localhost:8503"
echo "  • Port 8504: 英文AI医疗平台      - http://localhost:8504"
echo "  • Port 8505: 增强英文AI平台      - http://localhost:8505"
echo "  • Port 8506: 修复EMR显示系统     - http://localhost:8506"
echo "  • Port 8507: 超简EMR生成器       - http://localhost:8507"
echo "  • Port 8508: 中西医结合系统      - http://localhost:8508"
echo "  • Port 8509: 医生留存优化        - http://localhost:8509"
echo "  • Port 8510: 完整医生留存系统    - http://localhost:8510"
echo "  • Port 8511: 超级策略推导器      - http://localhost:8511"
echo "  • Port 8513: 医生AI仪表板        - http://localhost:8513"
echo ""
echo "📝 日志文件位置: logs/"
echo "🛑 停止所有系统: ./scripts/stop_all_systems.sh"
echo ""
echo "✨ ReticulotypeToolkit v2.0 已就绪！" 
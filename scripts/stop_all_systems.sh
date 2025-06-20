#!/bin/bash

# 🛑 ReticulotypeToolkit - 停止所有系统脚本
# 停止端口8502-8510上的所有Streamlit进程

echo "🛑 ReticulotypeToolkit - 系统停止器"
echo "================================="
echo "正在停止所有AI医疗系统..."
echo ""

# 停止函数
stop_port() {
    local port=$1
    local name=$2
    
    echo "🔍 检查端口 $port ($name)..."
    
    # 查找占用端口的进程
    pid=$(lsof -ti:$port)
    
    if [ -n "$pid" ]; then
        echo "   发现进程 PID: $pid"
        kill -TERM $pid
        sleep 2
        
        # 检查进程是否仍在运行
        if kill -0 $pid 2>/dev/null; then
            echo "   强制终止进程..."
            kill -KILL $pid
        fi
        
        echo "   ✅ $name 已停止"
    else
        echo "   ℹ️  端口 $port 未被占用"
    fi
    echo ""
}

# 停止所有系统
stop_port 8502 "快速AI部署系统"
stop_port 8503 "现代AI医疗平台"
stop_port 8504 "英文AI医疗平台"
stop_port 8505 "增强AI平台"
stop_port 8506 "EMR显示修复系统"
stop_port 8507 "超简EMR系统"
stop_port 8508 "中西医结合系统"
stop_port 8509 "医生留存优化系统"
stop_port 8510 "完整医生留存系统"

# 清理残留的streamlit进程
echo "🧹 清理残留进程..."
pkill -f "streamlit run" 2>/dev/null || true

echo "🎉 所有系统已停止！"
echo "================================="
echo ""
echo "📋 已停止的系统:"
echo "   ✅ 8502 - 快速AI部署系统"
echo "   ✅ 8503 - 现代AI医疗平台"
echo "   ✅ 8504 - 英文AI医疗平台"
echo "   ✅ 8505 - 增强AI平台"
echo "   ✅ 8506 - EMR显示修复系统"
echo "   ✅ 8507 - 超简EMR系统"
echo "   ✅ 8508 - 中西医结合系统"
echo "   ✅ 8509 - 医生留存优化系统"
echo "   ✅ 8510 - 完整医生留存系统"
echo ""
echo "💡 重新启动系统: ./start_all_systems.sh"
echo "🔍 检查系统状态: ./check_systems.sh" 
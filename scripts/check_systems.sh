#!/bin/bash

# 🔍 ReticulotypeToolkit - 系统状态检查器
# 检查端口8502-8510上所有系统的运行状态

echo "🔍 ReticulotypeToolkit - 系统状态检查器"
echo "======================================="
echo "检查所有AI医疗系统运行状态..."
echo ""

# 检查函数
check_port() {
    local port=$1
    local name=$2
    local file=$3
    
    # 检查端口是否被占用
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        local pid=$(lsof -ti:$port)
        echo "✅ 端口 $port - $name"
        echo "   状态: 运行中"
        echo "   PID: $pid" 
        echo "   URL: http://localhost:$port"
        
        # 检查HTTP响应
        if curl -s -f http://localhost:$port > /dev/null 2>&1; then
            echo "   HTTP: 响应正常 ✅"
        else
            echo "   HTTP: 响应异常 ⚠️"
        fi
        
        # 检查日志文件
        local log_file="logs/${file%.py}_$port.log"
        if [ -f "$log_file" ]; then
            local log_size=$(wc -l < "$log_file")
            echo "   日志: $log_file ($log_size 行)"
        fi
        
    else
        echo "❌ 端口 $port - $name"
        echo "   状态: 未运行"
    fi
    echo ""
}

# 系统信息
echo "💻 系统信息:"
echo "   操作系统: $(uname -s)"
echo "   Python版本: $(python3 --version 2>/dev/null || echo '未安装')"
echo "   当前时间: $(date)"
echo "   工作目录: $(pwd)"
echo ""

# 检查所有系统
echo "📋 系统状态详情:"
echo ""

check_port 8502 "快速AI部署系统" "quick_ai_deployment.py"
check_port 8503 "现代AI医疗平台" "modern_ai_medical_platform.py"
check_port 8504 "英文AI医疗平台" "english_ai_medical_platform.py"
check_port 8505 "增强AI平台" "enhanced_english_ai_platform.py"
check_port 8506 "EMR显示修复系统" "fixed_emr_display.py"
check_port 8507 "超简EMR系统" "ultra_simple_emr.py"
check_port 8508 "中西医结合系统" "tcm_western_integration.py"
check_port 8509 "医生留存优化系统" "doctor_retention_optimization.py"
check_port 8510 "完整医生留存系统 ⭐" "complete_doctor_retention_system.py"

# 统计信息
echo "📊 运行统计:"
running_count=0
total_count=9

for port in 8502 8503 8504 8505 8506 8507 8508 8509 8510; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        ((running_count++))
    fi
done

echo "   运行中: $running_count/$total_count 个系统"
echo "   运行率: $(( running_count * 100 / total_count ))%"

if [ $running_count -eq $total_count ]; then
    echo "   状态: 🟢 全部正常"
elif [ $running_count -gt 0 ]; then
    echo "   状态: 🟡 部分运行"
else
    echo "   状态: 🔴 全部停止"
fi

echo ""

# 资源使用情况
echo "💾 资源使用:"
if command -v ps &> /dev/null; then
    streamlit_processes=$(ps aux | grep "streamlit run" | grep -v grep | wc -l)
    echo "   Streamlit进程数: $streamlit_processes"
    
    if [ $streamlit_processes -gt 0 ]; then
        echo "   内存使用:"
        ps aux | grep "streamlit run" | grep -v grep | awk '{print "     PID " $2 ": " $6/1024 " MB (" $11 " " $12 " " $13 ")"}'
    fi
fi

echo ""

# 日志文件信息
echo "📄 日志文件:"
if [ -d "logs" ]; then
    log_count=$(ls -1 logs/*.log 2>/dev/null | wc -l)
    if [ $log_count -gt 0 ]; then
        echo "   日志文件数: $log_count"
        echo "   最新日志:"
        ls -1t logs/*.log 2>/dev/null | head -3 | while read log_file; do
            size=$(wc -l < "$log_file" 2>/dev/null)
            echo "     $log_file ($size 行)"
        done
    else
        echo "   无日志文件"
    fi
else
    echo "   日志目录不存在"
fi

echo ""
echo "======================================="

# 操作建议
if [ $running_count -eq 0 ]; then
    echo "💡 建议操作:"
    echo "   启动所有系统: ./start_all_systems.sh"
elif [ $running_count -lt $total_count ]; then
    echo "💡 建议操作:"
    echo "   重启所有系统: ./stop_all_systems.sh && ./start_all_systems.sh"
    echo "   或单独启动缺失的系统"
else
    echo "🎉 所有系统运行正常！"
    echo "   主推荐系统: http://localhost:8510"
fi

echo ""
echo "🔄 刷新状态: ./check_systems.sh"
echo "📚 查看文档: cat README.md" 
#!/usr/bin/env python3
"""
🔍 System Status Checker - 所有系统状态检查器
快速检查所有端口的运行状态
"""

import requests
import json
from datetime import datetime

def check_system_status():
    """检查所有系统状态"""
    
    systems = {
        8502: "快速AI部署系统",
        8503: "现代AI医疗平台(中文)",
        8504: "英文AI医疗平台", 
        8505: "增强AI平台",
        8506: "修复EMR显示系统",
        8507: "超简EMR系统",
        8508: "中西医结合系统",
        8509: "医生留存优化系统",
        8510: "完整医生留存系统",
        8511: "超强策略归纳器",
        8512: "另一个策略归纳器",
        8513: "医生-AI学习仪表盘"
    }
    
    print("🔍 正在检查所有系统状态...")
    print("=" * 60)
    
    status_summary = {
        "running": 0,
        "error": 0,
        "total": len(systems)
    }
    
    for port, name in systems.items():
        try:
            response = requests.get(f"http://localhost:{port}", timeout=5)
            if response.status_code == 200:
                status = "✅ 运行中"
                status_summary["running"] += 1
            else:
                status = f"⚠️ 响应异常 ({response.status_code})"
                status_summary["error"] += 1
        except:
            status = "❌ 无响应"
            status_summary["error"] += 1
        
        print(f"端口 {port}: {name:<25} {status}")
    
    print("=" * 60)
    print(f"📊 总结: {status_summary['running']}/{status_summary['total']} 系统正常运行")
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 生成状态报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "systems": systems,
        "status_summary": status_summary
    }
    
    with open("system_status_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("📄 详细报告已保存到: system_status_report.json")
    
    return status_summary

if __name__ == "__main__":
    check_system_status() 
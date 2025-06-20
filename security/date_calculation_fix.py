"""
Safe Date Calculation Utility
修复日期计算中的边界问题，确保月末日期的正确处理
"""

from datetime import datetime, timedelta
from typing import Optional
import calendar

class SafeDateCalculator:
    """安全的日期计算工具类"""
    
    @staticmethod
    def add_days(date: datetime, days: int) -> datetime:
        """
        安全地添加天数
        
        Args:
            date: 原始日期
            days: 要添加的天数
            
        Returns:
            新的日期
        """
        return date + timedelta(days=days)
    
    @staticmethod
    def add_months(date: datetime, months: int) -> datetime:
        """
        安全地添加月份（处理月末边界问题）
        
        Args:
            date: 原始日期
            months: 要添加的月数
            
        Returns:
            新的日期
        """
        month = date.month - 1 + months
        year = date.year + month // 12
        month = month % 12 + 1
        
        # 处理月末日期
        day = min(date.day, calendar.monthrange(year, month)[1])
        
        return datetime(year, month, day, date.hour, date.minute, date.second, date.microsecond)
    
    @staticmethod
    def safe_follow_up_date(current_date: datetime, days: int = 30) -> str:
        """
        安全生成随访日期字符串
        
        Args:
            current_date: 当前日期
            days: 随访间隔天数，默认30天
            
        Returns:
            格式化的随访日期字符串
        """
        try:
            follow_up_date = SafeDateCalculator.add_days(current_date, days)
            return follow_up_date.strftime('%Y年%m月%d日')
        except Exception as e:
            # 如果出错，返回一个默认的安全日期
            fallback_date = current_date + timedelta(days=30)
            return fallback_date.strftime('%Y年%m月%d日')
    
    @staticmethod
    def validate_date(year: int, month: int, day: int) -> bool:
        """
        验证日期是否有效
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            
        Returns:
            日期是否有效
        """
        try:
            datetime(year, month, day)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def fix_date_calculation_in_file(file_path: str, backup: bool = True) -> bool:
        """
        修复文件中的日期计算错误
        
        Args:
            file_path: 文件路径
            backup: 是否创建备份
            
        Returns:
            是否修复成功
        """
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建备份
            if backup:
                backup_path = f"{file_path}.backup"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"备份文件已创建: {backup_path}")
            
            # 修复常见的日期计算错误
            fixes = [
                # 修复 replace(day=day+30) 错误
                (
                    r'current_time\.replace\(day=current_time\.day \+ (\d+)\)',
                    r'(current_time + timedelta(days=\1))'
                ),
                # 修复其他可能的 replace 错误
                (
                    r'\.replace\(day=.*?\.day \+ (\d+)\)',
                    r' + timedelta(days=\1)'
                ),
                # 确保导入了 timedelta
                (
                    r'from datetime import datetime$',
                    r'from datetime import datetime, timedelta'
                )
            ]
            
            import re
            modified = False
            
            for pattern, replacement in fixes:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    modified = True
                    print(f"应用修复: {pattern} -> {replacement}")
            
            # 写回文件
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"文件已修复: {file_path}")
                return True
            else:
                print(f"文件无需修复: {file_path}")
                return False
                
        except Exception as e:
            print(f"修复失败: {e}")
            return False

def test_safe_date_calculator():
    """测试安全日期计算器"""
    print("🗓️ 测试安全日期计算器")
    
    calculator = SafeDateCalculator()
    
    # 测试正常日期
    test_date = datetime(2024, 6, 15)
    print(f"原始日期: {test_date.strftime('%Y年%m月%d日')}")
    
    # 测试添加天数
    future_date = calculator.add_days(test_date, 30)
    print(f"添加30天后: {future_date.strftime('%Y年%m月%d日')}")
    
    # 测试添加月份
    future_month = calculator.add_months(test_date, 1)
    print(f"添加1个月后: {future_month.strftime('%Y年%m月%d日')}")
    
    # 测试月末边界情况
    edge_date = datetime(2024, 1, 31)  # 1月31日
    edge_future = calculator.add_months(edge_date, 1)  # 应该变成2月29日（2024是闰年）
    print(f"月末测试: {edge_date.strftime('%Y年%m月%d日')} -> {edge_future.strftime('%Y年%m月%d日')}")
    
    # 测试安全随访日期
    follow_up = calculator.safe_follow_up_date(test_date, 30)
    print(f"随访日期: {follow_up}")

if __name__ == "__main__":
    test_safe_date_calculator()
    
    # 尝试修复 ultra_simple_emr.py 文件
    print("\n🔧 尝试修复 ultra_simple_emr.py 文件...")
    success = SafeDateCalculator.fix_date_calculation_in_file("ultra_simple_emr.py")
    if success:
        print("✅ 文件修复成功!")
    else:
        print("ℹ️ 文件无需修复或修复失败") 
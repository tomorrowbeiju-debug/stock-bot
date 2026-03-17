# 测试导入
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from app import app
    print("[OK] app.py 导入成功")
except Exception as e:
    print(f"[FAIL] app.py 导入失败: {e}")

try:
    from stock_analyzer import StockAnalyzer
    print("[OK] stock_analyzer.py 导入成功")
except Exception as e:
    print(f"[FAIL] stock_analyzer.py 导入失败: {e}")

try:
    from feishu_bot import FeishuBot
    print("[OK] feishu_bot.py 导入成功")
except Exception as e:
    print(f"[FAIL] feishu_bot.py 导入失败: {e}")

print("\n所有模块导入测试完成！")

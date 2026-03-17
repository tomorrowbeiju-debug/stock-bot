# 测试股票数据采集
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from stock_analyzer import StockAnalyzer

analyzer = StockAnalyzer()

print("测试获取股票数据...")

# 测试单只股票
stock_code = "sz000683"
print(f"\n获取 {stock_code} 数据...")
data = analyzer.get_stock_data(stock_code)

if data:
    print(f"股票名称: {data['name']}")
    print(f"当前价格: {data['current_price']}")
    print(f"涨跌幅: {data['change_percent']}%")
    print(f"成交量: {data['volume']}")
else:
    print("获取数据失败")

print("\n测试完成！")

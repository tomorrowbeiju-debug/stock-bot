import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class StockAnalyzer:
    """股票分析器 - 基于原有 PowerShell 逻辑改写"""

    def __init__(self):
        # 腾讯股票接口
        self.tencent_api = "http://qt.gtimg.cn/q="

    def get_stock_data(self, stock_code: str) -> Optional[Dict]:
        """
        获取股票实时数据
        stock_code 格式: sz000683 或 sh600000
        """
        try:
            url = f"{self.tencent_api}{stock_code}"
            response = requests.get(url, timeout=10)
            response.encoding = 'gbk'

            data = response.text
            if not data or '~' not in data:
                return None

            # 解析腾讯接口返回数据
            parts = data.split('~')

            stock_info = {
                'code': stock_code,
                'name': parts[1],
                'current_price': float(parts[3]) if parts[3] else 0,  # 当前价
                'close_price': float(parts[4]) if parts[4] else 0,   # 昨收
                'open_price': float(parts[5]) if parts[5] else 0,     # 今开
                'volume': float(parts[6]) if parts[6] else 0,         # 成交量(手)
                'amount': float(parts[37]) if parts[37] else 0,       # 成交额
                'high_price': float(parts[33]) if parts[33] else 0,  # 最高
                'low_price': float(parts[34]) if parts[34] else 0,   # 最低
                'date': parts[30],                                    # 日期
                'time': parts[31]                                     # 时间
            }

            # 计算涨跌幅
            if stock_info['close_price'] > 0:
                stock_info['change_percent'] = round(
                    (stock_info['current_price'] - stock_info['close_price']) / stock_info['close_price'] * 100, 2
                )
            else:
                stock_info['change_percent'] = 0

            return stock_info

        except Exception as e:
            print(f"获取股票数据失败: {e}")
            return None

    def get_historical_data(self, stock_code: str, days: int = 60) -> List[Dict]:
        """
        获取历史数据用于计算技术指标
        使用东方财富接口
        """
        try:
            # 转换代码格式: sz000683 -> 0.000683, sh600000 -> 1.600000
            if stock_code.startswith('sz'):
                fs_code = f"0.{stock_code[2:]}"
            else:
                fs_code = f"1.{stock_code[2:]}"

            # 东方财富 K线接口
            url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get"
            params = {
                'secid': fs_code,
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58',
                'klt': '101',  # 日K
                'fqt': '1',    # 前复权
                'end': '20500101',
                'lmt': days
            }

            response = requests.get(url, params=params, timeout=10)
            result = response.json()

            if result.get('data') and result['data'].get('klines'):
                klines = result['data']['klines']

                historical = []
                for kline in klines:
                    parts = kline.split(',')
                    historical.append({
                        'date': parts[0],
                        'open': float(parts[1]),
                        'close': float(parts[2]),
                        'high': float(parts[3]),
                        'low': float(parts[4]),
                        'volume': float(parts[5]),
                        'amount': float(parts[6])
                    })

                return historical

            return []

        except Exception as e:
            print(f"获取历史数据失败: {e}")
            return []

    def calculate_ma(self, data: List[Dict], period: int) -> float:
        """计算均线"""
        if len(data) < period:
            return 0

        closes = [d['close'] for d in data[:period]]
        return sum(closes) / period

    def calculate_rsi(self, data: List[Dict], period: int = 14) -> float:
        """计算 RSI"""
        if len(data) < period + 1:
            return 50

        gains = []
        losses = []

        for i in range(len(data) - 1, len(data) - period - 1, -1):
            change = data[i]['close'] - data[i-1]['close']
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    def analyze_stock(self, stock_code: str) -> Optional[Dict]:
        """
        完整的股票分析
        包含六层规则引擎
        """
        # 获取实时数据
        real_data = self.get_stock_data(stock_code)
        if not real_data:
            return None

        # 获取历史数据计算指标
        historical = self.get_historical_data(stock_code, days=60)
        if not historical:
            return real_data

        # 技术指标
        ma5 = self.calculate_ma(historical, 5)
        ma10 = self.calculate_ma(historical, 10)
        ma20 = self.calculate_ma(historical, 20)
        rsi = self.calculate_rsi(historical, 14)

        # 六层规则引擎
        analysis = {
            'stock_info': real_data,
            'indicators': {
                'ma5': round(ma5, 2),
                'ma10': round(ma10, 2),
                'ma20': round(ma20, 2),
                'rsi': rsi
            },
            'rules': self._apply_rules(real_data, ma5, ma10, ma20, rsi, historical)
        }

        return analysis

    def _apply_rules(self, stock: Dict, ma5: float, ma10: float, ma20: float,
                     rsi: float, historical: List[Dict]) -> Dict:
        """应用六层规则引擎"""

        # 第一层: 趋势判断
        trend = "中性"
        if ma5 > ma10 > ma20:
            trend = "多头趋势"
        elif ma5 < ma10 < ma20:
            trend = "空头趋势"
        elif ma5 > ma10 and ma10 < ma20:
            trend = "底部反弹"

        # 第二层: 强度判断
        strength = "中性"
        if rsi > 70:
            strength = "超买"
        elif rsi < 30:
            strength = "超卖"
        elif rsi > 50:
            strength = "强势"
        else:
            strength = "弱势"

        # 第三层: 量能判断
        volume_strength = "平量"
        if len(historical) >= 5:
            avg_volume = sum(h[:5]['volume'] for h in historical[:5]) / 5
            if stock['volume'] > avg_volume * 1.5:
                volume_strength = "放量"
            elif stock['volume'] < avg_volume * 0.7:
                volume_strength = "缩量"

        # 第四层: 市场阶段
        market_phase = "震荡"
        if stock['current_price'] > ma20 and ma5 > ma20:
            market_phase = "上涨"
        elif stock['current_price'] < ma20 and ma5 < ma20:
            market_phase = "下跌"
        elif stock['current_price'] > ma20 and ma5 < ma20:
            market_phase = "回调"
        elif stock['current_price'] < ma20 and ma5 > ma20:
            market_phase = "筑底"

        # 第五层: 主力行为
        major_behavior = "观察"
        if volume_strength == "放量" and stock['change_percent'] > 0:
            major_behavior = "买入"
        elif volume_strength == "放量" and stock['change_percent'] < 0:
            major_behavior = "卖出"

        # 第六层: 操作建议
        suggestion = "持有观望"
        if trend == "多头趋势" and strength != "超买" and major_behavior == "买入":
            suggestion = "建议加仓"
        elif trend == "空头趋势" and strength == "超卖" and volume_strength == "缩量":
            suggestion = "关注反弹"
        elif strength == "超买" and trend != "多头趋势":
            suggestion = "建议减仓"
        elif trend == "底部反弹" and volume_strength == "放量":
            suggestion = "谨慎买入"

        return {
            'trend': trend,
            'strength': strength,
            'volume_strength': volume_strength,
            'market_phase': market_phase,
            'major_behavior': major_behavior,
            'suggestion': suggestion
        }

    def format_analysis_message(self, analysis: Dict) -> str:
        """格式化分析结果为飞书消息"""

        stock = analysis['stock_info']
        indicators = analysis['indicators']
        rules = analysis['rules']

        # 价格颜色
        price_color = "🔴" if stock['change_percent'] >= 0 else "🟢"

        message = f"""
📊 **{stock['name']} ({stock['code']})**

**当前价格**: {price_color} ¥{stock['current_price']} ({stock['change_percent']:+.2f}%)
**今开**: ¥{stock['open_price']} | **昨收**: ¥{stock['close_price']}
**最高**: ¥{stock['high_price']} | **最低**: ¥{stock['low_price']}
**成交量**: {stock['volume']} 手 | **成交额**: {stock['amount']/10000:.1f} 亿

---
**📈 技术指标**
MA5: {indicators['ma5']} | MA10: {indicators['ma10']} | MA20: {indicators['ma20']}
RSI(14): {indicators['rsi']}

---
**🎯 六层规则分析**
1️⃣ 趋势: {rules['trend']}
2️⃣ 强度: {rules['strength']}
3️⃣ 量能: {rules['volume_strength']}
4️⃣ 阶段: {rules['market_phase']}
5️⃣ 主力: {rules['major_behavior']}

---
**💡 操作建议**: **{rules['suggestion']}**

🕐 更新时间: {stock['date']} {stock['time']}
"""

        return message

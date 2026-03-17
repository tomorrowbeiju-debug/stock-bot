from flask import Flask, request, jsonify
import json
import threading
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from stock_analyzer import StockAnalyzer
from feishu_bot import FeishuBot

# 配置信息
# 飞书群机器人 Webhook（简单方式，不需要企业认证）
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/4da51e25-fafe-4c4c-b337-7792fbeef237"
DEFAULT_STOCKS = ["sz000683", "sz300498", "sh510720"]

app = Flask(__name__)

# 初始化组件
analyzer = StockAnalyzer()
bot = FeishuBot(None, None)  # Webhook 方式不需要 app_id 和 secret

# 监控的股票列表
watched_stocks = DEFAULT_STOCKS.copy()

# 飞书群 Open ID（需要配置）
FEISHU_GROUP_OPEN_ID = ""

# 定时任务调度器
scheduler = BackgroundScheduler()

def is_stock_command(text: str) -> bool:
    """判断是否是股票分析命令"""
    stock_keywords = ["分析", "看盘", "股票", "复盘", "持仓", "监控", "代码"]

    text_lower = text.lower()
    for keyword in stock_keywords:
        if keyword in text:
            return True

    return False

def parse_stock_code(text: str) -> str:
    """从文本中提取股票代码"""
    # 常见格式: sz000683, sh600000, 000683, 600000
    import re

    # 匹配 6 位数字
    match = re.search(r'\d{6}', text)
    if match:
        code = match.group()

        # 判断市场
        if 'sz' in text.lower():
            return f"sz{code}"
        elif 'sh' in text.lower():
            return f"sh{code}"
        else:
            # 根据代码前缀判断
            if code.startswith('0') or code.startswith('3'):
                return f"sz{code}"
            elif code.startswith('6'):
                return f"sh{code}"
            else:
                return f"sz{code}"  # 默认深市

    return None

def analyze_and_reply(stock_code: str, reply_to_open_id: str, group_open_id: str = None):
    """分析股票并回复"""

    print(f"[{datetime.now()}] 开始分析股票: {stock_code}")

    # 分析股票
    analysis = analyzer.analyze_stock(stock_code)

    if not analysis:
        message = f"❌ 无法获取股票 {stock_code} 的数据，请检查代码是否正确"
    else:
        message = analyzer.format_analysis_message(analysis)

    # 发送消息（使用 Webhook）
    success = bot.send_via_webhook(message)

    if success:
        print(f"[{datetime.now()}] 消息发送成功")
    else:
        print(f"[{datetime.now()}] 消息发送失败")

def analyze_all_stocks(target_open_id: str):
    """分析所有监控的股票"""

    print(f"[{datetime.now()}] 开始分析所有股票: {watched_stocks}")

    # 生成汇总消息
    summary_lines = ["📊 **股票监控日报**\n"]

    for stock_code in watched_stocks:
        analysis = analyzer.analyze_stock(stock_code)

        if analysis:
            stock = analysis['stock_info']
            rules = analysis['rules']

            price_color = "🔴" if stock['change_percent'] >= 0 else "🟢"

            line = f"""
**{stock['name']}** ({stock['code']})
{price_color} ¥{stock['current_price']} ({stock['change_percent']:+.2f}%)
建议: {rules['suggestion']}
"""
            summary_lines.append(line)
        else:
            summary_lines.append(f"\n❌ {stock_code} 数据获取失败")

        # 避免发送太快
        time.sleep(1)

    summary_lines.append(f"\n🕐 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    summary = "\n".join(summary_lines)

    # 发送汇总消息（使用 Webhook）
    bot.send_via_webhook(summary)

from flask import Response
import json

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """飞书事件回调"""

    # GET 请求用于验证
    if request.method == 'GET':
        return jsonify({"status": "ok"})

    # 获取请求数据
    data = request.get_json()

    # 如果没有数据，返回空响应
    if not data:
        return jsonify({"code": 0})

    print(f"[{datetime.now()}] 收到飞书事件: {json.dumps(data, ensure_ascii=False)}")

    # 检查是否是验证请求
    if data.get('type') == 'url_verification':
        challenge = data.get('challenge')
        response = Response(
            json.dumps({'challenge': challenge}),
            mimetype='application/json'
        )
        return response

    # 检查是否是消息事件
    header = data.get('header', {})
    if header.get('event_type') == 'im.message.receive_v1':

        try:
            # 直接解析 JSON
            event_data = data.get('event', {})

            # 获取消息内容
            message = event_data.get('message', {})
            msg_type = message.get('message_type')

            # 消息类型检查
            if msg_type != 'text':
                print(f"忽略非文本消息类型: {msg_type}")
                return jsonify({"code": 0})

            # 解析消息内容
            content = json.loads(message.get('content', '{}'))
            text = content.get('text', '').strip()

            print(f"[{datetime.now()}] 收到消息: {text}")

            # 检查是否是股票命令
            if not is_stock_command(text):
                print("不是股票相关命令，忽略")
                return jsonify({"code": 0})

            # 获取发送者 ID
            sender = event_data.get('sender', {})
            sender_id = sender.get('sender_id', {})
            reply_to = sender_id.get('open_id')

            if not reply_to:
                print("无法获取发送者 ID")
                return jsonify({"code": 0})

            # 提取股票代码
            stock_code = parse_stock_code(text)

            if stock_code:
                # 分析指定股票
                threading.Thread(
                    target=analyze_and_reply,
                    args=(stock_code, reply_to)
                ).start()
            else:
                # 分析所有股票
                threading.Thread(
                    target=analyze_all_stocks,
                    args=(reply_to,)
                ).start()

        except Exception as e:
            print(f"处理消息异常: {e}")

    return jsonify({"code": 0})

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})

@app.route('/api/analyze', methods=['GET', 'POST'])
def api_analyze():
    """
    股票分析 API 接口
    用于 OpenClaw 调用获取实时股票数据
    
    使用方式:
    - GET: /api/analyze?code=sz000683
    - POST: /api/analyze {"code": "sz000683"}
    
    返回: JSON 格式的股票分析数据
    """
    # 获取股票代码
    stock_code = None
    
    if request.method == 'GET':
        stock_code = request.args.get('code')
    else:
        data = request.get_json()
        if data:
            stock_code = data.get('code')
    
    if not stock_code:
        return jsonify({
            "success": False,
            "error": "请提供股票代码，如: /api/analyze?code=sz000683"
        }), 400
    
    # 标准化股票代码
    stock_code = stock_code.strip().lower()
    if not stock_code.startswith(('sz', 'sh')):
        # 自动判断市场
        if stock_code.startswith('0') or stock_code.startswith('3'):
            stock_code = f"sz{stock_code}"
        elif stock_code.startswith('6'):
            stock_code = f"sh{stock_code}"
        else:
            stock_code = f"sz{stock_code}"
    
    print(f"[API] 分析股票: {stock_code}")
    
    try:
        # 获取实时数据
        stock_data = analyzer.get_stock_data(stock_code)
        
        if not stock_data:
            return jsonify({
                "success": False,
                "error": f"无法获取股票 {stock_code} 的数据"
            }), 404
        
        # 获取历史数据计算技术指标
        historical = analyzer.get_historical_data(stock_code, days=60)
        
        # 计算均线
        ma5 = analyzer.calculate_ma(historical, 5)
        ma10 = analyzer.calculate_ma(historical, 10)
        ma20 = analyzer.calculate_ma(historical, 20)
        
        # 计算 RSI
        rsi = analyzer.calculate_rsi(historical, 14)
        
        # 计算成交量变化
        volume_change = 0
        if len(historical) >= 2:
            avg_volume = sum(h['volume'] for h in historical[1:6]) / 5  # 前5日平均
            today_volume = historical[0]['volume'] if historical else 0
            if avg_volume > 0:
                volume_change = round((today_volume - avg_volume) / avg_volume * 100, 2)
        
        # 生成分析建议
        suggestion = "持有"
        reason_parts = []
        
        # 基于涨跌幅
        if stock_data['change_percent'] > 5:
            suggestion = "注意风险"
            reason_parts.append("涨幅较大，注意回调风险")
        elif stock_data['change_percent'] < -5:
            suggestion = "超跌关注"
            reason_parts.append("超跌，可能存在反弹机会")
        elif stock_data['change_percent'] > 0:
            suggestion = "看涨"
            reason_parts.append("小幅上涨")
        else:
            suggestion = "看跌"
            reason_parts.append("小幅下跌")
        
        # 基于均线位置
        if ma5 > ma20:
            suggestion = "看涨" if suggestion == "持有" else suggestion
            reason_parts.append("MA5 > MA20，多头排列")
        elif ma5 < ma20:
            suggestion = "看跌" if suggestion == "持有" else suggestion
            reason_parts.append("MA5 < MA20，空头排列")
        
        # 基于 RSI
        if rsi > 70:
            suggestion = "注意风险"
            reason_parts.append(f"RSI={rsi:.0f}，超买区域")
        elif rsi < 30:
            suggestion = "超跌关注"
            reason_parts.append(f"RSI={rsi:.0f}，超卖区域")
        
        # 基于量能
        if volume_change > 30:
            reason_parts.append(f"成交量放大 {volume_change}%")
        elif volume_change < -30:
            reason_parts.append(f"成交量萎缩 {abs(volume_change)}%")
        
        return jsonify({
            "success": True,
            "data": {
                "code": stock_data['code'],
                "name": stock_data['name'],
                "current_price": stock_data['current_price'],
                "change_percent": stock_data['change_percent'],
                "volume": stock_data['volume'],
                "amount": stock_data['amount'],
                "open": stock_data.get('open_price', 0),
                "high": stock_data.get('high_price', 0),
                "low": stock_data.get('low_price', 0),
                "prev_close": stock_data.get('close_price', 0),
                # 新增技术指标
                "ma5": round(ma5, 2) if ma5 else 0,
                "ma10": round(ma10, 2) if ma10 else 0,
                "ma20": round(ma20, 2) if ma20 else 0,
                "rsi": round(rsi, 1) if rsi else 50,
                "volume_change": volume_change,
                # 建议
                "suggestion": suggestion,
                "reason": "；".join(reason_parts),
                "update_time": stock_data.get('time', '')
            }
        })
        
    except Exception as e:
        import traceback
        print(f"[API] 分析错误: {e}")
        print(f"[API] 堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": f"分析股票时出错: {str(e)}"
        }), 500
    
    return jsonify({
        "success": True,
        "data": {
            "code": stock['code'],
            "name": stock['name'],
            "current_price": stock['current_price'],
            "change_percent": stock['change_percent'],
            "volume": stock['volume'],
            "amount": stock['amount'],
            "open": stock.get('open_price', 0),
            "high": stock.get('high_price', 0),
            "low": stock.get('low_price', 0),
            "prev_close": stock.get('close_price', 0),
            "suggestion": rules['suggestion'],
            "reason": rules['reason'],
            "update_time": stock.get('time', '')
        }
    })

def scheduled_morning_analysis():
    """早盘分析任务 (9:00)"""

    print(f"[{datetime.now()}] 执行早盘分析任务")

    if FEISHU_GROUP_OPEN_ID:
        analyze_all_stocks(FEISHU_GROUP_OPEN_ID)

def scheduled_evening_analysis():
    """收盘分析任务 (15:05)"""

    print(f"[{datetime.now()}] 执行收盘分析任务")

    if FEISHU_GROUP_OPEN_ID:
        analyze_all_stocks(FEISHU_GROUP_OPEN_ID)

def start_scheduler():
    """启动定时任务"""

    # 早盘分析: 每天 9:00
    scheduler.add_job(
        scheduled_morning_analysis,
        'cron',
        hour=9,
        minute=0,
        id='morning_analysis'
    )

    # 收盘分析: 每天 15:05
    scheduler.add_job(
        scheduled_evening_analysis,
        'cron',
        hour=15,
        minute=5,
        id='evening_analysis'
    )

    scheduler.start()
    print("定时任务已启动")

if __name__ == '__main__':
    # 启动定时任务
    start_scheduler()

    # 启动 Flask 服务
    print(f"股票助手服务启动中...")
    print(f"默认监控股票: {watched_stocks}")
    print(f"服务地址: http://0.0.0.0:5000")

    app.run(host='0.0.0.0', port=5000)

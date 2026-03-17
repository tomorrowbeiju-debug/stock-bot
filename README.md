# 🦞 股票助手 - 飞书机器人

基于飞书机器人 + 六层规则引擎的股票分析助手，支持实时分析和定时推送。

## 功能特点

- ✅ 实时股票行情采集（腾讯/东方财富接口）
- ✅ 技术指标计算（MA5/10/20、RSI14）
- ✅ 六层规则引擎分析（趋势/强度/量能/阶段/主力/风险）
- ✅ 飞书群实时对话
- ✅ 定时推送（开盘前 9:00、收盘后 15:05）
- ✅ 云端部署（Railway 24小时运行）

## 本地测试

### 1. 安装依赖

```bash
cd stock_bot
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填入你的配置：

```bash
cp .env.example .env
```

### 3. 启动服务

```bash
python app.py
```

服务启动后会在 `http://localhost:5000` 运行。

### 4. 测试消息

在飞书群里发送：
- `@机器人 分析 sz000683` - 分析指定股票
- `@机器人 分析` - 分析所有监控股票
- `@机器人 持仓` - 查看持仓分析

## 部署到 Railway

### 方法 1: GitHub + Railway（推荐）

1. 将代码推送到 GitHub 仓库
2. 登录 [Railway](https://railway.app)
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择你的仓库
5. Railway 会自动检测并部署

### 方法 2: Railway CLI

```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
railway init

# 部署
railway up
```

### 部署后配置

1. 获取 Railway 分配的公网 URL
2. 在飞书开放平台配置 Webhook URL（如果用 HTTP 模式）
3. 设置环境变量 `FEISHU_GROUP_OPEN_ID`（定时推送目标群）

## 获取飞书群 Open ID

1. 在群里发一条消息
2. 通过飞书 API 或日志查看消息事件的 sender_id
3. 记录该 open_id 并配置到环境变量

## 六层规则引擎

| 层级 | 判断维度 | 说明 |
|------|---------|------|
| 1️⃣ | 趋势 | 多头/空头/反弹/回调 |
| 2️⃣ | 强度 | RSI 超买/超卖/强势/弱势 |
| 3️⃣ | 量能 | 放量/缩量/平量 |
| 4️⃣ | 阶段 | 上涨/下跌/震荡/筑底 |
| 5️⃣ | 主力 | 买入/卖出/观察 |
| 6️⃣ | 建议 | 加仓/减仓/持有/观望 |

## 项目结构

```
stock_bot/
├── app.py                 # 主应用
├── stock_analyzer.py      # 股票分析核心
├── feishu_bot.py          # 飞书机器人客户端
├── requirements.txt       # 依赖
├── Dockerfile             # Docker 配置
├── railway.json          # Railway 配置
└── .env.example          # 环境变量示例
```

## 常见问题

### Q: 收不到机器人回复？

A: 检查以下几点：
- 飞书应用权限是否已开通（`im:message` 等）
- 机器人是否已加入群
- 消息中是否包含股票相关关键词（分析/看盘/股票等）

### Q: 定时推送不生效？

A:
- 确认环境变量 `FEISHU_GROUP_OPEN_ID` 已正确配置
- 检查 Railway 服务是否正常运行
- 查看日志是否有错误信息

### Q: 股票数据获取失败？

A:
- 检查股票代码格式（sz000683 或 sh600000）
- 确认交易时间内（9:30-15:00 数据更及时）
- 非交易时间可能获取延迟或失败

## 免责声明

本工具仅提供数据分析，不构成投资建议。投资有风险，入市需谨慎。

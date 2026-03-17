FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY stock_analyzer.py .
COPY feishu_bot.py .
COPY app.py .
COPY .env.example .env

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["python", "app.py"]

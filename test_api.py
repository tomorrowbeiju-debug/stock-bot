import requests
import json

# 测试东方财富 K 线接口
url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
params = {
    'secid': '0.300498',  # sz300498 -> 0.300498
    'fields1': 'f1,f2,f3,f4,f5,f6',
    'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58',
    'klt': '101',  # 日K
    'fqt': '1',    # 前复权
    'end': '20500101',
    'lmt': 30
}

try:
    response = requests.get(url, params=params, timeout=10)
    print("Status:", response.status_code)
    print("Response:", response.text[:1000])
except Exception as e:
    print("Error:", e)

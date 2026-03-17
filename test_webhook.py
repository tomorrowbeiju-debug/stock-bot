import requests
import json

# 飞书群机器人 Webhook
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/4da51e25-fafe-4c4c-b337-7792fbeef237"

def send_test_message():
    """测试发送 Webhook 消息"""
    try:
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {
            "msg_type": "text",
            "content": {
                "text": "[Test] Stock bot Webhook connection OK!"
            }
        }

        print(f"Sending request to: {WEBHOOK_URL}")
        response = requests.post(WEBHOOK_URL, headers=headers, json=data, timeout=10)
        result = response.json()

        print(f"Response: {result}")

        if result.get("code") == 0:
            print("SUCCESS - Message sent!")
            return True
        else:
            print(f"FAILED: {result.get('msg')}")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    send_test_message()

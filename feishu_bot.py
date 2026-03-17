import requests
import json
import time

# 群机器人 Webhook URL（简单方式，不需要企业认证）
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/4da51e25-fafe-4c4c-b337-7792fbeef237"

class FeishuBot:
    """飞书机器人 - 支持群机器人 Webhook"""

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.tenant_access_token = None
        self.token_expires_at = 0

    def _get_tenant_access_token(self) -> str:
        """获取租户访问令牌"""
        # 检查 token 是否有效
        if self.tenant_access_token and time.time() < self.token_expires_at:
            return self.tenant_access_token

        try:
            url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
            headers = {"Content-Type": "application/json; charset=utf-8"}
            data = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }

            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()

            if result.get("code") == 0:
                self.tenant_access_token = result.get("tenant_access_token")
                # 提前5分钟过期
                self.token_expires_at = time.time() + result.get("expire", 7200) - 300
                return self.tenant_access_token
            else:
                print(f"获取令牌失败: {result.get('msg')}")
                return None

        except Exception as e:
            print(f"获取令牌异常: {e}")
            return None

    def _send_request(self, method: str, url: str, data: dict = None) -> dict:
        """发送 API 请求"""
        token = self._get_tenant_access_token()
        if not token:
            return {"code": -1, "msg": "No token"}

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                return {"code": -1, "msg": "Invalid method"}

            return response.json()

        except Exception as e:
            print(f"请求异常: {e}")
            return {"code": -1, "msg": str(e)}

    def send_message(self, receive_id: str, content: str, msg_type: str = "text") -> bool:
        """发送消息到飞书"""

        # 构建消息内容
        if msg_type == "text":
            msg_content = json.dumps({"text": content})
        else:
            msg_content = content

        url = f"{self.base_url}/im/v1/messages"
        params = {
            "receive_id_type": "open_id"
        }

        data = {
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": msg_content
        }

        result = self._send_request("POST", url, data)

        if result.get("code") == 0:
            return True
        else:
            print(f"发送消息失败: {result.get('msg')}")
            return False

    def send_text_message(self, receive_id: str, text: str) -> bool:
        """发送文本消息（快捷方式）"""
        return self.send_message(receive_id, text, "text")

    def send_rich_text_message(self, receive_id: str, title: str, content: str) -> bool:
        """发送富文本消息"""

        # 构建富文本内容
        rich_text = {
            "title": title,
            "content": [
                [
                    {
                        "tag": "text",
                        "text": content
                    }
                ]
            ]
        }

        url = f"{self.base_url}/im/v1/messages"
        params = {
            "receive_id_type": "open_id"
        }

        data = {
            "receive_id": receive_id,
            "msg_type": "post",
            "content": json.dumps(rich_text)
        }

        result = self._send_request("POST", url, data)

        if result.get("code") == 0:
            return True
        else:
            print(f"发送富文本消息失败: {result.get('msg')}")
            return False

    def send_via_webhook(self, text: str) -> bool:
        """使用群机器人 Webhook 发送消息（简单方式）"""
        try:
            headers = {"Content-Type": "application/json; charset=utf-8"}
            data = {
                "msg_type": "text",
                "content": {
                    "text": text
                }
            }

            response = requests.post(WEBHOOK_URL, headers=headers, json=data, timeout=10)
            result = response.json()

            if result.get("code") == 0:
                print("Webhook 消息发送成功")
                return True
            else:
                print(f"Webhook 发送失败: {result.get('msg')}")
                return False

        except Exception as e:
            print(f"Webhook 请求异常: {e}")
            return False

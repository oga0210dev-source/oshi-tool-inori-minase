import os
import requests


WEBHOOK_ENV_MAP = {
    "INQUIRY": "DISCORD_INQUIRY_WEBHOOK_URL",
    "REQUEST": "DISCORD_REQUEST_WEBHOOK_URL",
    "BUG": "DISCORD_BUG_WEBHOOK_URL",
    "TODO": "DISCORD_TODO_WEBHOOK_URL",
}


def send_inquiry_notification(
    inquiry_id,
    inquiry_type,
    subject,
    message,
    user_id,
    email=None
):
    env_name = WEBHOOK_ENV_MAP.get(inquiry_type)

    if not env_name:
        raise ValueError(f"未対応の問い合わせ種別です: {inquiry_type}")

    webhook_url = os.getenv(env_name)

    if not webhook_url:
        raise ValueError(
            f"Discord Webhook URLが設定されていません: {env_name}"
        )

    type_name = {
        "INQUIRY": "📩 問い合わせ",
        "REQUEST": "💡 要望",
        "BUG": "🐛 バグ報告",
        "TODO": "📋 ToDo",
    }.get(inquiry_type, inquiry_type)

    content = f"""**{type_name}**

**問い合わせID：** #{inquiry_id}
**ユーザーID：** {user_id}
**件名：** {subject}
"""

    if email:
        content += f"**メールアドレス：** {email}\n"

    content += f"""
**内容：**
{message}

**ステータス：** 未対応
"""

    response = requests.post(
        webhook_url,
        json={
            "content": content
        },
        timeout=10
    )

    if response.status_code < 200 or response.status_code >= 300:
        raise RuntimeError(
            f"Discord通知に失敗しました: "
            f"HTTP {response.status_code} / {response.text}"
        )


def send_todo_reminder(todos):
    webhook_url = os.getenv("DISCORD_TODO_WEBHOOK_URL")

    if not webhook_url:
        raise ValueError(
            "Discord Webhook URLが設定されていません: "
            "DISCORD_TODO_WEBHOOK_URL"
        )

    base_url = os.getenv("BASE_URL")

    if not base_url:
        raise ValueError(
            "BASE_URLが設定されていません。"
        )

    content = f"""**📋 ToDoリマインド**

現在、未対応・対応中のToDoが **{len(todos)}件** あります。

"""

    for todo in todos:
        if todo["status"] == "UNRESOLVED":
            status_name = "🔴 未対応"
        elif todo["status"] == "IN_PROGRESS":
            status_name = "🟡 対応中"
        else:
            status_name = todo["status"]

        detail_url = (
            f"{base_url}/admin/inquiry/{todo['inquiry_id']}"
        )

        content += (
            f"- {status_name} "
            f"[#{todo['inquiry_id']} {todo['subject']}]"
            f"({detail_url})\n"
        )

    content += f"""
[お問い合わせ管理を開く]({base_url}/admin/inquiry)
"""

    response = requests.post(
        webhook_url,
        json={
            "content": content
        },
        timeout=10
    )

    if response.status_code < 200 or response.status_code >= 300:
        raise RuntimeError(
            f"Discord ToDoリマインドに失敗しました: "
            f"HTTP {response.status_code} / {response.text}"
        )

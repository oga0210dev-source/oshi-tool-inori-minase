from python.core import database
from python.services.inquiry_service import get_active_todos
from python.services.discord_service import send_todo_reminder


def main():
    conn = database.get_connection()

    try:
        todos = get_active_todos(conn)

        if not todos:
            print("未対応・対応中のToDoはありません。")
            return

        send_todo_reminder(todos)

        print(f"ToDoリマインドを送信しました。対象: {len(todos)}件")

    finally:
        conn.close()


if __name__ == "__main__":
    main()

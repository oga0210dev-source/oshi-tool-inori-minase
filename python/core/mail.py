import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mail:

    @staticmethod
    def send(
            to_email: str,
            subject: str,
            html: str
    ) -> bool:
        """Gmail SMTPを利用してメールを送信する"""

        mail_username = os.getenv("MAIL_USERNAME")
        mail_password = os.getenv("MAIL_PASSWORD")
        mail_from = os.getenv("MAIL_FROM")

        if not mail_username:
            raise RuntimeError(
                "MAIL_USERNAMEが設定されていません。"
            )

        if not mail_password:
            raise RuntimeError(
                "MAIL_PASSWORDが設定されていません。"
            )

        if not mail_from:
            raise RuntimeError(
                "MAIL_FROMが設定されていません。"
            )

        message = MIMEMultipart("alternative")

        message["From"] = mail_from
        message["To"] = to_email
        message["Subject"] = subject

        message.attach(
            MIMEText(
                html,
                "html",
                "utf-8"
            )
        )

        try:
            with smtplib.SMTP_SSL(
                "smtp.gmail.com",
                465
            ) as server:

                server.login(
                    mail_username,
                    mail_password
                )

                server.sendmail(
                    mail_from,
                    to_email,
                    message.as_string()
                )

        except Exception as e:
            raise RuntimeError(
                f"メール送信に失敗しました。: {e}"
            ) from e

        return True

import os
import bcrypt

from itsdangerous import URLSafeTimedSerializer


class Security:

    @staticmethod
    def hash_password(password: str) -> str:
        """パスワードをハッシュ化する"""

        hashed = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(
            password: str,
            hashed_password: str
    ) -> bool:
        """パスワードを照合する"""

        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    @staticmethod
    def _get_email_token_serializer():
        """メール認証トークン用Serializerを取得"""

        secret = os.getenv("EMAIL_TOKEN_SECRET")

        if not secret:
            raise RuntimeError(
                "EMAIL_TOKEN_SECRETが設定されていません。"
            )

        return URLSafeTimedSerializer(secret)

    @staticmethod
    def generate_email_verification_token(
            user_id: str,
            email: str
    ) -> str:
        """メール認証トークンを生成"""

        serializer = Security._get_email_token_serializer()

        return serializer.dumps({
            "user_id": user_id,
            "email": email
        })

    @staticmethod
    def verify_email_verification_token(
            token: str,
            max_age: int = 86400
    ):
        """
        メール認証トークンを検証

        max_age:
            86400秒 = 24時間
        """

        serializer = Security._get_email_token_serializer()

        try:
            return serializer.loads(
                token,
                max_age=max_age
            )

        except Exception:
            return None

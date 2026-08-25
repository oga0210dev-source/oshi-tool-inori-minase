from python.core.database import get_connection
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import render, auth

router = APIRouter()


@router.get("/mypage/public-setting")
def public_setting(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login")

    setting = PublicSettingModel.get(user_id)

    return render(
        request=request,
        name="templates/mypage/public_setting.html",
        context={
            "setting": setting
        }
    )


@router.post("/mypage/public-setting")
def update_public_setting(
        request: Request,
        gender_public: int = Form(...),
        birthday_public: int = Form(...),
        age_public: int = Form(...),
        member_since_public: int = Form(...),
        prefecture_public: int = Form(...),
        sns_public: int = Form(...),
        live_public: int = Form(...),
        meeting_public: int = Form(...)
):
    user_id = request.session.get("user_id")

    # ログイン確認
    if not auth.is_login(request):
        return RedirectResponse("/login", status_code=303)

    PublicSettingModel.update(
        user_id,
        gender_public,
        birthday_public,
        age_public,
        member_since_public,
        prefecture_public,
        sns_public,
        live_public,
        meeting_public
    )

    return RedirectResponse(
        "/mypage",
        status_code=303
    )


class PublicSettingModel:

    @staticmethod
    def get(user_id):
        """
        公開設定取得
        """
        conn = get_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        user_id,
                        gender_public,
                        birthday_public,
                        age_public,
                        member_since_public,
                        prefecture_public,
                        sns_public,
                        live_public,
                        meeting_public
                    FROM m_user_public_setting
                    WHERE user_id = %s
                    """,
                    (user_id,)
                )

                return cur.fetchone()

        finally:
            conn.close()

    @staticmethod
    def create(user_id):
        """
        公開設定初期登録
        """
        conn = get_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO m_user_public_setting (
                        user_id
                    )
                    VALUES (%s)
                    ON CONFLICT (user_id) DO NOTHING
                    """,
                    (user_id,)
                )

            conn.commit()

        finally:
            conn.close()

    @staticmethod
    def update(
            user_id,
            gender_public,
            birthday_public,
            age_public,
            member_since_public,
            prefecture_public,
            sns_public,
            live_public,
            meeting_public
    ):
        """
        公開設定更新
        """
        conn = get_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE m_user_public_setting
                    SET
                        gender_public = %s,
                        birthday_public = %s,
                        age_public = %s,
                        member_since_public = %s,
                        prefecture_public = %s,
                        sns_public = %s,
                        live_public = %s,
                        meeting_public = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                    """,
                    (
                        gender_public,
                        birthday_public,
                        age_public,
                        member_since_public,
                        prefecture_public,
                        sns_public,
                        live_public,
                        meeting_public,
                        user_id
                    )
                )

            conn.commit()

        finally:
            conn.close()

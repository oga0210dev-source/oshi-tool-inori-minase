from starlette.middleware.base import BaseHTTPMiddleware

from python.core.auth import update_last_access
from python.models.daily_access import DailyAccessModel
from python.services.discord_service import (
    send_daily_access_threshold_notification
)


class UserAccessMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        response = await call_next(request)

        # 最終アクセス日時更新
        update_last_access(request)

        # 静的ファイルはアクセス集計対象外
        if request.url.path.startswith("/static/"):
            return response

        # 日別アクセス記録
        user_id = request.session.get("user_id")
        role = request.session.get("role")

        if user_id and role != "admin":

            result = DailyAccessModel.record_access(user_id)

            for threshold in result["reached_thresholds"]:
                send_daily_access_threshold_notification(
                    access_date=result["access_date"],
                    unique_user_count=result["unique_user_count"],
                    threshold=threshold
                )

                DailyAccessModel.save_notification(
                    access_date=result["access_date"],
                    threshold=threshold
                )

        return response

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from python.core import render
from python.models.admin.master import maintenance as maintenance_model


router = APIRouter(
    prefix="/maintenance",
    tags=["maintenance"]
)


@router.get("")
async def maintenance_page(request: Request):
    maintenance = maintenance_model.get_active_maintenance()

    return render(
        request=request,
        name="templates/commons/maintenance/index.html",
        context={
            "maintenance": maintenance[0] if maintenance else None
        }
    )


@router.get("/return")
async def maintenance_return(request: Request):
    """
    メンテナンス終了後の戻り先判定
    """

    role = request.session.get("role")

    # Adminは通常通り利用可能
    if role == "admin":
        return RedirectResponse(
            "/home",
            status_code=303
        )

    # まだメンテナンス中ならメンテナンス画面へ戻す
    if maintenance_model.is_maintenance():
        return RedirectResponse(
            "/maintenance",
            status_code=303
        )

    # ログイン済みならホーム
    if request.session.get("user_id"):
        return RedirectResponse(
            "/home",
            status_code=303
        )

    # 未ログインならTOP
    return RedirectResponse(
        "/",
        status_code=303
    )

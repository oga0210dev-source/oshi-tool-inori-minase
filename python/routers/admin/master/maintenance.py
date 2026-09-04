from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from python.core import render, auth

from python.models.admin.master import maintenance as maintenance_model
from python.models.admin.master import announcement as announcement_model


router = APIRouter(
    prefix="/admin/master/maintenance",
    tags=["admin_master_maintenance"]
)


JST = ZoneInfo("Asia/Tokyo")
UTC = ZoneInfo("UTC")


MAINTENANCE_TYPE_LIST = [
    {
        "value": "ALL",
        "label": "全体"
    },
    {
        "value": "PARTIAL",
        "label": "一部機能"
    }
]


MAINTENANCE_TARGET_LIST = [
    {
        "value": "LIVE",
        "label": "ライブ",
        "path": "/home/live"
    },
    {
        "value": "MEETING",
        "label": "町民集会",
        "path": "/home/meeting"
    },
    {
        "value": "OSHI",
        "label": "推し情報",
        "path": "/home/oshi"
    }
]


def parse_datetime(value):
    """
    フォーム入力の日本時間をUTCへ変換
    """

    if not value:
        return None

    dt = datetime.fromisoformat(value)

    return dt.replace(
        tzinfo=JST
    ).astimezone(
        UTC
    ).replace(
        tzinfo=None
    )


def to_jst(value):
    """
    DBのUTCを日本時間へ変換
    """

    if not value:
        return None

    return value.replace(
        tzinfo=UTC
    ).astimezone(
        JST
    )


def format_jst(value):
    """
    DBのUTCを日本時間の表示文字列へ変換
    """

    value = to_jst(value)

    if not value:
        return None

    return value.strftime(
        "%Y-%m-%d %H:%M"
    )


def convert_maintenance_to_jst(maintenance):
    """
    編集画面用に日時をUTCから日本時間へ変換
    """

    if not maintenance:
        return maintenance

    maintenance = dict(maintenance)

    maintenance["start_at"] = to_jst(
        maintenance.get("start_at")
    )
    maintenance["end_at"] = to_jst(
        maintenance.get("end_at")
    )

    return maintenance


def convert_maintenances_for_list(maintenances):
    """
    一覧表示用に日時をUTCから日本時間の文字列へ変換
    """

    result = []

    for maintenance in maintenances:
        maintenance = dict(maintenance)

        maintenance["start_at"] = format_jst(
            maintenance.get("start_at")
        )
        maintenance["end_at"] = format_jst(
            maintenance.get("end_at")
        )

        result.append(maintenance)

    return result


def is_valid_maintenance_target(target_key):
    """
    メンテナンス対象機能が正しいか判定
    """

    return any(
        target["value"] == target_key
        for target in MAINTENANCE_TARGET_LIST
    )


def get_form_context(maintenance=None, error=None):
    """
    メンテナンスフォーム用コンテキスト取得
    """

    if maintenance:
        maintenance = convert_maintenance_to_jst(
            maintenance
        )

    maintenance_announcements = (
        announcement_model.get_maintenance_announcement_list()
    )

    for announcement in maintenance_announcements:
        announcement["start_at"] = to_jst(
            announcement["start_at"]
        )
        announcement["end_at"] = to_jst(
            announcement["end_at"]
        )

    return {
        "error": error,
        "maintenance": maintenance,
        "maintenance_type_list": MAINTENANCE_TYPE_LIST,
        "maintenance_target_list": MAINTENANCE_TARGET_LIST,
        "maintenance_announcements": maintenance_announcements
    }


@router.get("")
async def maintenance_list(
        request: Request
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    if not auth.is_admin(request):
        return RedirectResponse(
            "/home",
            status_code=303
        )

    maintenances = maintenance_model.get_maintenance_list()

    maintenances = convert_maintenances_for_list(
        maintenances
    )

    return render(
        request=request,
        name="templates/admin/master/maintenance/index.html",
        context={
            "maintenances": maintenances
        }
    )


@router.get("/create")
async def maintenance_create_page(
        request: Request
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    if not auth.is_admin(request):
        return RedirectResponse(
            "/home",
            status_code=303
        )

    return render(
        request=request,
        name="templates/admin/master/maintenance/form.html",
        context=get_form_context()
    )


@router.post("/create")
async def maintenance_create(
        request: Request,
        announcement_id: int = Form(None),
        maintenance_type: str = Form(...),
        target_key: str = Form(None),
        title: str = Form(...),
        message: str = Form(None),
        start_at: str = Form(None),
        end_at: str = Form(None),
        is_emergency: bool = Form(False)
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    if not auth.is_admin(request):
        return RedirectResponse(
            "/home",
            status_code=303
        )

    input_start_at = start_at
    input_end_at = end_at

    start_at = parse_datetime(start_at)
    end_at = parse_datetime(end_at)

    maintenance_data = {
        "announcement_id": announcement_id,
        "maintenance_type": maintenance_type,
        "target_key": target_key,
        "title": title,
        "message": message,
        "start_at": input_start_at,
        "end_at": input_end_at,
        "is_emergency": is_emergency,
        "is_active": False
    }

    if not title.strip():
        return render(
            request=request,
            name="templates/admin/master/maintenance/form.html",
            context=get_form_context(
                maintenance=maintenance_data,
                error="メンテナンス名を入力してください"
            )
        )

    if maintenance_type not in ["ALL", "PARTIAL"]:
        return render(
            request=request,
            name="templates/admin/master/maintenance/form.html",
            context=get_form_context(
                maintenance=maintenance_data,
                error="メンテナンスタイプが正しくありません"
            )
        )

    if maintenance_type == "ALL":
        maintenance_data["target_key"] = None

    elif not target_key or not target_key.strip():
        return render(
            request=request,
            name="templates/admin/master/maintenance/form.html",
            context=get_form_context(
                maintenance=maintenance_data,
                error="対象機能を選択してください"
            )
        )

    elif not is_valid_maintenance_target(target_key):
        return render(
            request=request,
            name="templates/admin/master/maintenance/form.html",
            context=get_form_context(
                maintenance=maintenance_data,
                error="対象機能が正しくありません"
            )
        )

    # 通常メンテナンスは告知必須
    if not is_emergency and not announcement_id:
        return render(
            request=request,
            name="templates/admin/master/maintenance/form.html",
            context=get_form_context(
                maintenance=maintenance_data,
                error="通常メンテナンスではメンテナンス告知を指定してください"
            )
        )

    maintenance_data["start_at"] = start_at
    maintenance_data["end_at"] = end_at

    maintenance_model.create_maintenance(
        maintenance_data
    )

    return RedirectResponse(
        "/admin/master/maintenance",
        status_code=303
    )


@router.get("/edit/{maintenance_id}")
async def maintenance_edit_page(
        request: Request,
        maintenance_id: int
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    if not auth.is_admin(request):
        return RedirectResponse(
            "/home",
            status_code=303
        )

    maintenance = maintenance_model.get_maintenance_by_id(
        maintenance_id
    )

    if not maintenance:
        return RedirectResponse(
            "/admin/master/maintenance",
            status_code=303
        )

    return render(
        request=request,
        name="templates/admin/master/maintenance/form.html",
        context=get_form_context(
            maintenance=maintenance
        )
    )


@router.post("/update/{maintenance_id}")
async def maintenance_update(
        request: Request,
        maintenance_id: int,
        announcement_id: int = Form(None),
        maintenance_type: str = Form(...),
        target_key: str = Form(None),
        title: str = Form(...),
        message: str = Form(None),
        start_at: str = Form(None),
        end_at: str = Form(None),
        is_emergency: bool = Form(False)
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    if not auth.is_admin(request):
        return RedirectResponse(
            "/home",
            status_code=303
        )

    input_start_at = start_at
    input_end_at = end_at

    start_at = parse_datetime(start_at)
    end_at = parse_datetime(end_at)

    maintenance_data = {
        "announcement_id": announcement_id,
        "maintenance_type": maintenance_type,
        "target_key": target_key,
        "title": title,
        "message": message,
        "start_at": input_start_at,
        "end_at": input_end_at,
        "is_emergency": is_emergency
    }

    if not title.strip():
        return render(
            request=request,
            name="templates/admin/master/maintenance/form.html",
            context=get_form_context(
                maintenance=maintenance_data,
                error="メンテナンス名を入力してください"
            )
        )

    if maintenance_type not in ["ALL", "PARTIAL"]:
        return render(
            request=request,
            name="templates/admin/master/maintenance/form.html",
            context=get_form_context(
                maintenance=maintenance_data,
                error="メンテナンスタイプが正しくありません"
            )
        )

    if maintenance_type == "ALL":
        maintenance_data["target_key"] = None

    elif not target_key or not target_key.strip():
        return render(
            request=request,
            name="templates/admin/master/maintenance/form.html",
            context=get_form_context(
                maintenance=maintenance_data,
                error="対象機能を選択してください"
            )
        )

    elif not is_valid_maintenance_target(target_key):
        return render(
            request=request,
            name="templates/admin/master/maintenance/form.html",
            context=get_form_context(
                maintenance=maintenance_data,
                error="対象機能が正しくありません"
            )
        )

    # 通常メンテナンスは告知必須
    if not is_emergency and not announcement_id:
        return render(
            request=request,
            name="templates/admin/master/maintenance/form.html",
            context=get_form_context(
                maintenance=maintenance_data,
                error="通常メンテナンスではメンテナンス告知を指定してください"
            )
        )

    maintenance_data["start_at"] = start_at
    maintenance_data["end_at"] = end_at

    maintenance_model.update_maintenance(
        maintenance_id,
        maintenance_data
    )

    return RedirectResponse(
        "/admin/master/maintenance",
        status_code=303
    )


@router.post("/status/{maintenance_id}")
async def maintenance_status(
        request: Request,
        maintenance_id: int,
        is_active: bool = Form(...)
):
    if not auth.is_login(request):
        return RedirectResponse(
            "/login",
            status_code=303
        )

    if not auth.is_admin(request):
        return RedirectResponse(
            "/home",
            status_code=303
        )

    maintenance = maintenance_model.get_maintenance_by_id(
        maintenance_id
    )

    if not maintenance:
        return RedirectResponse(
            "/admin/master/maintenance",
            status_code=303
        )

    # ONにする場合のみ開始条件をチェック
    if is_active:
        if not maintenance_model.can_start_normal_maintenance(
            maintenance_id
        ):
            return RedirectResponse(
                f"/admin/master/maintenance/edit/{maintenance_id}",
                status_code=303
            )

    maintenance_model.update_maintenance_status(
        maintenance_id,
        is_active
    )

    return RedirectResponse(
        "/admin/master/maintenance",
        status_code=303
    )

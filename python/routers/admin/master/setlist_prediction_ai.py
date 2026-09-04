from fastapi import APIRouter, Request

from python.core import auth, render
from python.services import (
    setlist_prediction_ai_service as prediction_ai_service
)


router = APIRouter(
    prefix="/admin/master/setlist-prediction-ai",
    tags=["admin_master_setlist_prediction_ai"]
)


@router.get("")
async def setlist_prediction_ai_list(
        request: Request
):
    # Adminのみ利用可能
    if not auth.is_admin(request):
        return {
            "success": False,
            "message": "権限がありません。"
        }

    lives = (
        prediction_ai_service
        .get_ai_prediction_live_list()
    )

    return render(
        request,
        "templates/admin/master/setlist_prediction_ai/list.html",
        {
            "request": request,
            "lives": lives
        }
    )


@router.get("/{live_id}")
async def setlist_prediction_ai_create(
        request: Request,
        live_id: int
):
    # Adminのみ利用可能
    if not auth.is_admin(request):
        return {
            "success": False,
            "message": "権限がありません。"
        }

    live = (
        prediction_ai_service
        .get_ai_prediction_target_live(
            live_id
        )
    )

    if not live:
        return {
            "success": False,
            "message": "LIVEが見つかりません。"
        }

    prediction = (
        prediction_ai_service
        .get_ai_prediction_by_live_id(
            live_id
        )
    )

    songs = (
        prediction_ai_service
        .get_ai_prediction_song_groups()
    )

    # テンプレートへ渡す既存予測をJSON化可能な形式に整形
    if prediction:
        prediction = {
            "prediction_id": prediction[
                "prediction_id"
            ],
            "live_id": prediction[
                "live_id"
            ],
            "prediction_context": prediction.get(
                "prediction_context"
            ),
            "admin_memo": prediction.get(
                "admin_memo"
            ),
            "public_flag": prediction.get(
                "public_flag",
                False
            ),
            "details": [
                {
                    "prediction_detail_id": detail[
                        "prediction_detail_id"
                    ],
                    "prediction_id": detail[
                        "prediction_id"
                    ],
                    "song_id": detail[
                        "song_id"
                    ],
                    "song_name": detail.get(
                        "song_name"
                    ),
                    "album_name": detail.get(
                        "album_name"
                    ),
                    "predicted_order": detail[
                        "predicted_order"
                    ],
                    "prediction_score": (
                        float(
                            detail[
                                "prediction_score"
                            ]
                        )
                        if detail[
                            "prediction_score"
                        ] is not None
                        else None
                    ),
                    "prediction_reason": detail.get(
                        "prediction_reason"
                    ),
                    "is_required": detail.get(
                        "is_required",
                        False
                    ),
                    "is_medley": detail.get(
                        "is_medley",
                        False
                    ),
                    "medley_order": detail.get(
                        "medley_order"
                    )
                }
                for detail in prediction.get(
                    "details",
                    []
                )
            ]
        }

    return render(
        request,
        "templates/admin/master/setlist_prediction_ai/create.html",
        {
            "request": request,
            "live": live,
            "songs": songs,
            "prediction": prediction
        }
    )


@router.post("/{live_id}/generate")
async def generate_setlist_prediction_ai(
        request: Request,
        live_id: int
):
    # Adminのみ利用可能
    if not auth.is_admin(request):
        return {
            "success": False,
            "message": "権限がありません。"
        }

    data = await request.json()

    prediction_context = data.get(
        "prediction_context"
    )

    admin_memo = data.get(
        "admin_memo"
    )

    required_song_ids = data.get(
        "required_song_ids",
        []
    )

    try:
        prediction = (
            prediction_ai_service
            .generate_ai_prediction(
                live_id=live_id,
                required_song_ids=(
                    required_song_ids
                ),
                prediction_context=(
                    prediction_context
                ),
                admin_memo=admin_memo
            )
        )
    except ValueError as error:
        return {
            "success": False,
            "message": str(error)
        }
    except Exception as error:
        import traceback

        traceback.print_exc()

        return {
            "success": False,
            "message": str(error)
        }

    if not prediction:
        return {
            "success": False,
            "message": (
                "予測を生成できませんでした。"
            )
        }

    details = prediction.get(
        "details",
        []
    )

    return {
        "success": True,
        "prediction_id": (
            prediction[
                "prediction_id"
            ]
        ),
        "live_id": (
            prediction[
                "live_id"
            ]
        ),
        "prediction_context": (
            prediction.get(
                "prediction_context"
            )
        ),
        "admin_memo": (
            prediction.get(
                "admin_memo"
            )
        ),
        "public_flag": (
            prediction.get(
                "public_flag",
                False
            )
        ),
        "predicted_setlist": [
            {
                "song_group_id": detail[
                    "song_id"
                ],
                "song_name": detail.get(
                    "song_name"
                ),
                "album_name": detail.get(
                    "album_name"
                ),
                "predicted_order": detail[
                    "predicted_order"
                ],
                "prediction_score": (
                    float(
                        detail[
                            "prediction_score"
                        ]
                    )
                    if detail[
                        "prediction_score"
                    ] is not None
                    else None
                ),
                "prediction_reason": detail.get(
                    "prediction_reason"
                ),
                "is_required": detail.get(
                    "is_required",
                    False
                ),
                "is_medley": detail.get(
                    "is_medley",
                    False
                ),
                "medley_order": detail.get(
                    "medley_order"
                )
            }
            for detail in details
        ]
    }

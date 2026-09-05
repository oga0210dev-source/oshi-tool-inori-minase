from collections import defaultdict
from datetime import date
import json

from python.services.gemini_service import gemini_service
from python.models.admin.master import (
    setlist as setlist_model,
    song as song_model,
    live as live_model,
    setlist_prediction_ai as prediction_ai_model
)


def get_ai_prediction_data(target_live):
    """
    AIセトリ予測用データを作成

    対象:
        - 対象LIVEより前のLIVE
        - LIVEのみ
        - INORI楽曲のみ

    集計:
        - 過去LIVE数
        - 平均楽曲数
        - 平均セトリ枠数
        - 同一ツアー公演数
        - 楽曲ごとの出演統計
        - メドレー統計
        - 直近LIVEのメドレー情報

    メドレー:
        - メドレー内の各楽曲は楽曲数として1曲ずつカウント
        - メドレー全体はセトリ枠として1枠
    """

    if not target_live:
        return None

    history = setlist_model.get_setlist_ai_history()

    # 対象LIVEより前の公演のみ
    history = [
        row
        for row in history
        if (
            row["live_date"],
            row["live_id"]
        )
        < (
            target_live["live_date"],
            target_live["live_id"]
        )
    ]

    # LIVE単位に整理
    live_setlist = defaultdict(list)

    for row in history:
        live_setlist[row["live_id"]].append(row)

    # 新しい公演順
    live_list = sorted(
        live_setlist.items(),
        key=lambda item: (
            max(
                song["live_date"]
                for song in item[1]
            ),
            item[0]
        ),
        reverse=True
    )

    total_live_count = len(live_list)

    # =========================================================
    # 過去LIVEの楽曲数・セトリ枠数
    # =========================================================

    setlist_song_counts = []
    setlist_slot_counts = []

    for live_id, songs in live_list:

        # 1公演内で同じ曲が複数行存在しても1曲として扱う
        unique_song_ids = {
            song["song_id"]
            for song in songs
        }

        setlist_song_counts.append(
            len(unique_song_ids)
        )

        # セトリ枠数
        # 通常曲 = 1枠
        # メドレー = 1枠
        slot_count = 0
        medley_song_orders = set()

        for song in songs:

            if song["is_medley"]:
                medley_song_orders.add(
                    song["song_order"]
                )
            else:
                slot_count += 1

        slot_count += len(
            medley_song_orders
        )

        setlist_slot_counts.append(
            slot_count
        )

    if setlist_song_counts:
        average_setlist_count = round(
            sum(setlist_song_counts)
            / len(setlist_song_counts)
        )
    else:
        average_setlist_count = 0

    if setlist_slot_counts:
        average_setlist_slot_count = round(
            sum(setlist_slot_counts)
            / len(setlist_slot_counts),
            1
        )
    else:
        average_setlist_slot_count = 0

    # =========================================================
    # 同一ツアーの公演
    # =========================================================

    tour_live_list = [
        item
        for item in live_list
        if (
            target_live.get("tour_name")
            and item[1][0]["tour_name"]
            == target_live["tour_name"]
        )
    ]

    tour_live_count = len(tour_live_list)

    # =========================================================
    # メドレー統計
    # =========================================================

    medley_live_count = 0
    medley_song_counts = []
    recent_medley_pattern = []

    for live_id, songs in live_list:

        # song_order単位でメドレーを判定
        medley_groups = defaultdict(list)

        for song in songs:

            if song["is_medley"]:
                medley_groups[
                    song["song_order"]
                ].append(song)

        has_medley = bool(
            medley_groups
        )

        if has_medley:
            medley_live_count += 1

            total_medley_song_count = 0

            for medley_songs in medley_groups.values():

                medley_song_ids = {
                    song["song_id"]
                    for song in medley_songs
                }

                total_medley_song_count += len(
                    medley_song_ids
                )

            medley_song_counts.append(
                total_medley_song_count
            )

        recent_medley_pattern.append(
            {
                "live_id": live_id,
                "live_date": str(
                    songs[0]["live_date"]
                ),
                "has_medley": has_medley,
                "medley_song_count": (
                    sum(
                        len(
                            {
                                song["song_id"]
                                for song in medley_songs
                            }
                        )
                        for medley_songs
                        in medley_groups.values()
                    )
                    if has_medley
                    else 0
                ),
                "medley_count": len(
                    medley_groups
                )
            }
        )

    if total_live_count > 0:
        medley_live_rate = round(
            medley_live_count
            / total_live_count
            * 100,
            1
        )
    else:
        medley_live_rate = 0

    if medley_song_counts:
        average_medley_song_count = round(
            sum(medley_song_counts)
            / len(medley_song_counts),
            1
        )
    else:
        average_medley_song_count = 0

    # 直近5公演
    recent_medley_pattern = (
        recent_medley_pattern[:5]
    )

    # =========================================================
    # 過去LIVEのセトリ構造
    # =========================================================

    historical_setlist = []

    for live_id, songs in live_list:

        ordered_songs = sorted(
            songs,
            key=lambda song: (
                song["song_order"],
                song["medley_order"]
                if song["medley_order"] is not None
                else 999
            )
        )

        historical_setlist.append(
            {
                "live_id": live_id,
                "live_date": str(
                    ordered_songs[0]["live_date"]
                ),
                "live_name": ordered_songs[0]["live_name"],
                "tour_name": ordered_songs[0]["tour_name"],
                "songs": [
                    {
                        "song_id": song["song_id"],
                        "song_name": song["song_name"],
                        "album_name": song["album_name"],
                        "song_order": song["song_order"],
                        "is_medley": song["is_medley"],
                        "medley_order": song["medley_order"]
                    }
                    for song in ordered_songs
                ]
            }
        )

    # =========================================================
    # 直近LIVE
    # =========================================================

    last_live = None

    if live_list:

        last_live_id, last_live_songs = (
            live_list[0]
        )

        last_medley_groups = defaultdict(list)

        for song in last_live_songs:

            if song["is_medley"]:
                last_medley_groups[
                    song["song_order"]
                ].append(song)

        last_medley_song_count = sum(
            len(
                {
                    song["song_id"]
                    for song in medley_songs
                }
            )
            for medley_songs
            in last_medley_groups.values()
        )

        last_live = {
            "live_id": last_live_id,
            "live_date": str(
                last_live_songs[0]["live_date"]
            ),
            "live_name": last_live_songs[0][
                "live_name"
            ],
            "tour_name": last_live_songs[0][
                "tour_name"
            ],
            "has_medley": bool(
                last_medley_groups
            ),
            "medley_count": len(
                last_medley_groups
            ),
            "medley_song_count": (
                last_medley_song_count
            )
        }

    # =========================================================
    # 予測候補となる全INORI楽曲
    # =========================================================

    song_groups = (
        song_model.get_ai_prediction_song_groups()
    )

    song_stats = {}

    for song in song_groups:

        song_stats[
            song["song_group_id"]
        ] = {
            "song_group_id": song[
                "song_group_id"
            ],
            "song_name": song[
                "song_name"
            ],
            "album_name": song[
                "album_name"
            ],
            "appearance_count": 0,
            "tour_appearance_count": 0,
            "recent_5_count": 0,
            "recent_10_count": 0,
            "last_appearance_index": None,
            "position_total": 0,
            "position_count": 0,
            "position_min": None,
            "position_max": None,
            "medley_count": 0,
            "early_count": 0,
            "middle_count": 0,
            "late_count": 0
        }

    # =========================================================
    # 楽曲ごとの統計
    # =========================================================

    for index, (live_id, songs) in enumerate(
        live_list
    ):

        is_same_tour = (
            target_live.get("tour_name")
            and songs[0]["tour_name"]
            == target_live["tour_name"]
        )

        # 1公演内で同じ曲が複数行存在しても1回として扱う
        live_songs = {}

        for song in songs:

            song_group_id = song[
                "song_id"
            ]

            if song_group_id not in live_songs:

                live_songs[
                    song_group_id
                ] = song

            else:

                # 同じ曲が複数ある場合は
                # 曲順の早い方を採用
                if (
                    song["song_order"]
                    < live_songs[
                        song_group_id
                    ]["song_order"]
                ):
                    live_songs[
                        song_group_id
                    ] = song

        for song_group_id, song in (
            live_songs.items()
        ):

            # 念のため未知の楽曲があった場合
            if song_group_id not in song_stats:

                song_stats[
                    song_group_id
                ] = {
                    "song_group_id": (
                        song_group_id
                    ),
                    "song_name": song[
                        "song_name"
                    ],
                    "album_name": song[
                        "album_name"
                    ],
                    "appearance_count": 0,
                    "tour_appearance_count": 0,
                    "recent_5_count": 0,
                    "recent_10_count": 0,
                    "last_appearance_index": (
                        None
                    ),
                    "position_total": 0,
                    "position_count": 0,
                    "position_min": None,
                    "position_max": None,
                    "medley_count": 0,
                    "early_count": 0,
                    "middle_count": 0,
                    "late_count": 0
                }

            stats = song_stats[
                song_group_id
            ]

            # 1公演につき1回
            stats[
                "appearance_count"
            ] += 1

            if is_same_tour:
                stats[
                    "tour_appearance_count"
                ] += 1

            if index < 5:
                stats[
                    "recent_5_count"
                ] += 1

            if index < 10:
                stats[
                    "recent_10_count"
                ] += 1

            if (
                stats[
                    "last_appearance_index"
                ]
                is None
            ):
                stats[
                    "last_appearance_index"
                ] = index

            position = song[
                "song_order"
            ]

            stats[
                "position_total"
            ] += position

            stats[
                "position_count"
            ] += 1

            if (
                stats[
                    "position_min"
                ]
                is None
            ):
                stats[
                    "position_min"
                ] = position
            else:
                stats[
                    "position_min"
                ] = min(
                    stats[
                        "position_min"
                    ],
                    position
                )

            if (
                stats[
                    "position_max"
                ]
                is None
            ):
                stats[
                    "position_max"
                ] = position
            else:
                stats[
                    "position_max"
                ] = max(
                    stats[
                        "position_max"
                    ],
                    position
                )

            if song["is_medley"]:
                stats[
                    "medley_count"
                ] += 1

            # =================================================
            # セトリ内の位置傾向
            # =================================================

            setlist_length = len(
                songs
            )

            if setlist_length > 0:

                position_rate = (
                    position
                    / setlist_length
                )

                if position_rate <= 0.33:

                    stats[
                        "early_count"
                    ] += 1

                elif position_rate <= 0.66:

                    stats[
                        "middle_count"
                    ] += 1

                else:

                    stats[
                        "late_count"
                    ] += 1

    # =========================================================
    # 統計値を計算
    # =========================================================

    for stats in song_stats.values():

        if total_live_count > 0:

            stats[
                "appearance_rate"
            ] = round(
                stats[
                    "appearance_count"
                ]
                / total_live_count
                * 100,
                1
            )

        else:

            stats[
                "appearance_rate"
            ] = 0

        if tour_live_count > 0:

            stats[
                "tour_appearance_rate"
            ] = round(
                stats[
                    "tour_appearance_count"
                ]
                / tour_live_count
                * 100,
                1
            )

        else:

            stats[
                "tour_appearance_rate"
            ] = 0

        if (
            stats[
                "position_count"
            ]
            > 0
        ):

            stats[
                "average_position"
            ] = round(
                stats[
                    "position_total"
                ]
                / stats[
                    "position_count"
                ],
                1
            )

        else:

            stats[
                "average_position"
            ] = None

        if (
            stats[
                "last_appearance_index"
            ]
            is None
        ):

            stats[
                "appearances_since_last"
            ] = None

        else:

            stats[
                "appearances_since_last"
            ] = stats[
                "last_appearance_index"
            ]

        if (
            stats[
                "appearance_count"
            ]
            > 0
        ):

            stats[
                "medley_rate"
            ] = round(
                stats[
                    "medley_count"
                ]
                / stats[
                    "appearance_count"
                ]
                * 100,
                1
            )

            stats[
                "early_rate"
            ] = round(
                stats[
                    "early_count"
                ]
                / stats[
                    "appearance_count"
                ]
                * 100,
                1
            )

            stats[
                "middle_rate"
            ] = round(
                stats[
                    "middle_count"
                ]
                / stats[
                    "appearance_count"
                ]
                * 100,
                1
            )

            stats[
                "late_rate"
            ] = round(
                stats[
                    "late_count"
                ]
                / stats[
                    "appearance_count"
                ]
                * 100,
                1
            )

        else:

            stats[
                "medley_rate"
            ] = 0

            stats[
                "early_rate"
            ] = 0

            stats[
                "middle_rate"
            ] = 0

            stats[
                "late_rate"
            ] = 0

    return {
        "target_live": target_live,
        "total_live_count": total_live_count,
        "tour_live_count": tour_live_count,
        "average_setlist_count": (
            average_setlist_count
        ),
        "average_setlist_slot_count": (
            average_setlist_slot_count
        ),
        "medley_live_count": (
            medley_live_count
        ),
        "medley_live_rate": (
            medley_live_rate
        ),
        "average_medley_song_count": (
            average_medley_song_count
        ),
        "recent_medley_pattern": (
            recent_medley_pattern
        ),
        "last_live": last_live,
        "historical_setlist": (
            historical_setlist
        ),
        "songs": list(
            song_stats.values()
        )
    }


def calculate_ai_prediction_scores(prediction_data):
    """
    AIセトリ予測用スコアを計算
    """

    if not prediction_data:
        return None

    songs = prediction_data["songs"]

    for song in songs:

        score = 0

        # 過去の出演率
        score += song["appearance_rate"] * 0.35

        # 同一ツアーでの出演率
        score += song["tour_appearance_rate"] * 0.30

        # 直近5公演での出演
        score += song["recent_5_count"] * 2

        # 直近10公演での出演
        score += song["recent_10_count"]

        # 前回出演から空いている場合
        if song["appearances_since_last"] is not None:
            score += min(
                song["appearances_since_last"] * 1.5,
                15
            )

        # メドレー出演率
        score += song["medley_rate"] * 0.05

        song["prediction_score"] = round(
            score,
            2
        )

    songs.sort(
        key=lambda song: song["prediction_score"],
        reverse=True
    )

    return prediction_data


def generate_ai_prediction_setlist(
    prediction_data,
    required_song_ids=None
):
    """
    予測スコアと過去の配置傾向から
    予測セトリを生成

    required_song_ids:
        管理者が指定した必須曲の
        song_group_id
    """

    if not prediction_data:
        return None

    required_song_ids = (
        required_song_ids or []
    )

    songs = prediction_data["songs"]

    setlist_count = (
        prediction_data["average_setlist_count"]
    )

    if setlist_count <= 0:
        return []

    song_map = {
        song["song_group_id"]: song
        for song in songs
    }

    # 必須曲
    required_songs = []

    for song_group_id in required_song_ids:

        song = song_map.get(song_group_id)

        if song and song not in required_songs:
            song["is_required"] = True
            required_songs.append(song)

    # 必須曲がセトリ曲数を超える場合
    if len(required_songs) > setlist_count:
        raise ValueError(
            "必須曲の数が予測セトリ曲数を超えています。"
        )

    required_song_id_set = {
        song["song_group_id"]
        for song in required_songs
    }

    candidates = [
        song
        for song in prediction_data["songs"]
        if song["song_group_id"]
        not in required_song_id_set
    ]

    candidates.sort(
        key=lambda song: (
            song["prediction_score"],
        ),
        reverse=True
    )

    remaining_count = (
        setlist_count
        - len(required_songs)
    )

    if remaining_count <= 0:

        predicted_songs = required_songs

    else:

        early_count = round(
            remaining_count * 0.33
        )

        middle_count = round(
            remaining_count * 0.34
        )

        late_count = (
            remaining_count
            - early_count
            - middle_count
        )

        predicted_songs = list(
            required_songs
        )

        # 序盤
        early_candidates = sorted(
            candidates,
            key=lambda song: (
                song["early_rate"],
                song["prediction_score"]
            ),
            reverse=True
        )

        for song in early_candidates:

            if len(predicted_songs) >= (
                len(required_songs)
                + early_count
            ):
                break

            if song not in predicted_songs:
                predicted_songs.append(song)

        # 中盤
        middle_candidates = sorted(
            candidates,
            key=lambda song: (
                song["middle_rate"],
                song["prediction_score"]
            ),
            reverse=True
        )

        for song in middle_candidates:

            if len(predicted_songs) >= (
                len(required_songs)
                + early_count
                + middle_count
            ):
                break

            if song not in predicted_songs:
                predicted_songs.append(song)

        # 終盤
        late_candidates = sorted(
            candidates,
            key=lambda song: (
                song["late_rate"],
                song["prediction_score"]
            ),
            reverse=True
        )

        for song in late_candidates:

            if len(predicted_songs) >= setlist_count:
                break

            if song not in predicted_songs:
                predicted_songs.append(song)

        # 足りない場合は総合スコアで補完
        for song in candidates:

            if len(predicted_songs) >= setlist_count:
                break

            if song not in predicted_songs:
                predicted_songs.append(song)

    # 平均曲順を基準に並べる
    predicted_songs.sort(
        key=lambda song: (
            song["average_position"]
            if song["average_position"]
            is not None
            else 999,
            -song["prediction_score"]
        )
    )

    # 必須フラグ
    for song in predicted_songs:

        if "is_required" not in song:
            song["is_required"] = False

        if "is_medley" not in song:
            song["is_medley"] = False

        if "medley_order" not in song:
            song["medley_order"] = None

    # 予測曲順
    for index, song in enumerate(
        predicted_songs,
        start=1
    ):
        song["predicted_position"] = index

    return predicted_songs


def generate_ai_prediction_setlist_with_ai(
    prediction_data,
    required_song_ids=None,
    prediction_context=None
):
    """
    統計予測と生成AIを組み合わせて
    AIセトリ予測を生成する
    """

    statistical_setlist = (
        generate_ai_prediction_setlist(
            prediction_data,
            required_song_ids
        )
    )

    if not statistical_setlist:
        return []

    return apply_ai_prediction(
        prediction_data,
        statistical_setlist,
        prediction_context
    )


def apply_ai_prediction(
    prediction_data,
    statistical_setlist,
    prediction_context=None
):
    """
    統計予測結果に生成AIによる評価を適用する

    現時点では統計予測結果をそのまま返す。
    """

    return statistical_setlist


def validate_prediction_editable(live):
    """
    AIセトリ予測が変更可能か確認

    開催日当日以降は変更不可。
    """

    if not live:
        raise ValueError(
            "対象LIVEが存在しません。"
        )

    if live["live_date"] <= date.today():
        raise ValueError(
            "開催日当日以降のAIセトリ予測は変更できません。"
        )


def generate_ai_prediction(
    live_id,
    required_song_ids=None,
    prediction_context=None,
    admin_memo=None
):
    """
    Geminiを使用してAIセトリ予測を生成・保存

    既存予測がある場合は上書きする。
    """

    target_live = prediction_ai_model.get_live(
        live_id
    )

    validate_prediction_editable(
        target_live
    )

    prediction_data = get_ai_prediction_data(
        target_live
    )

    prediction_data = calculate_ai_prediction_scores(
        prediction_data
    )

    ai_input = build_ai_prediction_input(
        prediction_data,
        prediction_context=prediction_context,
        required_song_ids=required_song_ids
    )

    gemini_result = generate_ai_prediction_with_gemini(
        ai_input
    )

    details = convert_gemini_prediction_to_details(
        gemini_result,
        ai_input
    )

    existing_prediction = (
        prediction_ai_model.get_prediction_by_live_id(
            live_id
        )
    )

    if existing_prediction:
        prediction_ai_model.update_prediction(
            prediction_id=existing_prediction[
                "prediction_id"
            ],
            live_id=live_id,
            prediction_context=prediction_context,
            admin_memo=admin_memo,
            public_flag=existing_prediction[
                "public_flag"
            ]
        )

        prediction_ai_model.update_prediction_details(
            prediction_id=existing_prediction[
                "prediction_id"
            ],
            details=details
        )

        return prediction_ai_model.get_prediction(
            existing_prediction[
                "prediction_id"
            ]
        )

    return save_ai_prediction(
        live_id=live_id,
        prediction_context=prediction_context,
        admin_memo=admin_memo,
        public_flag=False,
        details=details
    )


def save_ai_prediction(
    live_id,
    prediction_context=None,
    admin_memo=None,
    public_flag=False,
    details=None
):
    """
    AIセトリ予測をDBへ保存
    """

    if not live_id:
        return None

    if not details:
        return None

    prediction_id = (
        prediction_ai_model.create_prediction(
            live_id=live_id,
            prediction_context=(
                prediction_context
            ),
            admin_memo=admin_memo,
            public_flag=public_flag
        )
    )

    if not prediction_id:
        return None

    prediction_ai_model.create_prediction_details(
        prediction_id,
        details
    )

    return prediction_ai_model.get_prediction(
        prediction_id
    )


def get_ai_prediction_by_live_id(live_id):
    """
    LIVEに紐づく保存済みAIセトリ予測を取得
    """

    if not live_id:
        return None

    return prediction_ai_model.get_prediction_by_live_id(
        live_id
    )


def get_ai_prediction_tour_base(target_live):
    """
    同一ツアー直前公演をAIセトリ予測の基準として取得する。

    優先順位:
        1. 直前公演の実際のセトリ
        2. 実際のセトリがない場合、直前公演のAI予測
        3. どちらもない場合はNone

    ツアー公演でないLIVEは対象外。
    """

    if not target_live:
        return None

    tour_name = target_live.get("tour_name")

    if not tour_name:
        return None

    previous_live = live_model.get_previous_tour_live(
        target_live["live_id"]
    )

    if not previous_live:
        return None

    previous_live_id = previous_live["live_id"]

    # --------------------------------------------------
    # 1. 直前公演の実際のセトリを確認
    # --------------------------------------------------

    actual_setlist = setlist_model.get_setlist_list(
        event_type="LIVE",
        event_id=previous_live_id
    )

    if actual_setlist:
        return {
            "base_type": "actual",
            "base_live_id": previous_live_id,
            "base_live_name": previous_live["live_name"],
            "base_live_date": previous_live["live_date"],
            "songs": actual_setlist
        }

    # --------------------------------------------------
    # 2. 実際のセトリがなければAI予測を確認
    # --------------------------------------------------

    ai_prediction = get_ai_prediction_by_live_id(
        previous_live_id
    )

    if ai_prediction:
        return {
            "base_type": "ai_prediction",
            "base_live_id": previous_live_id,
            "base_live_name": previous_live["live_name"],
            "base_live_date": previous_live["live_date"],
            "songs": ai_prediction["details"]
        }

    # --------------------------------------------------
    # 3. 基準セトリなし
    # --------------------------------------------------

    return None


def update_ai_prediction(
    prediction_id,
    live_id,
    prediction_context=None,
    admin_memo=None,
    public_flag=False,
    predicted_setlist=None
):
    """
    保存済みAIセトリ予測を更新

    開催日当日以降は変更不可。
    """

    if not prediction_id:
        return None

    if not live_id:
        return None

    if not predicted_setlist:
        return None

    live = prediction_ai_model.get_live(
        live_id
    )

    validate_prediction_editable(
        live
    )

    updated = (
        prediction_ai_model.update_prediction(
            prediction_id=prediction_id,
            live_id=live_id,
            prediction_context=(
                prediction_context
            ),
            admin_memo=admin_memo,
            public_flag=public_flag
        )
    )

    if not updated:
        return None

    prediction_ai_model.update_prediction_details(
        prediction_id=prediction_id,
        details=[
            {
                "song_id": song[
                    "song_group_id"
                ],
                "predicted_order": index,
                "prediction_score": (
                    song.get(
                        "prediction_score"
                    )
                ),
                "prediction_reason": (
                    song.get(
                        "prediction_reason"
                    )
                ),
                "is_required": song.get(
                    "is_required",
                    False
                ),
                "is_medley": song.get(
                    "is_medley",
                    False
                ),
                "medley_order": song.get(
                    "medley_order"
                )
            }
            for index, song in enumerate(
                predicted_setlist,
                start=1
            )
        ]
    )

    return prediction_ai_model.get_prediction(
        prediction_id
    )


def get_ai_prediction_live_list():
    """
    AIセトリ予測対象LIVE一覧を取得
    """

    return prediction_ai_model.get_live_list()


def get_ai_prediction_target_live(live_id):
    """
    AIセトリ予測対象LIVEを取得
    """

    if not live_id:
        return None

    return prediction_ai_model.get_live(
        live_id
    )


def get_ai_prediction_song_groups():
    """
    AIセトリ予測で選択可能な楽曲一覧を取得
    """

    return song_model.get_ai_prediction_song_groups()


def build_ai_prediction_input(
    prediction_data,
    prediction_context=None,
    required_song_ids=None
):
    """
    Geminiへ渡すAIセトリ予測用入力データを作成

    Geminiには以下を渡す。

    - 対象LIVE
    - 管理者が入力した予測条件
    - 必須曲
    - 過去LIVEの統計
    - 直近LIVEの情報
    - 過去のメドレー傾向
    - 過去LIVEの実際のセトリ構造
    - 全INORI楽曲の統計

    管理者メモはAIには渡さない。
    """

    if not prediction_data:
        return None

    required_song_ids = required_song_ids or []

    try:
        required_song_id_set = {
            int(song_id)
            for song_id in required_song_ids
        }
    except (TypeError, ValueError) as error:
        raise ValueError(
            "必須曲の指定が不正です。"
        ) from error

    candidate_song_ids = {
        song["song_group_id"]
        for song in prediction_data["songs"]
    }

    invalid_required_song_ids = (
        required_song_id_set
        - candidate_song_ids
    )

    if invalid_required_song_ids:
        raise ValueError(
            "候補曲に存在しない必須曲が指定されています: "
            + ", ".join(
                str(song_id)
                for song_id in sorted(
                    invalid_required_song_ids
                )
            )
        )

    # =========================================================
    # 必須曲
    # =========================================================

    required_songs = []

    for song in prediction_data["songs"]:

        if (
            song["song_group_id"]
            in required_song_id_set
        ):
            required_songs.append(
                {
                    "song_id": song["song_group_id"],
                    "song_name": song["song_name"],
                    "album_name": song["album_name"]
                }
            )

    # =========================================================
    # 全楽曲統計
    # =========================================================

    songs = []

    for song in prediction_data["songs"]:

        songs.append(
            {
                "song_id": song["song_group_id"],
                "song_name": song["song_name"],
                "album_name": song["album_name"],
                "appearance_count": song["appearance_count"],
                "appearance_rate": song["appearance_rate"],
                "tour_appearance_count": song[
                    "tour_appearance_count"
                ],
                "tour_appearance_rate": song[
                    "tour_appearance_rate"
                ],
                "recent_5_count": song["recent_5_count"],
                "recent_10_count": song["recent_10_count"],
                "appearances_since_last": song[
                    "appearances_since_last"
                ],
                "average_position": song[
                    "average_position"
                ],
                "position_min": song["position_min"],
                "position_max": song["position_max"],
                "medley_count": song["medley_count"],
                "medley_rate": song["medley_rate"],
                "early_rate": song["early_rate"],
                "middle_rate": song["middle_rate"],
                "late_rate": song["late_rate"],
                "prediction_score": song.get(
                    "prediction_score",
                    0
                ),
                "is_required": (
                    song["song_group_id"]
                    in required_song_id_set
                )
            }
        )

    # =========================================================
    # 対象LIVE
    # =========================================================

    target_live = prediction_data["target_live"]

    target_live_data = {
        "live_id": target_live["live_id"],
        "live_name": target_live["live_name"],
        "tour_name": target_live.get("tour_name"),
        "tour_order": target_live.get("tour_order"),
        "live_date": str(
            target_live["live_date"]
        )
    }

    # =========================================================
    # セトリ統計
    # =========================================================

    setlist_statistics = {
        "total_live_count": prediction_data[
            "total_live_count"
        ],
        "tour_live_count": prediction_data[
            "tour_live_count"
        ],
        "average_song_count": prediction_data[
            "average_setlist_count"
        ],
        "average_slot_count": prediction_data[
            "average_setlist_slot_count"
        ],
        "medley_live_count": prediction_data[
            "medley_live_count"
        ],
        "medley_live_rate": prediction_data[
            "medley_live_rate"
        ],
        "average_medley_song_count": prediction_data[
            "average_medley_song_count"
        ]
    }

    # =========================================================
    # 直近LIVE
    # =========================================================

    last_live = prediction_data.get(
        "last_live"
    )

    if last_live:

        last_live_data = {
            "live_id": last_live["live_id"],
            "live_date": last_live["live_date"],
            "live_name": last_live["live_name"],
            "tour_name": last_live["tour_name"],
            "has_medley": last_live["has_medley"],
            "medley_count": last_live["medley_count"],
            "medley_song_count": last_live[
                "medley_song_count"
            ]
        }

    else:

        last_live_data = None

    # =========================================================
    # 直近のメドレー傾向
    # =========================================================

    recent_medley_pattern = prediction_data.get(
        "recent_medley_pattern",
        []
    )

    # =========================================================
    # 過去LIVEの実際のセトリ
    # =========================================================

    historical_setlist = prediction_data.get(
        "historical_setlist",
        []
    )

    # =========================================================
    # Gemini入力データ
    # =========================================================

    return {
        "target_live": target_live_data,
        "prediction_context": (
            prediction_context or ""
        ),
        "required_songs": required_songs,
        "setlist_statistics": setlist_statistics,
        "last_live": last_live_data,
        "recent_medley_pattern": (
            recent_medley_pattern
        ),
        "historical_setlist": (
            historical_setlist
        ),
        "songs": songs
    }


def build_ai_prediction_prompt(ai_input):
    """
    Geminiへ渡すAIセトリ予測プロンプトを作成
    """

    if not ai_input:
        return None

    system_instruction = """
あなたは水瀬いのりのLIVEセトリを予測するAIです。

提供された過去LIVEのセトリ、楽曲ごとの出演統計、
直近LIVEの情報、メドレー傾向、対象LIVEの情報、
管理者が指定した予測条件を分析し、
対象LIVEで披露される可能性が高いセトリを予測してください。

【重要なルール】

1. 必須曲
- required_songs に含まれる楽曲は必ずセトリに含める。
- 必須曲を除外してはいけない。
- 必須曲も含め、同じ楽曲を2回以上使用してはいけない。

2. 楽曲
- songs に存在する song_id のみ使用する。
- songs に存在しない song_id を作成してはいけない。
- song_name、album_nameなどの情報を勝手に作成・変更してはいけない。

3. セトリ構成
- 過去LIVEの実際のセトリ構造を参考にする。
- 過去の出演率だけでなく、曲順、直近の出演状況、
  同一ツアーでの出演状況、メドレー傾向などを総合的に判断する。
- セトリ全体として自然な流れになるように曲順を決める。
- 楽曲の雰囲気、盛り上がり、ジャンル、曲同士のつながりなど、
  明示されていない主観的な要素についても合理的に推測してよい。
- ただし、提供されたデータから確認できない事実を断定してはいけない。

4. メドレー
- 過去LIVEで確認できるメドレー構成を参考にする。
- メドレーを作る場合は、1つのslotに複数曲を入れる。
- メドレー内部の曲順も決定する。
- メドレー内部の曲数は過去の傾向を参考にする。
- 必要以上にメドレーを増やさない。

5. セトリ曲数
- 過去LIVEの平均曲数、平均セトリ枠数、メドレー傾向を参考に、
  現実的な曲数とセトリ枠数にする。

6. 予測条件
- prediction_context に記載された条件を重視する。
- prediction_context に明確な条件がある場合、
  その条件を可能な限り予測へ反映する。
- required_songs は必須条件として扱う。
- 自然言語で指定された条件について、提供データから検証できない場合は、
  その条件を事実として扱わず、予測上の仮定として扱う。

7. 過去データ
- historical_setlist は過去LIVEの実際のセトリであり、
  楽曲の選択、曲順、メドレー構成を判断するための重要な参考データである。
- ただし、過去LIVEをそのままコピーするのではなく、
  対象LIVEの条件に合わせて予測する。

8. 管理者メモ
- 管理者用メモはAIへの入力情報には含まれていないため、
  推測してはいけない。

9. 出力
必ず以下のJSON形式だけを返してください。

{
  "predicted_setlist": {
    "song_count": 18,
    "slot_count": 16,
    "slots": [
      {
        "slot_order": 1,
        "is_medley": false,
        "songs": [
          {
            "song_id": 101,
            "medley_order": null,
            "reason": "序盤に適した楽曲と判断"
          }
        ]
      },
      {
        "slot_order": 2,
        "is_medley": true,
        "songs": [
          {
            "song_id": 102,
            "medley_order": 1,
            "reason": "メドレー構成として適している"
          },
          {
            "song_id": 103,
            "medley_order": 2,
            "reason": "前曲から自然につながる"
          }
        ]
      }
    ]
  }
}

【出力形式の厳密なルール】

- slot_order は1から開始し、連番にする。
- 通常曲のslotには1曲だけ入れる。
- メドレーのslotには2曲以上入れる。
- 通常曲のmedley_orderはnullにする。
- メドレー内のmedley_orderは1から開始し、連番にする。
- song_countは全slotに含まれる楽曲数。
- slot_countはslotの数。
- 各楽曲にはreasonを必ず設定する。
- song_idは必ずsongsに存在するものを使用する。
- 同じsong_idを複数回使用しない。
- required_songsの全楽曲を必ず含める。
- JSON以外の文章を出力しない。
"""

    prompt = json.dumps(
        ai_input,
        ensure_ascii=False,
        indent=2,
        default=str
    )

    return {
        "system_instruction": system_instruction.strip(),
        "prompt": prompt
    }


def generate_ai_prediction_with_gemini(
    ai_input
):
    """
    Geminiを使用してAIセトリ予測を生成
    """

    prompt_data = build_ai_prediction_prompt(
        ai_input
    )

    if not prompt_data:
        raise ValueError(
            "Geminiに渡す予測データがありません。"
        )

    result = gemini_service.generate_json(
        system_instruction=prompt_data[
            "system_instruction"
        ],
        prompt=prompt_data[
            "prompt"
        ]
    )

    if not isinstance(result, dict):
        raise ValueError(
            "Geminiから不正な形式のレスポンスが返されました。"
        )

    predicted_setlist = result.get(
        "predicted_setlist"
    )

    if not isinstance(
        predicted_setlist,
        dict
    ):
        raise ValueError(
            "Geminiのレスポンスに"
            "predicted_setlistがありません。"
        )

    slots = predicted_setlist.get(
        "slots"
    )

    if not isinstance(
        slots,
        list
    ) or not slots:
        raise ValueError(
            "Geminiのレスポンスに"
            "slotsがありません。"
        )

    validate_ai_prediction_result(
        result,
        ai_input
    )

    return result


def validate_ai_prediction_result(
    result,
    ai_input
):
    """
    Geminiが生成したAIセトリ予測を検証
    """

    if not isinstance(result, dict):
        raise ValueError(
            "AI予測結果が不正です。"
        )

    predicted_setlist = result.get(
        "predicted_setlist"
    )

    if not isinstance(
        predicted_setlist,
        dict
    ):
        raise ValueError(
            "AI予測結果にpredicted_setlistがありません。"
        )

    slots = predicted_setlist.get(
        "slots"
    )

    if not isinstance(
        slots,
        list
    ) or not slots:
        raise ValueError(
            "AI予測結果にslotsがありません。"
        )

    candidate_song_ids = {
        song["song_id"]
        for song in ai_input.get(
            "songs",
            []
        )
    }

    required_song_ids = {
        song["song_id"]
        for song in ai_input.get(
            "required_songs",
            []
        )
    }

    used_song_ids = []
    actual_song_count = 0
    actual_slot_count = len(
        slots
    )

    for expected_slot_order, slot in enumerate(
        slots,
        start=1
    ):
        if not isinstance(
            slot,
            dict
        ):
            raise ValueError(
                "AI予測結果に不正なslotがあります。"
            )

        slot_order = slot.get(
            "slot_order"
        )

        if slot_order != expected_slot_order:
            raise ValueError(
                "slot_orderが連番になっていません。"
            )

        is_medley = slot.get(
            "is_medley"
        )

        if not isinstance(
            is_medley,
            bool
        ):
            raise ValueError(
                "is_medleyが不正です。"
            )

        songs = slot.get(
            "songs"
        )

        if not isinstance(
            songs,
            list
        ) or not songs:
            raise ValueError(
                "slotにsongsがありません。"
            )

        if is_medley:

            if len(songs) < 2:
                raise ValueError(
                    "メドレーには2曲以上必要です。"
                )

        else:

            if len(songs) != 1:
                raise ValueError(
                    "通常曲のslotには1曲だけ指定してください。"
                )

        for expected_medley_order, song in enumerate(
            songs,
            start=1
        ):
            if not isinstance(
                song,
                dict
            ):
                raise ValueError(
                    "AI予測結果に不正な楽曲があります。"
                )

            song_id = song.get(
                "song_id"
            )

            if song_id not in candidate_song_ids:
                raise ValueError(
                    f"候補曲に存在しないsong_idです: {song_id}"
                )

            if song_id in used_song_ids:
                raise ValueError(
                    f"同じ楽曲が複数回指定されています: {song_id}"
                )

            reason = song.get(
                "reason"
            )

            if not isinstance(
                reason,
                str
            ) or not reason.strip():
                raise ValueError(
                    f"楽曲のreasonがありません: {song_id}"
                )

            if is_medley:

                medley_order = song.get(
                    "medley_order"
                )

                if medley_order != expected_medley_order:
                    raise ValueError(
                        "メドレー内のmedley_orderが連番になっていません。"
                    )

            else:

                if song.get(
                    "medley_order"
                ) is not None:
                    raise ValueError(
                        "通常曲のmedley_orderはnullである必要があります。"
                    )

            used_song_ids.append(
                song_id
            )

            actual_song_count += 1

    used_song_id_set = set(
        used_song_ids
    )

    missing_required_song_ids = (
        required_song_ids
        - used_song_id_set
    )

    if missing_required_song_ids:
        raise ValueError(
            "必須曲がAI予測に含まれていません: "
            + ", ".join(
                str(song_id)
                for song_id in sorted(
                    missing_required_song_ids
                )
            )
        )

    predicted_song_count = (
        predicted_setlist.get(
            "song_count"
        )
    )

    if predicted_song_count != actual_song_count:
        raise ValueError(
            "song_countと実際の楽曲数が一致していません。"
        )

    predicted_slot_count = (
        predicted_setlist.get(
            "slot_count"
        )
    )

    if predicted_slot_count != actual_slot_count:
        raise ValueError(
            "slot_countと実際のslot数が一致していません。"
        )

    return True


def convert_gemini_prediction_to_details(
    result,
    ai_input
):
    """
    Geminiのセトリ予測結果をDB保存用detailsへ変換
    """

    predicted_setlist = result[
        "predicted_setlist"
    ]

    slots = predicted_setlist[
        "slots"
    ]

    required_song_ids = {
        song["song_id"]
        for song in ai_input.get(
            "required_songs",
            []
        )
    }

    details = []

    for slot in slots:

        slot_order = slot[
            "slot_order"
        ]

        is_medley = slot[
            "is_medley"
        ]

        for song in slot[
            "songs"
        ]:

            song_id = song[
                "song_id"
            ]

            details.append(
                {
                    "song_id": song_id,
                    "predicted_order": slot_order,
                    "prediction_score": None,
                    "prediction_reason": song[
                        "reason"
                    ],
                    "is_required": (
                        song_id
                        in required_song_ids
                    ),
                    "is_medley": is_medley,
                    "medley_order": (
                        song["medley_order"]
                        if is_medley
                        else None
                    )
                }
            )

    return details

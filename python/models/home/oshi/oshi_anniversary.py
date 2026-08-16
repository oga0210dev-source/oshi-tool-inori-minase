from datetime import date

from python.core.database import get_connection


def get_next_anniversary_date(
        anniversary_date,
        today
):
    try:
        next_date = anniversary_date.replace(
            year=today.year
        )
    except ValueError:
        next_date = anniversary_date.replace(
            year=today.year,
            day=28
        )

    if next_date < today:
        try:
            next_date = anniversary_date.replace(
                year=today.year + 1
            )
        except ValueError:
            next_date = anniversary_date.replace(
                year=today.year + 1,
                day=28
            )

    return next_date


def get_anniversary_list(
        keyword="",
        sort="next"
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:

            today = date.today()
            anniversaries = []

            # ==========================================
            # 推し基本情報
            # ==========================================

            cur.execute(
                """
                SELECT
                    oshi_name,
                    birthday,
                    voice_actor_debut_date,
                    singer_debut_date
                FROM m_oshi_basic
                WHERE
                    oshi_id = 1
                """
            )

            oshi_basic = cur.fetchone()

            if oshi_basic:

                basic_items = [
                    {
                        "anniversary_id": -1,
                        "anniversary_name": "誕生日",
                        "anniversary_date": oshi_basic["birthday"],
                        "description": None,
                        "anniversary_type": "BIRTHDAY"
                    },
                    {
                        "anniversary_id": -2,
                        "anniversary_name": "声優デビュー",
                        "anniversary_date": (
                            oshi_basic["voice_actor_debut_date"]
                        ),
                        "description": None,
                        "anniversary_type": "VOICE_ACTOR"
                    },
                    {
                        "anniversary_id": -3,
                        "anniversary_name": "歌手デビュー",
                        "anniversary_date": (
                            oshi_basic["singer_debut_date"]
                        ),
                        "description": None,
                        "anniversary_type": "SINGER"
                    }
                ]

                for item in basic_items:

                    anniversary_date = item["anniversary_date"]

                    if anniversary_date is None:
                        continue

                    if item["anniversary_type"] == "BIRTHDAY":
                        search_text = (
                            f"{item['anniversary_name']} "
                            f"{oshi_basic['oshi_name']}"
                        )
                    else:
                        search_text = item["anniversary_name"]

                    item["search_text"] = search_text

                    next_date = get_next_anniversary_date(
                        anniversary_date,
                        today
                    )

                    item["next_anniversary_date"] = next_date

                    item["remaining_days"] = (
                        next_date - today
                    ).days

                    item["anniversary_years"] = (
                        next_date.year - anniversary_date.year
                    )

                    if item["anniversary_type"] == "BIRTHDAY":
                        item["display_type"] = "birthday"
                        item["display_label"] = "誕生日"
                    elif item["anniversary_type"] == "VOICE_ACTOR":
                        item["display_type"] = "debut"
                        item["display_label"] = "声優デビュー"
                    else:
                        item["display_type"] = "debut"
                        item["display_label"] = "歌手デビュー"

                    anniversaries.append(item)

            # ==========================================
            # 記念日マスタ
            # ==========================================

            conditions = [
                "is_deleted = FALSE",
                "public_flag = TRUE"
            ]

            params = []

            if keyword:
                conditions.append(
                    """
                    (
                        anniversary_name ILIKE %s
                        OR description ILIKE %s
                    )
                    """
                )

                search_keyword = f"%{keyword}%"

                params.extend([
                    search_keyword,
                    search_keyword
                ])

            where_sql = " AND ".join(conditions)

            cur.execute(
                f"""
                SELECT
                    anniversary_id,
                    anniversary_name,
                    anniversary_date,
                    description
                FROM m_oshi_anniversary
                WHERE
                    {where_sql}
                """,
                tuple(params)
            )

            master_anniversaries = cur.fetchall()

            for anniversary in master_anniversaries:

                if anniversary["description"]:
                    anniversary["description"] = (
                        anniversary["description"].strip()
                    )

                anniversary_date = (
                    anniversary["anniversary_date"]
                )

                next_date = get_next_anniversary_date(
                    anniversary_date,
                    today
                )

                anniversary["next_anniversary_date"] = (
                    next_date
                )

                anniversary["remaining_days"] = (
                    next_date - today
                ).days

                anniversary["anniversary_years"] = (
                    next_date.year - anniversary_date.year
                )

                anniversary["anniversary_type"] = "MASTER"
                anniversary["display_type"] = "anniversary"
                anniversary["display_label"] = "記念日"

                anniversaries.append(anniversary)

            # ==========================================
            # 検索
            # ==========================================

            if keyword:
                keyword_lower = keyword.lower()

                anniversaries = [
                    anniversary
                    for anniversary in anniversaries
                    if keyword_lower in (
                        anniversary.get("search_text", "")
                        or anniversary["anniversary_name"]
                    ).lower()
                    or keyword_lower in (
                        anniversary.get("description") or ""
                    ).lower()
                ]

            # ==========================================
            # ソート
            # ==========================================

            if sort == "next":

                anniversaries.sort(
                    key=lambda x: (
                        x["remaining_days"],
                        x["anniversary_id"]
                    )
                )

            elif sort == "date_asc":

                anniversaries.sort(
                    key=lambda x: (
                        x["anniversary_date"].month,
                        x["anniversary_date"].day,
                        x["anniversary_id"]
                    )
                )

            elif sort == "date_desc":

                anniversaries.sort(
                    key=lambda x: (
                        x["anniversary_date"].month,
                        x["anniversary_date"].day,
                        x["anniversary_id"]
                    ),
                    reverse=True
                )

            elif sort == "name":

                anniversaries.sort(
                    key=lambda x: (
                        x["anniversary_name"],
                        x["anniversary_id"]
                    )
                )

            return anniversaries

    finally:
        conn.close()

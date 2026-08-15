from datetime import date

from python.core.database import get_connection


def calculate_age(
        birthday,
        today
):
    age = today.year - birthday.year

    if (today.month, today.day) < (
            birthday.month,
            birthday.day
    ):
        age -= 1

    return age


def calculate_elapsed_date(
        start_date,
        today
):
    years = today.year - start_date.year

    try:
        anniversary = start_date.replace(
            year=start_date.year + years
        )
    except ValueError:
        anniversary = start_date.replace(
            year=start_date.year + years,
            day=28
        )

    if anniversary > today:
        years -= 1

        try:
            anniversary = start_date.replace(
                year=start_date.year + years
            )
        except ValueError:
            anniversary = start_date.replace(
                year=start_date.year + years,
                day=28
            )

    months = 0
    current_date = anniversary

    while True:
        next_month = current_date.month + 1
        next_year = current_date.year

        if next_month > 12:
            next_month = 1
            next_year += 1

        try:
            next_date = current_date.replace(
                year=next_year,
                month=next_month
            )
        except ValueError:
            next_date = current_date.replace(
                year=next_year,
                month=next_month,
                day=28
            )

        if next_date > today:
            break

        current_date = next_date
        months += 1

    days = (today - current_date).days

    return years, months, days


def calculate_debut_info(
        debut_date,
        today
):
    if debut_date is None:
        return {
            "date": None,
            "years": None,
            "months": None,
            "days": None,
            "total_days": None
        }

    years, months, days = calculate_elapsed_date(
        debut_date,
        today
    )

    return {
        "date": debut_date,
        "years": years,
        "months": months,
        "days": days,
        "total_days": (
            today - debut_date
        ).days
    }


def get_oshi_basic():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    oshi_id,
                    oshi_name,
                    birthday,
                    voice_actor_debut_date,
                    singer_debut_date,
                    profile_image,
                    profile_message
                FROM m_oshi_basic
                WHERE oshi_id = 1
                """
            )

            oshi = cur.fetchone()

            if oshi is None:
                return None

            if oshi["profile_message"]:
                oshi["profile_message"] = oshi["profile_message"].strip()

            today = date.today()

            birthday = oshi["birthday"]

            age = calculate_age(
                birthday,
                today
            )

            birthday_this_year = birthday.replace(
                year=today.year
            )

            if birthday_this_year < today:
                next_birthday = birthday.replace(
                    year=today.year + 1
                )
            else:
                next_birthday = birthday_this_year

            birthday_remaining_days = (
                next_birthday - today
            ).days

            voice_actor_debut = calculate_debut_info(
                oshi["voice_actor_debut_date"],
                today
            )

            singer_debut = calculate_debut_info(
                oshi["singer_debut_date"],
                today
            )

            oshi["age"] = age
            oshi["birthday_remaining_days"] = (
                birthday_remaining_days
            )

            oshi["voice_actor_debut_elapsed_years"] = (
                voice_actor_debut["years"]
            )
            oshi["voice_actor_debut_elapsed_months"] = (
                voice_actor_debut["months"]
            )
            oshi["voice_actor_debut_elapsed_days"] = (
                voice_actor_debut["days"]
            )
            oshi["voice_actor_debut_elapsed_total_days"] = (
                voice_actor_debut["total_days"]
            )

            oshi["singer_debut_elapsed_years"] = (
                singer_debut["years"]
            )
            oshi["singer_debut_elapsed_months"] = (
                singer_debut["months"]
            )
            oshi["singer_debut_elapsed_days"] = (
                singer_debut["days"]
            )
            oshi["singer_debut_elapsed_total_days"] = (
                singer_debut["total_days"]
            )

            return oshi

    finally:
        conn.close()

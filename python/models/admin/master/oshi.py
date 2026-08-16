from python.core.database import get_connection


def get_oshi():
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

            return cur.fetchone()

    finally:
        conn.close()


def save_oshi(
        oshi_name,
        birthday,
        voice_actor_debut_date,
        singer_debut_date,
        profile_image,
        profile_message
):
    conn = get_connection()

    profile_message = profile_message.strip()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    oshi_id
                FROM m_oshi_basic
                WHERE oshi_id = 1
                """
            )

            oshi = cur.fetchone()

            if oshi:
                cur.execute(
                    """
                    UPDATE m_oshi_basic
                    SET
                        oshi_name = %s,
                        birthday = %s,
                        voice_actor_debut_date = %s,
                        singer_debut_date = %s,
                        profile_image = %s,
                        profile_message = %s
                    WHERE oshi_id = 1
                    """,
                    (
                        oshi_name,
                        birthday,
                        voice_actor_debut_date,
                        singer_debut_date,
                        profile_image,
                        profile_message
                    )
                )

            else:
                cur.execute(
                    """
                    INSERT INTO m_oshi_basic (
                        oshi_id,
                        oshi_name,
                        birthday,
                        voice_actor_debut_date,
                        singer_debut_date,
                        profile_image,
                        profile_message
                    )
                    VALUES (
                        1,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        oshi_name,
                        birthday,
                        voice_actor_debut_date,
                        singer_debut_date,
                        profile_image,
                        profile_message
                    )
                )

            conn.commit()

    finally:
        conn.close()

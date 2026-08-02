from python.core.database import get_connection


def get_setlist_list(event_type=None, event_id=None):
    conn = get_connection()

    sql = """
        SELECT
            *
        FROM
            m_setlist s
    """
    # params = [event_type, event_id]
    params = []
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()

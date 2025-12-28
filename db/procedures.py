def call_proc(conn, name, params):
    """
    Poziva PostgreSQL proceduru sa parametrima i commit-uje.
    """
    with conn.cursor() as cur:
        cur.execute(
            f"CALL {name}({','.join(['%s'] * len(params))})",
            params
        )
    conn.commit()
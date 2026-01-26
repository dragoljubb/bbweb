import pandas as pd

def load_view(view_name, season):
    q = f"""
    SELECT *
    FROM {view_name}
    WHERE season_code = '{season}'
      AND round = {round}
    """
    return pd.read_sql(q, engine)
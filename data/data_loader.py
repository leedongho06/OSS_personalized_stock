import sqlite3
import pandas as pd
import os


def load_data_from_db(db_path: str) -> pd.DataFrame:
    """DB에서 주식 데이터 로드. DB 없으면 빈 DataFrame 반환."""
    if not os.path.exists(db_path):
        return pd.DataFrame()

    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(
            "SELECT * FROM daily_prices", conn
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


def load_feedback_data(db_path: str) -> pd.DataFrame:
    """DB에서 피드백 데이터 로드. DB 없으면 빈 DataFrame 반환."""
    empty_df = pd.DataFrame(
        columns=["user_id", "ticker", "preference", "reason"]
    )

    if not os.path.exists(db_path):
        return empty_df

    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(
            "SELECT user_id, ticker, preference, reason FROM feedback", conn
        )
        conn.close()
        return df
    except Exception:
        return empty_df

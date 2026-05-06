import pandas as pd
import sqlite3
import os
from recommendation.validator import DataValidator

def load_data_from_db(db_path="data/stock_data.db"):
    if not os.path.exists(db_path):
        print(f"[Error] Database not found: {db_path}")
        return pd.DataFrame()

    try:
        # 데이터베이스 연결
        conn = sqlite3.connect(db_path)

        # 동호님 스펙에 맞춰 ma_20, volume 컬럼 추가
        query = """
        SELECT
            s.ticker,
            s.name,
            s.sector,
            d.per,
            d.pbr,
            d.ma_20,      -- 추가된 필수 피처
            d.volume      -- 추가된 필수 피처
            -- d.close_price 
        FROM stocks s
        JOIN daily_data d ON s.ticker = d.ticker
        WHERE d.date = (SELECT MAX(date) FROM daily_data)
        """

        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # ★ 읽어온 직후 유효성 검사 수
        DataValidator.validate_stock_d행ata(df)
        print("[Info] DB 로드 및 유효성 검사 완료")
        
        return df

    except Exception as e:
        print(f"[Error] DB Load or Validation fail: {e}")
        return pd.DataFrame()

def load_feedback_data(db_path="data/stock_data.db"):
    """
    알고리즘 고도화를 위한 사용자 상세 피드백 데이터를 로드합니다.
    (피드백도 동일한 SQLite DB의 user_feedback 테이블 등에 저장되어 있다고 가정)
    """
    if not os.path.exists(db_path):
        return pd.DataFrame()
        
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT user_id, ticker, preference, reason FROM user_feedback"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        DataValidator.validate_feedback_data(df)
        return df
    except Exception as e:
        print(f"[Warning] 피드백 데이터 로드 실패 (초기 상태일 수 있음): {e}")
        # 실패 시 validator에 정의된 필수 컬럼만 가진 빈 데이터프레임 반환
        return pd.DataFrame(columns=["user_id", "ticker", "preference", "reason"])

# 실행 테스트용 코드
if __name__ == "__main__":
    print("--- Testing DB Loader ---")
    df = load_data_from_db()
    if not df.empty:
        print(df.head())
    else:
        print("No data found or validation failed.")

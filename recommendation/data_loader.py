import pandas as pd
import sqlite3
import os

# SQLite 데이터베이스에서 최신 주가 및 재무 데이터를 로드
def load_data_from_db(db_path="data/stock_data.db"):
    if not os.path.exists(db_path):
        print(f"[Error] Database not found: {db_path}")
        return pd.DataFrame()

    try:
        # 데이터베이스 연결
        conn = sqlite3.connect(db_path)
        
        # stocks와 daily_data를 조인하여 필요한 컬럼을 모두 가져옴
        # 최신 날짜(date)의 데이터만 가져오는 쿼리
        query = """
        SELECT 
            s.ticker, 
            s.name, 
            s.sector, 
            d.per, 
            d.pbr, 
            d.close_price
        FROM stocks s
        JOIN daily_data d ON s.ticker = d.ticker
        WHERE d.date = (SELECT MAX(date) FROM daily_data)
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"[Error] DB Load fail: {e}")
        return pd.DataFrame()

# 실행 테스트용 코드
if __name__ == "__main__":
    # 이 부분은 DB 를 생성한 후에 실제 경로로 테스트
    print("--- Testing DB Loader ---")
    df = load_data_from_db() 
    if not df.empty:
        print(df.head())
    else:
        print("No data found. Check if the database exists.")

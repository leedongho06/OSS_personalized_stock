import os
import sqlite3
import pandas as pd

# main.py 또는 updater.py와 경로를 맞추기 위해 절대 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "stock_data.db")
TABLE_NAME = "daily_prices"


def init_db():
    """
    [초기화] DB 파일을 체크하고, per와 pbr 컬럼이 포함된 daily_prices 테이블을 생성합니다.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            dividends REAL,
            stock_splits REAL,
            ticker TEXT,
            per REAL,
            pbr REAL,
            PRIMARY KEY (date, ticker)
        )
    """)
    conn.commit()
    conn.close()


def save_daily_data(ticker_code, df: pd.DataFrame):
    """
    [저장 모듈] 전처리 및 유효성 검사가 완료된 데이터프레임을 DB에 적재합니다.
    INSERT OR REPLACE 방식을 도입하여 UNIQUE constraint (PK) 충돌을 원천 차단합니다.
    """
    init_db()
    
    if df.empty:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits', 'ticker', 'per', 'pbr']
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = 0.0 if col != 'date' and col != 'ticker' else ""

        final_df = df[required_columns].copy()
        
        data_tuples = [tuple(x) for x in final_df.to_numpy()]
        
        query = f"""
            INSERT OR REPLACE INTO {TABLE_NAME} 
            (date, open, high, low, close, volume, dividends, stock_splits, ticker, per, pbr)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.executemany(query, data_tuples)
        conn.commit()
        
    except Exception as e:
        print(f"[DB Error] {ticker_code} 데이터 저장 실패: {e}")
        conn.rollback()
    finally:
        conn.close()

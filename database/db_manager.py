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
    # data 디렉토리가 없다면 자동 생성
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # [🔥 스키마 확장] per와 pbr 컬럼을 REAL 타입으로 추가하여 생성합니다.
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
    """
    # 테이블이 없을 경우를 대비해 항상 먼저 초기화 검사 수행
    init_db()
    
    if df.empty:
        return

    conn = sqlite3.connect(DB_PATH)
    
    try:
        # 데이터프레임의 컬럼 순서와 스키마를 맞추기 위해 명시적 정렬
        # df 내부에는 이미 updater.py에서 주입한 'per', 'pbr' 컬럼이 포함되어 있습니다.
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits', 'ticker', 'per', 'pbr']
        
        # 만약 전처리 기에서 dividends나 stock_splits를 drop했다면 기본값 0.0으로 채워줌
        for col in required_columns:
            if col not in df.columns:
                df[col] = 0.0 if col != 'date' and col != 'ticker' else ""

        final_df = df[required_columns].copy()
        
        # 중복 데이터가 들어올 경우 기존 데이터를 덮어쓰거나 무시하도록 SQL 처리
        # pandas의 to_sql은 OR REPLACE를 기본 지원하지 않으므로 임시 테이블 기법이나 조절을 활용할 수 있으나, 
        # 여기서는 updater가 '마지막 날짜 다음 날'부터 긁어오므로 안전하게 append 처리합니다.
        final_df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
        conn.commit()
        
    except Exception as e:
        print(f"[DB Error] {ticker_code} 데이터 저장 실패: {e}")
        conn.rollback()
    finally:
        conn.close()

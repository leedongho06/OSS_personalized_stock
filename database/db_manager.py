import sqlite3
import pandas as pd
import os

# 현재 파일 위치를 기준으로 프로젝트 최상위 폴더 경로를 찾아 DB 연결
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(ROOT_DIR, 'stock_data.db')

# 1. 종목 기본 정보 저장
def insert_stock(ticker, name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO stocks (ticker, name) VALUES (?, ?)', (ticker, name))
    conn.commit()
    conn.close()

# 2. 모든 종목 조회
def get_all_stocks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stocks')
    rows = cursor.fetchall()
    conn.close()
    return rows

# 3. 일별 주가 데이터 저장
def save_daily_data(ticker, df):
    if df.empty:
        return
    conn = sqlite3.connect(DB_PATH)
    df.columns = [col.lower() for col in df.columns]
    df['ticker'] = ticker
    try:
        df.to_sql('daily_prices', conn, if_exists='append', index=False)
        print(f"[{ticker}] 저장 성공!")
    except Exception as e:
        print(f"저장 실패: {e}")
    finally:
        conn.close()

# 4. 특정 종목의 기간별 주가 데이터 조회 (Read)
def get_daily_prices(ticker, start_date=None, end_date=None):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM daily_prices WHERE ticker = ?"
    params = [ticker]
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    query += " ORDER BY date ASC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# --- 테스트 실행 파트 ---
if __name__ == "__main__":
    print("--- 테스트 시작 ---")
    insert_stock('005930', '삼성전자')
    
    dummy_df = pd.DataFrame({
        'Date': ['2026-04-15', '2026-04-16'],
        'Open': [70000, 71000],
        'High': [72000, 73000],
        'Low': [69000, 70000],
        'Close': [71000, 72000],
        'Volume': [1000000, 1100000]
    })
    print("가짜 주가 데이터를 저장해봅니다...")
    save_daily_data('005930', dummy_df)

    print("\n--- 저장된 삼성전자('005930') 데이터 조회를 시작합니다 ---")
    fetched_df = get_daily_prices('005930', start_date='2026-04-15', end_date='2026-04-16')
    
    if not fetched_df.empty:
        print("데이터 조회 성공!")
        print(fetched_df)
    else:
        print("해당 기간의 데이터가 없습니다.")
    print("--- 테스트 종료 ---")

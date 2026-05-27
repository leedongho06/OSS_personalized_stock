import sqlite3
import pandas as pd

DB_PATH = 'stock_data.db'

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

# 4. 일별 주가 데이터 조회
def get_daily_prices(ticker):
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM daily_prices WHERE ticker = '{ticker}' ORDER BY date ASC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 5. [추가됨] 사용자 투자 성향 저장
def insert_user(user_id, username, investment_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (user_id, username, investment_type) VALUES (?, ?, ?)', (user_id, username, investment_type))
    conn.commit()
    conn.close()

# 6. [추가됨] 사용자 정보 조회
def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

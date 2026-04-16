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

# 3. [추가] 일별 주가 데이터 저장 (A1의 데이터프레임용)
def save_daily_data(ticker, df):
    if df.empty: return
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

# --- 여기서부터 테스트 실행 파트 (맨 아래에 위치) ---
if __name__ == "__main__":
    print("--- 테스트 시작 ---")
    
    # 기본 종목 저장 테스트
    insert_stock('005930', '삼성전자')
    
    # [새로운 테스트] 가짜 데이터프레임 만들어서 저장 테스트
    
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
    
    print("--- 테스트 종료 ---")

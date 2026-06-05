import sqlite3
import pandas as pd
import os

# DB 파일이 항상 database/ 폴더 안에 안전하게 생성되도록 절대 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'stock_data.db')

def get_connection():
    """DB 연결 객체를 반환합니다."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """
    데이터베이스 및 테이블을 초기 생성합니다. (파일 임포트 시 자동 실행)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 주가 데이터 테이블 생성
    # 💡 고유 키(Date, Ticker)를 묶어서 PRIMARY KEY로 설정하여 중복 저장을 원천 차단합니다.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stock_data (
            Date TEXT,
            Ticker TEXT,
            Open REAL,
            High REAL,
            Low REAL,
            Close REAL,
            Volume INTEGER,
            Change REAL,
            PRIMARY KEY (Date, Ticker)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_daily_data(ticker, df):
    """
    api_fetcher.py 및 updater.py에서 수집/전처리한 주가 데이터를 DB에 저장합니다.
    """
    if df is None or df.empty:
        return
        
    # 원본 데이터프레임 손상 방지를 위해 복사본 사용
    df = df.copy()
    
    # DB 저장을 위해 종목코드(Ticker) 컬럼 추가
    df['Ticker'] = ticker
    
    # Date가 인덱스로 잡혀있다면 일반 컬럼으로 꺼내기
    if df.index.name == 'Date' or 'Date' not in df.columns:
        df = df.reset_index()
        # 혹시 'index'라는 이름으로 빠져나왔다면 'Date'로 변경
        if 'index' in df.columns:
            df = df.rename(columns={'index': 'Date'})
            
    # datetime 객체라면 텍스트(YYYY-MM-DD) 형식으로 안전하게 변환
    if pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        
    conn = get_connection()
    cursor = conn.cursor()
    
    # DataFrame을 딕셔너리 리스트로 변환
    records = df[['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume', 'Change']].to_dict(orient='records')
    
    # 💡 INSERT OR REPLACE: 기존에 같은 날짜+종목 데이터가 있으면 덮어쓰고, 없으면 새로 추가합니다.
    cursor.executemany('''
        INSERT OR REPLACE INTO daily_stock_data 
        (Date, Ticker, Open, High, Low, Close, Volume, Change) 
        VALUES (:Date, :Ticker, :Open, :High, :Low, :Close, :Volume, :Change)
    ''', records)
    
    conn.commit()
    conn.close()

def get_recent_stocks_for_web(limit=50):
    """
    app.py에서 호출되어, 웹 대시보드에 띄울 최신 주가 데이터를 DB에서 꺼내 반환합니다.
    """
    try:
        conn = get_connection()
        
        # 가장 최근 날짜(Date DESC) 기준으로 정렬하여 limit 개수만큼 가져오기
        query = """
            SELECT Date, Ticker, Open, High, Low, Close, Volume, Change 
            FROM daily_stock_data 
            ORDER BY Date DESC, Ticker ASC
            LIMIT ?
        """
        
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        
        # 웹에 예쁘게 출력하기 위해 데이터 후처리 (선택 사항)
        if not df.empty and 'Change' in df.columns:
            # Change(등락률) 값을 퍼센트 단위로 소수점 2자리까지만 표시
            df['Change'] = (df['Change'] * 100).round(2)
            
            # 숫자에 콤마(,) 찍기 (예: 75000 -> 75,000)
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                df[col] = df[col].apply(lambda x: f"{int(x):,}" if pd.notnull(x) else "0")
            
        return df.to_dict(orient='records')
        
    except Exception as e:
        print(f"[DB 읽기 에러] {e}")
        return []

if __name__ == "__main__":
    init_db()

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# 현재 폴더(data)의 상위 폴더(프로젝트 최상위)를 인식시켜 다른 폴더의 파이썬 파일을 불러올 수 있게 합니다.
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# A2(질문자님)가 만든 DB 관리 기능 불러오기
from database.db_manager import save_daily_data, insert_stock
# A1 팀원이 만든 전처리 및 검증 기능 불러오기
from data.preprocessor import preprocess_stock_data
from data.validator import validate_stock_data

def fetch_stock_data(ticker, days=30):
    try:
        if ticker.isdigit():
            full_ticker = ticker + ".KS"
        else:
            full_ticker = ticker
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        stock = yf.Ticker(full_ticker)
        df = stock.history(start=start_date, end=end_date)
        if df.empty:
            print(f"[Warning] No data found for {full_ticker}")
            return pd.DataFrame()
        df = df.reset_index()
        return df
    except Exception as e:
        print(f"[Error] Fetching {ticker} failed: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    target_stocks = {
        "005930": "삼성전자",
        "000660": "SK하이닉스",
        "005380": "현대차",
        "035420": "NAVER",
        "000880": "한화"
    }
    print("--- 🚀 데이터 수집 ➔ 전처리 ➔ 검증 ➔ DB 저장 파이프라인 시작 ---")

    for ticker_code, ticker_name in target_stocks.items():
        print(f"\n[{ticker_name} ({ticker_code})] 작업 시작...")
        
        # 1. DB에 종목 기본 정보 먼저 만들기 (안 만들면 주가 저장 시 에러 발생)
        insert_stock(ticker_code, ticker_name)

        # 2. 인터넷에서 날것의 데이터 캐오기 (수집)
        raw_df = fetch_stock_data(ticker_code, days=30)
        if raw_df.empty:
            print(f"--- {ticker_name} 수집 실패 ---")
            continue

        # 3. 캐온 데이터 예쁘게 씻고 다듬기 (전처리)
        processed_df = preprocess_stock_data(raw_df)

        # 4. 다듬어진 데이터에 불량품은 없는지 깐깐하게 검사 (검증)
        is_ok, msg = validate_stock_data(processed_df, ticker_name)

        if is_ok:
            # 5. 검사를 통과한 완벽한 데이터만 DB 창고에 쏟아붓기 (저장)
            save_daily_data(ticker_code, processed_df)
            print(f"--- 🌟 {ticker_name} DB 저장 완료! ---")
        else:
            print(f"--- ❌ {ticker_name} 검증 통과 실패: {msg} ---")

    print("\n--- 🎉 모든 주식 데이터 수집 및 DB 저장 작업이 완료되었습니다! ---") 

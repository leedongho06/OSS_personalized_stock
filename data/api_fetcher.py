#!/usr/bin/env python3
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 특정 종목의 최근 데이터를 yfinance로 가져오는 함수
def fetch_stock_data(ticker, days=30):
    try:
        # yfinance는 한국 종목의 경우 '005930.KS' 형식을 사용해야 합니다.
        # 만약 숫자로만 들어오면 자동으로 .KS를 붙여주는 안전장치
        if ticker.isdigit():
            full_ticker = ticker + ".KS"
        else:
            full_ticker = ticker

        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 데이터 수집
        stock = yf.Ticker(full_ticker)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            print(f"[Warning] No data found for {full_ticker}")
            return pd.DataFrame()
            
        # 인덱스(Date)를 컬럼으로 빼고 정렬
        df = df.reset_index()
        return df
    except Exception as e:
        print(f"[Error] Fetching {ticker} failed: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    print("yfinance 데이터 수집 테스트 시작...")
    # 삼성전자(005930.KS) 테스트
    result = fetch_stock_data("005930")
    
    if not result.empty:
        print("\n--- 수집 성공 (최근 5일 데이터) ---")
        print(result.tail())
    else:
        print("\n--- 수집 실패: 위 에러 메시지를 확인하세요 ---")

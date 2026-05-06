#!/usr/bin/env python3
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

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
    # 1. 수집하고 싶은 종목 딕셔너리 (종목코드: 종목이름)
    target_stocks = {
        "005930": "삼성전자",
        "000660": "SK하이닉스",
        "005380": "현대차",
        "035420": "NAVER",
        "000880": "한화"
    }

    print("--- yfinance 다중 종목 데이터 수집 시작 ---")
    
    # 2. 반복문을 통해 각 종목별로 데이터 수집 및 출력
    for ticker_code, ticker_name in target_stocks.items():
        print(f"\n[{ticker_name} ({ticker_code})] 수집 중...")
        
        result = fetch_stock_data(ticker_code)
        
        if not result.empty:
            print(f"--- {ticker_name} 최근 5일 데이터 ---")
            # 가독성을 위해 Date, Open, High, Low, Close, Volume만 출력
            cols_to_show = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            print(result[cols_to_show].tail())
        else:
            print(f"--- {ticker_name} 수집 실패 ---")

    print("\n--- 모든 데이터 수집 작업 완료 ---")

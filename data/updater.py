import os
import sys
import time
import random
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# 프로젝트 루트 경로 설정 (에러 방지용 절대 경로)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# DB 매니저 임포트
from database.db_manager import save_daily_data, DB_PATH
import FinanceDataReader as fdr

def get_latest_date_in_db(ticker=None):
    print("[Data Engine] 로컬 자산 레포지토리 날짜 검증 중 ...")
    if not os.path.exists(DB_PATH):
        # DB 파일이 아예 없으면 30일 전부터 수집 시작
        return (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        # 테이블명 호환성을 위해 둘 다 확인
        try:
            query = "SELECT MAX(Date) FROM daily_stock_data"
            df = pd.read_sql(query, conn)
        except:
            query = "SELECT MAX(Date) FROM daily_prices"
            df = pd.read_sql(query, conn)
            
        conn.close()
        
        latest_date = df.iloc[0, 0]
        if latest_date:
            # 마지막으로 저장된 날짜의 '다음 날'부터 긁어오도록 설정
            next_day = datetime.strptime(latest_date, "%Y-%m-%d") + timedelta(days=1)
            return next_day.strftime("%Y-%m-%d")
            
    except Exception as e:
        pass
        
    return (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

def get_latest_date_from_db(ticker=None):
    """get_latest_in_db의 호환용 별칭 (ticker 인자 무시)."""
    return get_latest_date_in_db()

def run_daily_updater():
    start_date = get_latest_date_in_db()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if start_date > today:
        print("--- 이미 모든 데이터가 최신 상태입니다 ---")
        return
        
    print(f"--- {start_date} 부터 {today} 까지의 주가 데이터 수집 시작 ---")
    
    csv_path = os.path.join(BASE_DIR, 'data', 'stocks.csv')
    if not os.path.exists(csv_path):
        print("[오류] 대상 종목 리스트(stocks.csv)를 찾을 수 없습니다.")
        return
        
    stocks_df = pd.read_csv(csv_path)
    
    for index, row in stocks_df.iterrows():
        ticker = str(row['ticker']).zfill(6)
        name = row['name']
        
        try:
            # 주가 데이터 수집
            df = fdr.DataReader(ticker, start_date)
            
            # 주말이거나 상장폐지되어 데이터가 텅 비었다면 스킵
            if df.empty:
                continue
                
            # 💡 [핵심 해결 로직] 어떤 데이터가 들어와도 영어 포맷으로 강제 변환
            df = df.reset_index()
            
            # 1. 혹시 컬럼명이 한글이라면 영어로 바꿈
            rename_map = {
                '시가': 'Open', '고가': 'High', '저가': 'Low', 
                '종가': 'Close', '거래량': 'Volume', '등락률': 'Change', '날짜': 'Date'
            }
            df = df.rename(columns=rename_map)
            
            # 2. API가 Change(등락률)를 안 줬다면 Close(종가)를 바탕으로 직접 계산
            if 'Change' not in df.columns and 'Close' in df.columns:
                df['Change'] = df['Close'].pct_change().fillna(0)
                
            # 3. 필수 컬럼만 안전하게 필터링 (에러의 주범 원천 차단)
            required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Change']
            missing_cols = [c for c in required_cols if c not in df.columns]
            
            if missing_cols:
                print(f"   [경고] {name} : 데이터 누락으로 건너뜁니다 {missing_cols}")
                continue
                
            df = df[required_cols]
            
            # DB 저장
            save_daily_data(ticker, df)
            print(f"   [적재 완료] {name} ({ticker})")
            
        except Exception as e:
            print(f"   [오류] {name} : {e}")
            
        finally:
            # 차단 방지를 위한 유동적 휴식 (매우 중요)
            time.sleep(random.uniform(0.5, 1.2))
            
    print("--- 로컬 증분 데이터베이스 최신화 완료 ---")

if __name__ == "__main__": #pragma: no cover
    run_daily_updater()

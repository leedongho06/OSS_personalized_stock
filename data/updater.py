import os
import sys
import time
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import FinanceDataReader as fdr

# 상위 폴더의 모듈들을 불러오기 위한 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.preprocessor import preprocess_stock_data
from data.validator import validate_stock_data
from database.db_manager import save_daily_data  # 팀원 A2가 만든 저장 모듈 (이름은 실제에 맞게 수정 필요)

# 관심 기업 목록
TICKER_MAP = {
    "삼성전자": "005930", "SK하이닉스": "000660",
    "카카오": "035720", "NAVER": "035420",
    "신한지주": "055550", "KB금융": "105560", "하나금융지주": "086790", "우리금융지주": "316140",
    "셀트리온": "068270", "삼성바이오로직스": "207940",
    "현대차": "005380", "기아": "000270", "두산": "000150", "HD현대": "267250",
    "한국전력": "015760", "SK텔레콤": "017670", "KT": "030200", "LG유플러스": "032640",
    "LG화학": "051910", "롯데케미칼": "011170",
    "CJ제일제당": "097950", "농심": "004370", "오리온": "271560",
    "롯데쇼핑": "023530", "이마트": "139480"
}

DB_PATH = "database/stock_data.db"  # A2님이 설정한 DB 파일 경로

def get_latest_date_from_db(ticker_code):
    """
    [조회 로직] DB를 확인하여 해당 종목의 가장 마지막 데이터 날짜를 가져옵니다.
    """
    if not os.path.exists(DB_PATH):
        return None
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # daily_data 테이블에서 해당 종목의 가장 최근 날짜(MAX) 조회
        query = f"SELECT MAX(date) FROM daily_data WHERE ticker = '{ticker_code}'"
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return result[0]  # 예: '2026-05-19'
    except Exception as e:
        print(f"[Warning] DB에서 {ticker_code} 날짜 조회 실패: {e}")
        
    return None

def run_daily_updater():
    """
    [갱신 파이프라인] 비어있는 날짜를 계산하고, 수집-전처리-검증-저장 과정을 지휘합니다.
    """
    print("=== [Updater] 주식 데이터 최신화 파이프라인 가동 ===")
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    for name, code in TICKER_MAP.items():
        print(f"\n>>> [{name} ({code})] 업데이트 확인 중...")
        
        # 1. DB에서 마지막 저장 날짜 확인
        last_date_str = get_latest_date_from_db(code)
        
        if last_date_str:
            # 마지막 날짜 '다음 날'부터 수집 시작
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
            start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # 만약 DB 날짜가 오늘보다 크거나 같으면 수집 건너뜀 (이미 최신)
            if start_date > today_str:
                print("    [통과] 이미 최신화되어 있습니다.")
                continue
        else:
            # DB에 종목 자체가 없으면 최근 1년(365일) 데이터 초기 수집
            print("    [Info] DB에 기존 데이터 없음. 최근 1년 치 수집 진행.")
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

        print(f"    [수집] {start_date} ~ {today_str} 데이터 요청...")
        
        try:
            # 2. FDR 데이터 수집
            df = fdr.DataReader(code, start_date, today_str)
            
            if df.empty:
                print(f"    [스킵] 휴장일이거나 해당 기간의 수집 데이터가 없습니다.")
                continue
                
            # 3. 전처리 (날짜 꺼내기 포함)
            df = df.reset_index()
            
            # ★ 핵심: FDR 결과에는 종목코드(ticker)가 없으므로 DB 저장을 위해 명시적으로 추가
            df['ticker'] = code 
            
            clean_df = preprocess_stock_data(df)
            
            # 4. 유효성 검사 (품질 검증)
            is_ok, msg = validate_stock_data(clean_df, name)
            if not is_ok:
                print(f"    [검증 탈락] {msg}")
                continue
                
            # 5. DB 갱신 (저장)
            save_daily_data(code, clean_df)
            print(f"    [완료] {len(clean_df)}일 치 영업일 데이터 갱신 성공!")
            
            # 서버 차단 방지를 위한 매너 타임
            time.sleep(0.2)
            
        except Exception as e:
            print(f"    [에러 발생] {name} 갱신 중 실패: {e}")

    print("\n=== 모든 종목 최신화 작업 완료! ===")

if __name__ == "__main__":
    run_daily_updater()

import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
import os

# 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import save_daily_data
from data.preprocessor import preprocess_stock_data
from data.validator import validate_stock_data

# 성현님이 지정한 섹터별 핵심 기업 종목코드
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

def fetch_stock_data(ticker, days=30):
    """
    [테스트 및 개별 수집용 함수]
    지정한 종목의 최근 N일치 원시 데이터를 FDR을 통해 수집하여 반환합니다.
    """
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    try:
        df = fdr.DataReader(ticker, start_date, end_date)
        return df
    except Exception as e:
        print(f"   [API 에러] {ticker} 수집 실패: {e}")
        return pd.DataFrame()


def run_fdr_pipeline():
    print(f"--- 총 {len(TICKER_MAP)}개 우량 기업 데이터 수집 시작 (서버 차단 면역 모드) ---")
    
    for name, code in TICKER_MAP.items():
        print(f"\n>>> [{name} ({code})] 수집 중...")
        
        try:
            # 1. 분리한 수집 함수 호출 (중복 제거)
            df = fetch_stock_data(code, days=30)
            
            if df.empty:
                print(f"   [실패] 데이터 없음")
                continue
                
            # 2. 전처리
            df = df.reset_index()
            clean_df = preprocess_stock_data(df)
            
            # 3. 검증
            is_ok, msg = validate_stock_data(clean_df, name)
            if not is_ok:
                print(f"   [검증 탈락] {msg}")
                continue
                
            # 4. DB 저장
            save_daily_data(code, clean_df)
            time.sleep(0.1) # 안전하게 0.1초 휴식
            
        except Exception as e:
            print(f"   [에러 발생] {name}: {e}")

    print("\n--- 모든 섹터 종목 데이터 수집 및 DB 저장 완료! ---")

if __name__ == "__main__":
    # 이전에 설정한 가이드라인 안내 문구 유지
    print("\n" + "="*60)
    print("[Notice] 전체 데이터 수집 및 부분 최신화 파이프라인 가동은")
    print("         'python3 data/updater.py'를 실행하는 것을 권장합니다.")
    print("="*60 + "\n")

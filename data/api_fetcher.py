
#!/usr/bin/env python3
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
import os

# 경로 설정 (부모 폴더를 인식시켜 모듈 임포트 해결)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import save_daily_data
from data.preprocessor import preprocess_stock_data
from data.validator import validate_stock_data

# 성현님의 섹터 키워드
SECTOR_KEYWORDS = {
    "IT": ["삼성전자", "SK하이닉스"],
    "커뮤니케이션": ["카카오", "NAVER"],
    "금융": ["신한지주", "KB금융", "하나금융지주", "우리금융지주"],
    "헬스케어": ["셀트리온", "삼성바이오로직스"],
    "산업재": ["현대차", "기아", "두산", "HD현대"],
    "유틸리티": ["한국전력", "SK텔레콤", "KT", "LG유플러스"],
    "소재": ["LG화학", "롯데케미칼"],
    "필수소비재": ["CJ제일제당", "농심", "오리온"],
    "임의소비재": ["롯데쇼핑", "이마트"],
}

def get_ticker_map_fdr(keywords_dict):
    """FDR의 StockListing 기능을 이용해 매핑 테이블을 만듭니다."""
    print("FDR을 통해 상장사 목록 로드 중...")
    df_krx = fdr.StockListing('KRX') # 코스피, 코스닥, 코넥스 통합
    
    all_target_names = []
    for names in keywords_dict.values():
        all_target_names.extend(names)
    
    # { '삼성전자': '005930', ... } 형태 딕셔너리 생성
    ticker_map = df_krx[df_krx['Name'].isin(all_target_names)].set_index('Name')['Code'].to_dict()
    return ticker_map

def run_fdr_pipeline():
    TICKER_MAP = get_ticker_map_fdr(SECTOR_KEYWORDS)
    
    if not TICKER_MAP:
        print("수집할 종목을 찾지 못했습니다.")
        return

    print(f"총 {len(TICKER_MAP)}개 기업 수집 시작...")
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    for name, code in TICKER_MAP.items():
        print(f"\n>>> [{name} ({code})] 수집 중...")
        
        # 1. 수집 (FDR은 아주 심플합니다)
        df = fdr.DataReader(code, start_date, end_date)
        
        if df.empty:
            print(f"   [실패] 데이터 없음")
            continue
            
        # 2. 전처리 (FDR은 기본적으로 Date가 Index이므로 reset_index 필요)
        df = df.reset_index()
        clean_df = preprocess_stock_data(df)
        
        # 3. 검증
        is_ok, msg = validate_stock_data(clean_df, name)
        if not is_ok:
            print(f"   [검증 탈락] {msg}")
            continue
            
        # 4. DB 저장
        save_daily_data(code, clean_df)
        time.sleep(0.2) # FDR은 속도가 빨라 0.2초면 충분합니다.

if __name__ == "__main__":
    run_fdr_pipeline()

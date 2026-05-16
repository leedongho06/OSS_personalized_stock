import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# 우리가 만든 모듈들 임포트 (경로가 다를 경우 프로젝트 구조에 맞게 수정하세요)
try:
    from database.db_manager import save_daily_data
    from data.preprocessor import preprocess_stock_data
    from data.validator import validate_stock_data
except ImportError:
    print("[경고] 관련 모듈을 찾을 수 없습니다. 경로 설정을 확인해주세요.")

# 1. 성현님의 섹터 키워드 딕셔너리
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

def get_ticker_map_from_krx(keywords_dict):
    """
    KRX 상장사 목록을 긁어와서 키워드에 있는 기업들의 yfinance 티커 맵을 만듭니다.
    """
    print("KRX 종목 정보를 불러와 매핑 테이블을 생성 중...")
    url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
    
    try:
        krx_df = pd.read_html(url, header=0)[0]
        krx_df['종목코드'] = krx_df['종목코드'].apply(lambda x: str(x).zfill(6))
        
        # 키워드에 포함된 모든 기업명 추출
        all_target_names = []
        for names in keywords_dict.values():
            all_target_names.extend(names)
        all_target_names = set(all_target_names) # 중복 제거

        ticker_map = {}
        for _, row in krx_df.iterrows():
            if row['회사명'] in all_target_names:
                # 유가증권/코스닥 구분 없이 일단 .KS로 시도 후 에러 시 보정하는 전략
                # (보통 대형주는 .KS입니다)
                ticker_map[row['회사명']] = f"{row['종목코드']}.KS"
        
        return ticker_map
    except Exception as e:
        print(f"매핑 테이블 생성 실패: {e}")
        return {}

def fetch_stock_data(ticker_full, days=30):
    """yfinance를 이용해 주가 수집"""
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        stock = yf.Ticker(ticker_full)
        df = stock.history(start=start_date, end=end_date)
        
        # .KS로 검색 안 될 경우 .KQ(코스닥)로 재시도
        if df.empty and ".KS" in ticker_full:
            ticker_full = ticker_full.replace(".KS", ".KQ")
            stock = yf.Ticker(ticker_full)
            df = stock.history(start=start_date, end=end_date)

        if not df.empty:
            return df.reset_index(), ticker_full
    except Exception as e:
        print(f"[{ticker_full}] 수집 에러: {e}")
    return pd.DataFrame(), ticker_full

def run_sector_pipeline():
    # 2. 실시간으로 TICKER_MAP 생성
    TICKER_MAP = get_ticker_map_from_krx(SECTOR_KEYWORDS)
    
    if not TICKER_MAP:
        print("수집할 종목 정보를 찾지 못했습니다.")
        return

    print(f"총 {len(TICKER_MAP)}개 기업에 대한 파이프라인을 가동합니다.")

    for name, ticker in TICKER_MAP.items():
        print(f"\n>>> [{name} ({ticker})] 처리 중...")
        
        # 1. 수집 (재시도 로직 포함)
        raw_df, final_ticker = fetch_stock_data(ticker)
        if raw_df.empty:
            print(f"   [실패] 데이터를 가져오지 못했습니다.")
            continue
            
        # 2. 전처리
        clean_df = preprocess_stock_data(raw_df)
        
        # 3. 검증
        is_ok, msg = validate_stock_data(clean_df, name)
        if not is_ok:
            print(f"   [검증 탈락] {msg}")
            continue
            
        # 4. DB 저장
        try:
            save_daily_data(final_ticker.split('.')[0], clean_df) # 티커 코드만 저장
        except NameError:
            print("   [안내] save_daily_data가 정의되지 않아 출력을 대체합니다.")
            print(clean_df.head(2))
        
        time.sleep(1)

if __name__ == "__main__":
    run_sector_pipeline()

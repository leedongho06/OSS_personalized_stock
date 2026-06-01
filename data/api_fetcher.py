import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import time
import random  # 💡 패턴 우회를 위한 랜덤 모듈 추가
import sys
import os

# 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import save_daily_data
from data.preprocessor import preprocess_stock_data
from data.validator import validate_stock_data

# 섹터별 핵심 기업 종목코드 (100개 세트 완전 유지)
TICKER_MAP = {
    "삼성전자": "005930", "SK하이닉스": "000660", "POSCO홀딩스": "005490", "현대차": "005380",
    "기아": "000270", "NAVER": "035420", "LG화학": "051910", "삼성SDI": "006400",
    "카카오": "035720", "셀트리온": "068270", "LG": "003550", "삼성물산": "028260",
    "현대모비스": "012330", "SK이노베이션": "096770", "SK텔레콤": "017670", "KT": "030200",
    "신한지주": "055550", "KB금융": "105560", "하나금융지주": "086790", "우리금융지주": "316140",
    "삼성생명": "032830", "삼성전기": "009150", "삼성에스디에스": "018260", "SK": "034730",
    "HMM": "011200", "고려아연": "010130", "넷마블": "251270", "포스코인터내셔널": "047050",
    "LG전자": "066570", "한화솔루션": "009830", "대한항공": "003490", "아모레퍼시픽": "090430",
    "S-Oil": "010950", "한국타이어앤테크놀로지": "161390", "삼성화재": "000810", "기업은행": "024110",
    "이마트": "139480", "LG이노텍": "011070", "CJ제일제당": "097950", "CJ": "001040",
    "코웨이": "021240", "SK스퀘어": "402340", "GS": "078930", "유한양행": "000100",
    "한화생명": "088350", "한국금융지주": "071050", "호텔신라": "008770", "한온시스템": "018880",
    "금호석유": "011780", "한미반도체": "042700", "현대건설": "000720", "한화시스템": "272210",
    "포스코퓨처엠": "003670", "SK바이오팜": "326030", "삼성바이오로직스": "207940", "한미약품": "128940",
    "엔씨소프트": "036570", "위메이드": "112040", "펄어비스": "263750", "JYP Ent.": "035900",
    "에스엠": "041510", "미래에셋증권": "006800", "삼성증권": "016360", "삼성카드": "029780",
    "한진칼": "180640", "하이트진로": "000080", "GS리테일": "007070", "현대제철": "004020",
    "OCI홀딩스": "010060", "코스모화학": "005070", "영풍": "000670", "현대해상": "001450",
    "대동": "000490", "LS": "006260", "삼화콘덴서": "001820", "DB손해보험": "005830",
    "아모레G": "002790", "롯데케미칼": "004000", "롯데케미칼우": "011170", "롯데쇼핑": "023530",
    "롯데지주": "004990", "KT&G": "033780", "대림산업": "000210", "한국항공우주": "047810",
    "HD한국조선해양": "009540", "삼성중공업": "010140", "한화오션": "042660", "HD현대": "267250",
    "HD현대중공업": "329180", "한국전력": "015760", "한국가스공사": "036460", "STX중공업": "071970",
    "한국전력우": "011155", "두산": "000150", "두산에너빌리티": "034020", "두산밥캣": "241560",
    "하이브": "352820", "태광산업": "003240", "한미사이언스": "008930", "휴젤": "145020"
}

def fetch_stock_data(ticker, days=30):
    """
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
    
    for i, (name, code) in enumerate(TICKER_MAP.items(), start=1):
        print(f"\n>>> [{i}/{len(TICKER_MAP)}] [{name} ({code})] 수집 중...")
        
        try:
            # 1. 분리한 수집 함수 호출
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
            print(f"   [적재 완료] {len(clean_df)}일 치 빌드 성공")
            
            # 💡 [핵심 보완] 고정 0.1초 대신 1.0초 ~ 2.2초 사이의 유동적인 무작위 딜레이 패턴 주입
            # 기계적인 매크로 수집 패턴을 흩트려서 백엔드 포털 서버의 탐지 엔진을 우회합니다.
            delay = random.uniform(1.0, 2.2)
            print(f"   [대기] 트래픽 안정화를 위해 {delay:.2f}초간 휴식합니다...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"   [에러 발생] {name}: {e}")

    print("\n--- 모든 섹터 종목 데이터 수집 및 DB 저장 완료! ---")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("[Notice] 전체 데이터 수집 및 부분 최신화 파이프라인 가동은")
    print("         'python3 data/updater.py'를 실행하는 것을 권장합니다.")
    print("="*60 + "\n")
    
    run_fdr_pipeline()

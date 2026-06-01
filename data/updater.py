import os
import sys
import time
import random
import sqlite3
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta

# 상위 폴더의 모듈들을 불러오기 위한 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.preprocessor import preprocess_stock_data
from data.validator import validate_stock_data
from database.db_manager import save_daily_data, DB_PATH, TABLE_NAME

# 100개 핵심 기업 종목코드 맵
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

def get_latest_date_in_db() -> str:
    """DB에 저장되어 있는 가장 최신 데이터의 날짜를 yyyy-mm-dd 형식으로 반환합니다."""
    if not os.path.exists(DB_PATH):
        return ""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT MAX(date) FROM {TABLE_NAME}")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row and row[0] else ""
    except Exception:
        return ""

def fetch_stock_data(ticker, start_date, end_date):
    """지정한 범위의 주가 데이터를 FDR을 통해 수집합니다."""
    try:
        df = fdr.DataReader(ticker, start_date, end_date)
        return df
    except Exception as e:
        print(f"   [API 에러] {ticker} 수집 실패: {e}")
        return pd.DataFrame()

def run_daily_updater():
    """날짜를 체크하여 누락된 데이터만 스마트하게 스마트 갱신하는 코어 파이프라인"""
    print("\n[Data Engine] 로컬 자산 레포지토리 날짜 검증 중...")
    
    latest_db_date = get_latest_date_in_db()
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # 1. 기저 데이터가 아예 없는 경우 -> 최초 1회 전체 빌드 (최근 30일치)
    if not latest_db_date:
        print("   -> 💡 로컬 DB가 비어있습니다. 최초 1회 초기 전체 빌드를 시작합니다 (30일 분량).")
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    else:
        # 2. 날짜가 동일한 경우 -> 장 마감 전이거나 오늘 이미 업데이트 완료됨 (스킵)
        if latest_db_date == today_str:
            print(f"   -> ✅ 데이터가 최신 상태입니다 (최신 기록일: {latest_db_date}). 동적 업데이트를 스킵합니다.")
            return
        
        # 3. 날짜가 다른 경우 -> 마지막 저장일 다음 날부터 오늘까지 수집 범위 최적화
        last_dt = datetime.strptime(latest_db_date, '%Y-%m-%d')
        start_date = (last_dt + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 만약 금요일 장 마감 후 주말(토/일) 동안 실행하는 것이라면, start_date가 오늘보다 미래일 수 있으므로 안전 가드
        if start_date > today_str:
            print(f"   -> ✅ 영업일 기준 최신 상태입니다. (최신 기록일: {latest_db_date}).")
            return

        print(f"   -> 🔄 날짜 바뀜 감지! 업데이트 범위: [{start_date}] ~ [{today_str}]")

    total_stocks = len(TICKER_MAP)
    print(f"--- 총 {total_stocks}개 우량 기업 증분 데이터 적재 가동 ---")
    
    for i, (name, code) in enumerate(TICKER_MAP.items(), start=1):
        try:
            df = fetch_stock_data(code, start_date=start_date, end_date=today_str)
            
            if df.empty:
                continue
                
            df = df.reset_index()
            clean_df = preprocess_stock_data(df)
            
            if clean_df.empty:
                continue
            
            is_ok, msg = validate_stock_data(clean_df, name)
            if not is_ok:
                continue
                
            save_daily_data(code, clean_df)
            print(f"   [{i}/{total_stocks}] [{name}] 증분 데이터 적재 완료 (+{len(clean_df)}일)")
            
            # 네트워크 부하 방지 무작위 딜레이 (0.3 ~ 0.8초로 갱신 시에는 소폭 단축)
            time.sleep(random.uniform(0.3, 0.8))
            
        except Exception as e:
            print(f"   [오류] {name}: {e}")

    print("--- 로컬 증분 데이터베이스 최신화 완료 ---")

if __name__ == "__main__":
    run_daily_updater()

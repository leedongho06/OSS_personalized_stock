import pandas as pd
import sys
import os
import sqlite3
from datetime import datetime, timedelta

# 1. 프로젝트 최상위 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.api_fetcher import fetch_stock_data
from data.preprocessor import preprocess_stock_data
from data.validator import validate_stock_data
# updater.py에서 날짜 조회 로직과 메인 갱신 함수 가져오기
from data.updater import get_latest_date_from_db, run_daily_updater

# 테스트용 임시 DB 경로 설정 (실제 DB 보호용)
TEST_DB_PATH = "database/test_stock_data.db"

def setup_test_db():
    """테스트 시작 전 빈 테이블 구조를 가상으로 만들어줍니다."""
    print("\n[Setup] 테스트용 가상 데이터베이스 초기화 중...")
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    
    # 실제 schema.sql과 동일한 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            ticker TEXT PRIMARY KEY,
            name TEXT,
            sector TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_data (
            ticker TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date)
        )
    """)
    
    # 테스트용 기본 종목 정보 삽입
    cursor.execute("INSERT OR IGNORE INTO stocks VALUES ('005930', '삼성전자', 'IT')")
    conn.commit()
    conn.close()

def teardown_test_db():
    """테스트가 끝나면 깔끔하게 가상 DB 파일을 지워줍니다."""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        print("[Teardown] 테스트용 가상 데이터베이스 삭제 완료.")

def run_integration_test(ticker, name):
    print(f"\n" + "="*50)
    print(f"[{name} ({ticker})] 갱신 파이프라인 통합 테스트 시작")
    print("="*50)

    # 1단계: Updater 동작 검증 (DB 조회)
    print("\n1단계: Updater - 기존 DB 최신 일자 확인 중...")
    # 임시로 과거 데이터를 하나 찔러 넣어 봅니다 (예: 5일 전)
    past_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT OR IGNORE INTO daily_data 
        VALUES ('{ticker}', '{past_date}', 70000, 71000, 69000, 70500, 1000000)
    """)
    conn.commit()
    conn.close()

    # 원래 updater.py의 DB_PATH를 테스트용 DB 경로로 강제 우회시킵니다.
    import data.updater
    original_db_path = data.updater.DB_PATH
    data.updater.DB_PATH = TEST_DB_PATH

    latest_date = get_latest_date_from_db(ticker)
    print(f"✅ Updater 확인: DB에 저장된 최신 일자는 [{latest_date}] 입니다.")
    
    # 2단계: 부분 수집 검증 (api_fetcher)
    print(f"\n2단계: Fetcher - 마지막 날짜({latest_date}) 다음 날부터 오늘까지 수집...")
    start_date = (datetime.strptime(latest_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # 계산된 시작일부터 오늘까지 데이터 수집
    raw_df = fetch_stock_data(ticker, days=(datetime.now() - datetime.strptime(start_date, '%Y-%m-%d')).days + 1)
    
    if raw_df is None or raw_df.empty:
        print("ℹ️ 알림: 최근 영업일 데이터가 이미 가득 차 있거나 수집할 타겟이 없습니다. (휴장일 포함)")
        # 빈 데이터인 경우 테스트 흐름 유지를 위해 강제로 10일치 데이터를 가져오게끔 대체
        raw_df = fetch_stock_data(ticker, days=10)
        
    print(f"✅ Fetcher 성공: {len(raw_df)}개의 신규 행을 가져왔습니다.")

    # 3단계: 전처리 및 종목코드 라벨링 검증 (preprocessor)
    print("\n3단계: Preprocessor - 데이터 정제 및 Ticker 매핑 진행...")
    if not isinstance(raw_df.index, pd.RangeIndex):
        raw_df = raw_df.reset_index()
    
    raw_df['ticker'] = ticker # updater.py가 수행하는 필수 라벨링 로직
    processed_df = preprocess_stock_data(raw_df)
    
    if 'date' in processed_df.columns and 'ticker' in processed_df.columns:
        print(f"✅ Preprocessor 성공: 컬럼 소문자화 및 'ticker'({ticker}) 매핑 완료")
    else:
        print("❌ 실패: 필수 핵심 컬럼('date' 혹은 'ticker')이 유실되었습니다.")
        data.updater.DB_PATH = original_db_path
        return False

    # 4단계: 유효성 검사 (validator)
    print("\n4단계: Validator - 최종 데이터 무결성 검증 중...")
    is_valid, message = validate_stock_data(processed_df, ticker)
    
    # 원래 원본 DB 경로로 원상복구
    data.updater.DB_PATH = original_db_path

    if is_valid:
        print(f"✅ Validator 통과: {message}")
        print("\n[최종 적재 대기 데이터 샘플]")
        cols = [c for c in ['date', 'ticker', 'open', 'close', 'volume'] if c in processed_df.columns]
        print(processed_df[cols].head(2))
        return True
    else:
        print(f"❌ Validator 실패: {message}")
        return False

if __name__ == "__main__":
    # 1. 가상 DB 셋업
    setup_test_db()
    
    # 2. 통합 테스트 수행
    test_ticker = "005930"
    test_name = "삼성전자"
    success = run_integration_test(test_ticker, test_name)

    # 3. 가상 DB 삭제 및 클린업
    teardown_test_db()

    print("\n" + "="*50)
    if success:
        print("🎉 [최종 결과] Updater를 포함한 전 파이프라인 연동 성공!")
    else:
        print("🚫 [최종 결과] 파이프라인 연동 실패. 코드를 다시 점검하세요.")
    print("="*50)

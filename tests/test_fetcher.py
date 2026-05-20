import pandas as pd
from api_fetcher import fetch_stock_data
from preprocessor import preprocess_stock_data
from validator import validate_stock_data

def run_integration_test(ticker, name):
    print(f"\n" + "="*50)
    print(f"[{name} ({ticker})] 통합 테스트 시작")
    print("="*50)

    # 1단계: 수집 (api_fetcher)
    print("\n1단계: 데이터 수집 중...")
    raw_df = fetch_stock_data(ticker, days=10) # 테스트용으로 최근 10일치만 수집
    
    if raw_df.empty:
        print("❌ 실패: 데이터를 수집하지 못했습니다.")
        return False
    print(f"✅ 수집 성공: {len(raw_df)}개의 행을 가져왔습니다.")

    # 2단계: 전처리 (preprocessor)
    print("\n2단계: 데이터 전처리 진행 중...")
    processed_df = preprocess_stock_data(raw_df)
    
    # 전처리 후 날짜 컬럼 확인
    if 'date' in processed_df.columns:
        print(f"✅ 전처리 성공: 컬럼명 소문자 변환 및 날짜 형식 정리 완료")
    else:
        print("❌ 실패: 전처리 과정에서 'date' 컬럼을 찾을 수 없습니다.")
        return False

    # 3단계: 유효성 검사 (validator)
    print("\n3단계: 데이터 유효성 검사 진행 중...")
    is_valid, message = validate_stock_data(processed_df, ticker)
    
    if is_valid:
        print(f"✅ 검사 통과: {message}")
        print("\n[최종 데이터 샘플 (상위 3건)]")
        print(processed_df[['date', 'open', 'close', 'volume']].head(3))
        return True
    else:
        print(f"❌ 검사 실패: {message}")
        return False

if __name__ == "__main__":
    # 테스트할 종목 선정 (대표 종목 삼성전자)
    test_ticker = "005930"
    test_name = "삼성전자"

    success = run_integration_test(test_ticker, test_name)

    print("\n" + "="*50)
    if success:
        print("🎉 [최종 결과] 모든 파이프라인이 정상적으로 작동합니다!")
    else:
        print("🚫 [최종 결과] 파이프라인에 문제가 발견되었습니다. 코드를 확인하세요.")
    print("="*50)

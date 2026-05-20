import pandas as pd

def validate_stock_data(df, ticker):
    """
    데이터의 유효성을 검사하여 (성공여부, 메시지)를 반환합니다.
    """
    # 1. 빈 데이터 체크
    if df is None or df.empty:
        return False, f"[{ticker}] 데이터가 존재하지 않습니다."

    # 2. 필수 컬럼 체크
    required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    # 전처리 과정에서 소문자로 바꿨으므로 소문자로 체크합니다.
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        return False, f"[{ticker}] 필수 컬럼 누락: {missing_cols}"

    # 3. 수치 데이터 논리성 체크
    # 가격이나 거래량이 0 이하일 수 없습니다.
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_cols:
        if (df[col] <= 0).any():
            return False, f"[{ticker}] {col} 컬럼에 0 이하의 잘못된 값이 있습니다."

    # 4. 고가/저가 논리 체크
    if (df['low'] > df['high']).any():
        return False, f"[{ticker}] 저가가 고가보다 높은 데이터 오류가 있습니다."

    # 5. 날짜 중복 체크 (DB PK 충돌 방지)
    if df['date'].duplicated().any():
        return False, f"[{ticker}] 날짜가 중복된 데이터가 있습니다."

    return True, "Success"

if __name__ == "__main__":
    # 테스트용 정상 데이터
    sample_df = pd.DataFrame({
        'date': ['2026-04-16', '2026-04-17'],
        'open': [72000, 73000],
        'high': [73000, 74000],
        'low': [71000, 72000],
        'close': [72500, 73500],
        'volume': [1000000, 1200000]
    })
    
    is_ok, msg = validate_stock_data(sample_df, "SAMSUNG")
    print(f"검증 결과: {is_ok}, 메시지: {msg}")

import pandas as pd

def validate_stock_data(df, ticker):
    """
    데이터의 유효성을 검사하여 (성공여부, 메시지)를 반환합니다.
    yfinance 호환성 및 다중 데이터 형식(MultiIndex 등) 방어 레이어가 추가되었습니다.
    """
    # 1. 빈 데이터 체크
    if df is None or df.empty:
        return False, f"[{ticker}] 데이터가 존재하지 않습니다."

    # [🔥 yfinance 대응] yfinance는 가끔 컬럼이 MultiIndex(예: ('Close', '005930.KS'))로 반환될 수 있습니다.
    # 혹은 단일 인덱스더라도 문자열 처리를 위해 컬럼명을 1차원 문자열 리스트로 단순화합니다.
    try:
        if isinstance(df.columns, pd.MultiIndex):
            # 상위 레벨(Open, High, Low...)만 추출하여 단일 인덱스로 평탄화
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [str(col).lower() for col in df.columns]
    except Exception as e:
        return False, f"[{ticker}] 컬럼명 평탄화 및 소문자 변환 실패: {e}"

    # 2. 필수 컬럼 체크
    required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        return False, f"[{ticker}] 필수 컬럼 누락: {missing_cols}"

    # 3. 수치 데이터 논리성 체크
    # [🔥 yfinance 대응] yfinance는 가끔 거래량(volume)을 float64나 객체 타입으로 들고 오면서
    # 누락된 일자에 NaN(결측치)을 채워 넣거나, 소수점 형태로 가져올 수 있습니다. 안전하게 수치형 변환 후 검증합니다.
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_cols:
        # 데이터가 비어있거나 NaN이 채워진 경우 방어
        if df[col].isnull().any():
            return False, f"[{ticker}] {col} 컬럼에 누락된 값(NaN)이 존재합니다."
            
        # 0 이하의 잘못된 값 체크
        if (df[col] <= 0).any():
            return False, f"[{ticker}] {col} 컬럼에 0 이하의 잘못된 값이 있습니다."

    # 4. 고가/저가 논리 체크
    if (df['low'] > df['high']).any():
        return False, f"[{ticker}] 저가가 고가보다 높은 데이터 오류가 있습니다."

    # 5. 날짜 중복 체크 (DB PK 충돌 방지)
    if df['date'].duplicated().any():
        return False, f"[{ticker}] 날짜가 중복된 데이터가 있습니다."

    return True, "Success"

if __name__ == "__main__": #pragma: no cover
    # 테스트용 정상 데이터
    sample_df = pd.DataFrame({
        'date': ['2026-04-16', '2026-04-17'],
        'open': [72000, 73000],
        'high': [73000, 74000],
        'low': [71000, 72000],
        'close': [72500, 73500],
        'volume': [1000000, 1200000]
    })
    
    # 셈플 데이터 검증 진행
    is_ok, msg = validate_stock_data(sample_df, "SAMSUNG")
    print(f"검증 결과: {is_ok}, 메시지: {msg}")

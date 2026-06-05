import pandas as pd
import numpy as np

def preprocess_stock_data(df):
    # 1. 데이터가 비어있으면 그대로 반환
    if df is None or df.empty:
        return pd.DataFrame()

    # 복사본 생성 (원본 훼손 방지)
    processed_df = df.copy()

    # 2. 컬럼명 정리 (yfinance는 대문자 시작, DB는 소문자)
    # db_manager.py에서 lower() 처리를 하지만, 여기서 미리 맞춰주는게 안전
    processed_df.columns = [col.lower() for col in processed_df.columns]

    # 3. 결측치(NaN) 처리
    # 주식 데이터에서 결측치는 보통 전날 가격을 그대로 사용(Forward Fill)하거나
    # 데이터가 아예 없는 행은 삭제합니다.
    processed_df = processed_df.dropna(subset=['close']) # 종가가 없으면 삭제
    processed_df = processed_df.ffill()   # 중간에 빈 값은 이전 값으로 채움

    # 4. 날짜 형식 통일 (YYYY-MM-DD)
    if 'date' in processed_df.columns:
        processed_df['date'] = pd.to_datetime(processed_df['date']).dt.strftime('%Y-%m-%d')

    # 5. 중복 데이터 제거 (ticker와 date가 같은 데이터 방지)
    if 'date' in processed_df.columns:
        processed_df = processed_df.drop_duplicates(subset=['date'])
    
    if 'change' in processed_df.columns:
        processed_df = processed_df.drop(columns=['change'])

    return processed_df

if __name__ == "__main__": #pragma:no cover
    # 테스트용 가짜 데이터
    test_data = pd.DataFrame({
        'Date': ['2026-04-15', '2026-04-16', '2026-04-16'], # 중복 날짜
        'Close': [70000, np.nan, 71000],                   # 결측치
        'Volume': [1000000, 1100000, 1100000]
    })
    
    print("--- 전처리 전 ---")
    print(test_data)
    
    result = preprocess_stock_data(test_data)
    
    print("\n--- 전처리 후 ---")
    print(result)

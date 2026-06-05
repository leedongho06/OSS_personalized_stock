import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from recommendation.profile import get_feature_cols, get_ideal

def build_feature_matrix(df: pd.DataFrame):
    cols = get_feature_cols()
    feature_df = df[cols].copy()

    # 숫자형으로 변환
    for col in cols:
        feature_df[col] = pd.to_numeric(feature_df[col], errors="coerce")

    # 결측값 처리
    feature_df = feature_df.fillna(feature_df.median())

    # 그래도 NaN 있으면 0으로
    feature_df = feature_df.fillna(0)

    scaler = MinMaxScaler()
    matrix = scaler.fit_transform(feature_df)
    return matrix, scaler

def get_ideal_vector(style: str, scaler: MinMaxScaler) -> np.ndarray:
    cols = get_feature_cols()
    profile = get_ideal(style)
    
    # 투자 스타일 데이터 중 누락된 값이 있다면 0으로 안전하게 처리합니다.
    raw = np.array([[profile.get(col, 0) if pd.notna(profile.get(col)) else 0 for col in cols]])
    
    ideal_vec = scaler.transform(raw)
    
    # 최종 벡터 내 결측치 처리
    ideal_vec = np.nan_to_num(ideal_vec, nan=0.0)
    
    return ideal_vec

def recommend(df: pd.DataFrame, style: str, top_n: int = 5) -> pd.DataFrame:
    if df.empty:
        print("  추천 가능한 종목이 없습니다.")
        return pd.DataFrame()

    matrix, scaler = build_feature_matrix(df)
    ideal_vec = get_ideal_vector(style, scaler)
    
    # 결측치가 완벽히 제거된 상태에서 안정적으로 코사인 유사도를 계산합니다.
    scores = cosine_similarity(ideal_vec, matrix).flatten()

    result = df.copy()
    result["score"] = scores
    actual_n = min(top_n, len(result))  # 종목 수가 요청한 n개보다 부족할 때 처리
    
    # 기존 코드의 컬럼 추출 구조 유지
    result = (
        result.sort_values("score", ascending=False)
              .head(actual_n)[["ticker", "name", "sector", "per", "pbr", "score"]]
              .reset_index(drop=True)
    )
    result["score"] = result["score"].round(4)
    return result

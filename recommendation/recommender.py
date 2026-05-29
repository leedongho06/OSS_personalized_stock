import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from recommendation.profile import get_feature_cols, get_ideal

def build_feature_matrix(df: pd.DataFrame):
    cols = get_feature_cols()
    
    # 1차 처리: 각 컬럼의 중앙값(median)으로 빈 값을 채웁니다.
    feature_df = df[cols].fillna(df[cols].median())
    
    # 2차 처리(안전 패치): 특정 컬럼 전체가 NaN이어서 median도 NaN인 경우를 대비해 0으로 한 번 더 채웁니다.
    feature_df = feature_df.fillna(0)
    
    scaler = MinMaxScaler()
    matrix = scaler.fit_transform(feature_df)
    
    # 정규화 계산 과정에서 생길 수 있는 결측치를 최종 방어합니다.
    matrix = np.nan_to_num(matrix, nan=0.0)
    
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

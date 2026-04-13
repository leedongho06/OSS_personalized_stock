import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from recommendation.profile import get_feature_cols, get_ideal

def build_feature_matrix(df:pd.DataFrame):
	cols = get_feature_cols()
	feature_df= df[cols].fillna(df[cols].median())
	scaler = MinMaxScaler()
	matrix = scaler.fit_transform(feature_df)
	return matrix, scaler

def get_ideal_vector(style: str, scaler: MinMaxScaler) -> np.ndarray:
	cols = get_feature_cols()
	profile= get_ideal(style)
	raw = np.array([[profile[col] for col in cols]])
	return scaler.transform(raw)

def recommend(df: pd.DataFrame, style:str, top_n: int = 5) -> pd.DataFrame:
	if df.empty:
	   return pd.DataFrame()
	matrix, scaler = build_feature_matrix(df)
	ideal_vec = get_ideal_vector(style,scaler)
	scores = cosine_similarity(ideal_vec, matrix).flatten()

	result = df.copy()
	result["score"] = scores
	result = (
		result.sort_values("score", ascending=False)
		      .head(top_n)[["ticker","name","sector","per","pbr","score"]]
		      .reset_index(drop=True)
		)
	result["score"] = result["score"].round(4)
	return result

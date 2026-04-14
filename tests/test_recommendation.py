import pandas as pd
from recommendation.scorer import infer_style
from recommendation.filter import filter_stocks
from recommendation.recommender import recommend

def test_infer_style_aggressive():
	style, score, _ = infer_style(["kakao","SK_hynix"])
	assert style == "aggresive"

def test_infer_style_stable():
	style, score, _ = infer_style(["Shinhan"])
	assert style == "stable"

def test_infer_style_empty():
	style, score, _ = infer_style([])
	assert style == "empty"

def test_filter_stocks():
	df = pd.read.csv("data/dummy.csv")
	filtered = filter_stocks(df, "aggressive")
	assert len(filtered) > 0
	assert all(filtered["sector"].isin(["IT","communicaiton","industrial"])

def test_recommend_returns_topn():
	df = pd.read_csv("data/dummy.csv")
	filtered = filter_stocks(df,"aggressive")
	result = recommend(filtered, "aggressive", top_n=2)
	assert len(result)<=2
	assert "score" in result.columns

def test_recommend_empty_df():
	result = recommend(pd.DataFrame(), "aggressive")
	assert result.empty

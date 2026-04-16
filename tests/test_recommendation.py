import pandas as pd
from recommendation.scorer import infer_style
from recommendation.filter import filter_stocks
from recommendation.recommender import recommend


def test_infer_style_aggressive():
    style, score, _ = infer_style(["카카오", "SK하이닉스"])
    assert style == "공격형"


def test_infer_style_stable():
    style, score, _ = infer_style(["신한지주"])
    assert style == "안정형"


def test_infer_style_empty():
    style, score, _ = infer_style([])
    assert style == "중립형"


def test_filter_stocks():
    df = pd.read_csv("data/dummy.csv")
    filtered = filter_stocks(df, "공격형")
    assert len(filtered) > 0
    assert all(filtered["sector"].isin(["IT", "커뮤니케이션", "임의소비재"]))


def test_recommend_returns_topn():
    df = pd.read_csv("data/dummy.csv")
    filtered = filter_stocks(df, "공격형")
    result = recommend(filtered, "공격형", top_n=2)
    assert len(result) <= 2
    assert "score" in result.columns


def test_recommend_empty_df():
    result = recommend(pd.DataFrame(), "공격형")
    assert result.empty

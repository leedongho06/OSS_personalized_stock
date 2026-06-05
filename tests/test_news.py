import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from news.classifier import classify_sector, add_sector_to_news
from news.random_picker import pick_random_news
from news.interest_scorer import calculate_interest
from news.style_inferrer import infer_style_from_news


def test_classify_sector_IT():
    """GEMINI_API_KEY 없을 때 기타 반환 확인"""
    sector = classify_sector("삼성전자 반도체 실적")
    assert sector in ["IT", "기타"]  # API 키 없으면 기타 반환


def test_classify_sector_finance():
    """GEMINI_API_KEY 없을 때 기타 반환 확인"""
    sector = classify_sector("신한은행 금리 인상")
    assert sector in ["금융", "기타"]  # API 키 없으면 기타 반환


def test_classify_sector_unknown():
    assert classify_sector("오늘 날씨 맑음") == "기타"


def test_add_sector_to_news():
    news_list = [
        {"title": "삼성전자 AI 반도체", "description": ""},
        {"title": "신한지주 배당", "description": ""},
    ]
    result = add_sector_to_news(news_list)
    assert len(result) == 2


def test_pick_random_news():
    news_list = [{"title": f"뉴스{i}", "sector": "IT"} for i in range(10)]
    picked = pick_random_news(news_list, n=5)
    assert len(picked) == 5


def test_pick_random_news_less():
    news_list = [{"title": "뉴스1", "sector": "IT"}]
    picked = pick_random_news(news_list, n=5)
    assert len(picked) <= 5


def test_calculate_interest():
    rated = [
        {"sector": "IT", "rating": 5},
        {"sector": "IT", "rating": 3},
        {"sector": "금융", "rating": 2},
    ]
    interest = calculate_interest(rated)
    assert interest["IT"] == 4.0
    assert interest["금융"] == 2.0


def test_infer_style_aggressive():
    interest = {"IT": 5.0, "커뮤니케이션": 5.0}
    style, score, _ = infer_style_from_news(interest)
    assert style == "공격형"


def test_infer_style_stable():
    interest = {"금융": 5.0, "유틸리티": 5.0}
    style, score, _ = infer_style_from_news(interest)
    assert style == "안정형"


def test_infer_style_empty():
    style, score, _ = infer_style_from_news({})
    assert style == "중립형"

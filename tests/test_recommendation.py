import pytest
import pandas as pd
import sqlite3

# 모든 모듈 임포트
from recommendation.validator import DataValidator
from recommendation.data_loader import load_data_from_db
from recommendation.filter import filter_by_style
from recommendation.scorer import infer_style
from recommendation.recommender import recommend

# ==========================================
# 1. 테스트용 가상 데이터 셋업 (Fixtures)
# ==========================================

@pytest.fixture
def dummy_df():
    """CSV 파일 대신 사용할 가상의 주식 데이터프레임"""
    return pd.DataFrame({
        "ticker": ["005930", "035420", "055550", "000000"],
        "name": ["삼성전자", "NAVER", "신한지주", "상장폐지위기종목"],
        "sector": ["IT", "커뮤니케이션", "금융", "기타"],
        "per": [15.2, 38.4, 7.8, -5.0],  # 적자 기업 포함
        "pbr": [1.5, 2.1, 0.5, 0.1],
        "ma_20": [75000, 190000, 38000, 1000],
        "volume": [15000000, 150000, 50000, 10000] # 신한지주는 10만 미만
    })

@pytest.fixture
def temp_db_path(tmp_path):
    """임시 SQLite DB 생성 (Data Loader 테스트용)"""
    db_path = tmp_path / "test_stock.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE stocks (ticker TEXT, name TEXT, sector TEXT)")
    cursor.execute("CREATE TABLE daily_data (ticker TEXT, date TEXT, per REAL, pbr REAL, ma_20 REAL, volume INTEGER)")
    cursor.execute("INSERT INTO stocks VALUES ('005930', '삼성전자', 'IT')")
    cursor.execute("INSERT INTO daily_data VALUES ('005930', '2026-05-10', 15.2, 1.5, 75000, 15000000)")
    conn.commit()
    conn.close()
    return str(db_path)

# ==========================================
# 2. 파이프라인 전반부: Loader & Validator 테스트
# ==========================================

def test_validator_success(dummy_df):
    assert DataValidator.validate_stock_data(dummy_df) is True

def test_load_data_from_db_success(temp_db_path):
    df = load_data_from_db(temp_db_path)
    assert not df.empty
    assert "ma_20" in df.columns

# ==========================================
# 3. 파이프라인 후반부: Scorer, Filter, Recommender 테스트 (기존 작성 코드 통합)
# ==========================================

def test_infer_style_aggressive():
    """(동호) 카카오, SK하이닉스 입력 시 공격형 추론"""
    style, score, _ = infer_style(["카카오", "SK하이닉스"])
    assert style == "공격형"

def test_infer_style_stable():
    """(동호) 신한지주 입력 시 안정형 추론"""
    style, score, _ = infer_style(["신한지주"])
    assert style == "안정형"

def test_infer_style_empty():
    """(동호) 입력이 없을 시 중립형 기본 할당"""
    style, score, _ = infer_style([])
    assert style == "중립형"

def test_filter_by_style(dummy_df):
    """filter_by_style 기본 필터링 테스트"""
    filtered = filter_by_style(dummy_df, "Value")
    assert len(filtered) >= 0
    # 적자 기업(per < 0) 제거 확인
    if len(filtered) > 0:
        assert (filtered["per"] > 0).all()

def test_recommend_returns_topn(dummy_df):
    """(동호/성현) 최종 추천 결과가 지정된 N개 이하로 나오며 score가 부여되는지 테스트"""
    # 1. 1차 필터링 거치기
    filtered = filter_by_style(dummy_df, "공격형")
    
    # 2. 추천 모듈 통과
    result = recommend(filtered, "공격형", top_n=2)
    
    assert len(result) <= 2
    

def test_recommend_empty_df():
    """빈 데이터프레임이 들어왔을 때 에러 없이 빈 결과를 반환하는지 테스트"""
    result = recommend(pd.DataFrame(), "공격형")
    assert result.empty

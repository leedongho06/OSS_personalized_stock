import sys
import os
import pytest
import pandas as pd

# 프로젝트 루트 경로 추가 (Import 에러 방지)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 필요한 함수들을 모두 import 합니다.
from data.data_loader import load_data_from_db, load_feedback_data

def test_load_data_no_db_file():
    """시나리오 1: 데이터베이스 파일이 없을 때 빈 DataFrame 반환 확인"""
    df = load_data_from_db("non_existent.db")
    assert df.empty == True

def test_load_feedback_no_db():
    """시나리오 2: DB 파일이 없을 때 빈 피드백 DataFrame 반환 확인"""
    df = load_feedback_data("non_existent.db")
    assert df.empty == True
    # 필수 컬럼이 포함되어 있는지 확인
    expected_cols = ["user_id", "ticker", "preference", "reason"]
    assert list(df.columns) == expected_cols

def test_load_data_success_mock(monkeypatch):
    """시나리오 3: 정상적으로 데이터를 읽어왔을 때 유효성 검사 통과 여부"""
    sample_df = pd.DataFrame({
        'ticker': ['005930'], 'name': ['삼성'], 'sector': ['IT'],
        'per': [15.0], 'pbr': [1.0], 'ma_20': [70000.0], 'volume': [1000]
    })
    
    # pd.read_sql_query를 가짜 함수로 바꿔서 실제 DB 파일이 없어도 테스트 가능하게 만듦
    def mock_read_sql(q, c):
        return sample_df
        
    monkeypatch.setattr(pd, "read_sql_query", mock_read_sql)
    
    df = load_data_from_db("data/stock_data.db")
    assert not df.empty
    assert df.iloc[0]['ticker'] == '005930'

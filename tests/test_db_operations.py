import pytest
import pandas as pd
import numpy as np
import sqlite3
from database import db_manager

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch, tmp_path):
    """안전한 격리용 임시 DB 환경 구축"""
    test_db_path = str(tmp_path / "test_stock.db")
    monkeypatch.setattr("database.db_manager.DB_PATH", test_db_path)
    db_manager.init_db()


# ==============================================================================
# 1. 기존 정상 작동 테스트
# ==============================================================================

def test_save_and_get_data():
    ticker = "005930"
    df = pd.DataFrame({
        'Date': ['2026-06-05'],
        'Open': [70000.0], 'High': [71000.0], 'Low': [69000.0],
        'Close': [70500.0], 'Volume': [10000], 'Change': [0.01]
    })
    
    db_manager.save_daily_data(ticker, df)
    results = db_manager.get_recent_stocks_for_web(limit=1)
    
    assert len(results) == 1
    assert results[0]['Ticker'] == '005930'
    assert results[0]['Close'] == '70,500'


def test_save_daily_data_replace():
    ticker = "005930"
    df1 = pd.DataFrame({'Date': ['2026-06-05'], 'Open': [70000.0], 'High': [71000.0], 'Low': [69000.0], 'Close': [70000.0], 'Volume': [1000], 'Change': [0]})
    df2 = pd.DataFrame({'Date': ['2026-06-05'], 'Open': [70000.0], 'High': [71000.0], 'Low': [69000.0], 'Close': [80000.0], 'Volume': [1000], 'Change': [0]})
    
    db_manager.save_daily_data(ticker, df1)
    db_manager.save_daily_data(ticker, df2)
    
    results = db_manager.get_recent_stocks_for_web(limit=1)
    assert results[0]['Close'] == '80,000'


def test_get_recent_stocks_empty():
    results = db_manager.get_recent_stocks_for_web()
    assert results == []


# ==============================================================================
# 2. 방어/예외 로직 테스트 (커버리지 100% 달성용)
# ==============================================================================

def test_save_daily_data_datetime_index():
    """인덱스 이름이 명시적으로 'Date'일 때의 방어 로직 테스트 (44번 줄 등 커버)"""
    df = pd.DataFrame({
        'Open': [70000.0], 'High': [71000.0], 'Low': [69000.0],
        'Close': [70500.0], 'Volume': [10000], 'Change': [0.01]
    }, index=pd.to_datetime(['2026-06-05']))
    df.index.name = 'Date'
    
    db_manager.save_daily_data("005930", df)
    results = db_manager.get_recent_stocks_for_web(limit=1)
    assert results[0]['Date'] == '2026-06-05'

# 💡 [새로 추가된 핵심 코드] 57번 줄 완벽 저격!
def test_save_daily_data_no_date_name():
    """인덱스 이름이 비어있어서 'index'라는 임시 컬럼이 생길 때의 로직(57번 줄) 커버"""
    df = pd.DataFrame({
        'Open': [70000.0], 'High': [71000.0], 'Low': [69000.0],
        'Close': [70500.0], 'Volume': [10000], 'Change': [0.01]
    })
    # 인덱스에 날짜는 넣지만, 이름(name)을 지정하지 않음 -> 기본값 None
    df.index = pd.to_datetime(['2026-06-06'])
    
    db_manager.save_daily_data("005930", df)
    results = db_manager.get_recent_stocks_for_web(limit=1)
    # 가장 마지막에 저장된(limit=1이므로 최신순 정렬에 의해) 6일자 데이터 확인
    assert results[0]['Date'] == '2026-06-06'


def test_save_daily_data_empty():
    """빈 데이터프레임 방어 로직 테스트"""
    db_manager.save_daily_data("005930", pd.DataFrame())
    db_manager.save_daily_data("005930", None)
    assert True


def test_get_recent_stocks_exception(monkeypatch):
    """데이터 조회 중 DB 에러 시 예외 처리 테스트"""
    def force_error(*args, **kwargs):
        raise sqlite3.Error("DB 조회 강제 에러")
    monkeypatch.setattr(sqlite3, "connect", force_error)
    
    results = db_manager.get_recent_stocks_for_web()
    assert results == []

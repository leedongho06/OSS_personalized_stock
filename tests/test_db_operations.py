import pytest
import pandas as pd
from database import db_manager

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch, tmp_path):
    """
    :memory: 대신 pytest가 제공하는 안전한 임시 폴더(tmp_path)에 
    진짜 파일 형태의 임시 DB를 만듭니다. (테스트 종료 시 자동 삭제됨)
    """
    # 1. 임시 파일 경로 생성 (예: /tmp/pytest-of-user/test_stock.db)
    test_db_path = str(tmp_path / "test_stock.db")
    
    # 2. db_manager의 DB_PATH를 이 임시 파일 경로로 덮어쓰기
    monkeypatch.setattr("database.db_manager.DB_PATH", test_db_path)
    
    # 3. 임시 파일에 테이블 생성 (파일 형태라 close() 해도 안 날아갑니다!)
    db_manager.init_db()

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

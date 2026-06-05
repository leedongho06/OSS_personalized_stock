import unittest
import pandas as pd
import os
import sqlite3
from datetime import datetime, timedelta

from data.api_fetcher import fetch_stock_data
from data.preprocessor import preprocess_stock_data
from data.validator import validate_stock_data
import data.updater  # 모듈 통째로 임포트

TEST_DB_PATH = "database/test_stock_data.db"

class TestStockPipeline(unittest.TestCase):
    def setUp(self):
        # 💡 가장 확실한 방법: 여기서 강제로 실제 모듈의 DB 경로를 덮어씌웁니다!
        self.original_db_path = data.updater.DB_PATH
        data.updater.DB_PATH = TEST_DB_PATH

        os.makedirs(os.path.dirname(TEST_DB_PATH), exist_ok=True)
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        
        # 이전 테스트가 실패해서 남은 찌꺼기 테이블 초기화
        cursor.execute("DROP TABLE IF EXISTS daily_stock_data")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stock_data (
                Date TEXT, Ticker TEXT, Open REAL, High REAL, Low REAL, Close REAL, Volume INTEGER, Change REAL,
                PRIMARY KEY (Date, Ticker)
            )
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        # 💡 테스트 종료 후 원래 실제 DB 경로로 원상 복구!
        data.updater.DB_PATH = self.original_db_path
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    def test_integration_pipeline(self):
        ticker = "005930"
        past_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        
        # 가짜 DB에 데이터 주입
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO daily_stock_data VALUES ('{past_date}', '{ticker}', 70000, 71000, 69000, 70500, 1000000, 0.0)")
        conn.commit()
        conn.close()

        # 검증 시작
        expected_next = (datetime.strptime(past_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        latest_date = data.updater.get_latest_date_in_db(ticker)
        self.assertEqual(latest_date, expected_next)
        
        raw_df = fetch_stock_data(ticker, days=10) 
        self.assertIsNotNone(raw_df)
        self.assertFalse(raw_df.empty)

        if not isinstance(raw_df.index, pd.RangeIndex):
            raw_df = raw_df.reset_index()
        raw_df['ticker'] = ticker
        processed_df = preprocess_stock_data(raw_df)
        
        self.assertIn('date', processed_df.columns)
        self.assertIn('ticker', processed_df.columns)

        is_valid, _ = validate_stock_data(processed_df, ticker)
        self.assertTrue(is_valid)

if __name__ == '__main__':
    unittest.main()

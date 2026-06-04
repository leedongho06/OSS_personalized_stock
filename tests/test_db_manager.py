import unittest
import os
import tempfile
from unittest.mock import patch

# 테스트할 원본 모듈 임포트
import news.db_manager as dbm

class TestDBManager(unittest.TestCase):
    def setUp(self):
        """각 테스트가 실행되기 직전에 한 번씩 호출되어 안전한 가짜 DB 환경을 만듭니다."""
        # 1. 임시 파일 생성
        self.test_db_fd, self.test_db_path = tempfile.mkstemp(suffix='.db')
        
        # 2. db_manager.py 안의 DB_PATH 변수를 임시 DB 경로로 가로채기(Mocking)
        self.patcher = patch('news.db_manager.DB_PATH', self.test_db_path)
        self.patcher.start()
        
        # 3. 임시 DB에 테이블 초기화
        dbm.init_news_table()
        dbm.init_trade_table()

    def tearDown(self):
        """각 테스트가 끝나면 호출되어 가짜 DB를 싹 지웁니다."""
        self.patcher.stop()
        os.close(self.test_db_fd)
        os.unlink(self.test_db_path)

    # ==========================================
    # 뉴스 테이블 테스트
    # ==========================================
    def test_save_and_load_news(self):
        dummy_news = [
            {"title": "삼성전자 역대급 실적", "description": "반도체 훈풍", "sector": "IT", "link": "http://test.com/1"},
            {"title": "현대차 전기차 올인", "description": "아이오닉 대박", "sector": "자동차", "link": "http://test.com/2"}
        ]
        
        dbm.save_news(dummy_news)
        
        self.assertEqual(dbm.get_news_count(), 2)
        
        loaded = dbm.load_news(limit=5)
        self.assertEqual(len(loaded), 2)
        
        titles = [n['title'] for n in loaded]
        self.assertIn("삼성전자 역대급 실적", titles)
        self.assertIn("현대차 전기차 올인", titles)

    def test_save_news_prevents_duplicates(self):
        dummy_news = [{"title": "중복 뉴스", "description": "내용1", "sector": "IT", "link": ""}]
        
        dbm.save_news(dummy_news)
        self.assertEqual(dbm.get_news_count(), 1)
        
        # 동일한 데이터 재저장 시도
        dbm.save_news(dummy_news)
        # 갯수가 늘어나지 않아야 함
        self.assertEqual(dbm.get_news_count(), 1)

    # ==========================================
    # 매매일지 테이블 테스트
    # ==========================================
    def test_save_and_load_trades(self):
        dbm.save_trade(name="NAVER", trade_type="매수", price=200000)
        
        trades = dbm.load_trades()
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]["name"], "NAVER")
        self.assertEqual(trades[0]["trade_type"], "매수")
        self.assertEqual(trades[0]["price"], 200000)

    def test_trade_profit_rate_calculation(self):
        dbm.save_trade(name="카카오", trade_type="매도", price=120000, buy_price=100000, sell_price=120000)
        
        trades = dbm.load_trades()
        self.assertEqual(trades[0]["profit_rate"], 20.0)

    def test_update_trade_rating(self):
        dbm.save_trade(name="SK하이닉스", trade_type="매수", price=150000)
        trades_before = dbm.load_trades()
        trade_id = trades_before[0]["id"]
        
        dbm.update_trade_rating(trade_id, rating=5)
        
        trades_after = dbm.load_trades()
        self.assertEqual(trades_after[0]["rating"], 5)

if __name__ == '__main__':
    unittest.main()

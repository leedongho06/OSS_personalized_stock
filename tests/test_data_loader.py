import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from data.data_loader import load_data_from_db, load_feedback_data

class TestDataLoader(unittest.TestCase):

    # ==========================================
    # 1. load_data_from_db 함수 테스트
    # ==========================================
    
    @patch('data.data_loader.os.path.exists')
    def test_load_data_no_db(self, mock_exists):
        """DB 파일이 존재하지 않을 때 빈 DataFrame을 반환하는지 테스트"""
        mock_exists.return_value = False # 파일이 없다고 가짜로 설정
        
        result = load_data_from_db("dummy_stock.db")
        self.assertTrue(result.empty)

    @patch('data.data_loader.sqlite3.connect')
    @patch('data.data_loader.pd.read_sql_query')
    @patch('data.data_loader.os.path.exists')
    def test_load_data_success(self, mock_exists, mock_read_sql, mock_connect):
        """DB 파일이 존재하고 쿼리가 성공했을 때 데이터를 잘 반환하는지 테스트"""
        mock_exists.return_value = True
        
        # 가짜 DB 응답 데이터 세팅
        dummy_df = pd.DataFrame({"date": ["2026-04-15"], "close": [70000]})
        mock_read_sql.return_value = dummy_df
        
        result = load_data_from_db("dummy_stock.db")
        
        self.assertFalse(result.empty)
        self.assertEqual(result.iloc[0]["close"], 70000)
        
        # 커넥션이 정상적으로 열리고 닫혔는지 검증
        mock_connect.assert_called_once_with("dummy_stock.db")
        mock_connect.return_value.close.assert_called_once()

    @patch('data.data_loader.sqlite3.connect')
    @patch('data.data_loader.os.path.exists')
    def test_load_data_exception(self, mock_exists, mock_connect):
        """DB 연결이나 쿼리 도중 에러(Exception)가 났을 때 죽지 않고 빈 DataFrame을 반환하는지 테스트"""
        mock_exists.return_value = True
        mock_connect.side_effect = Exception("DB 연결 실패 시뮬레이션")
        
        result = load_data_from_db("dummy_stock.db")
        self.assertTrue(result.empty)


    # ==========================================
    # 2. load_feedback_data 함수 테스트
    # ==========================================
    
    @patch('data.data_loader.os.path.exists')
    def test_load_feedback_no_db(self, mock_exists):
        """피드백 DB 파일이 없을 때 지정된 4개의 컬럼을 가진 빈 DataFrame을 반환하는지 테스트"""
        mock_exists.return_value = False
        
        result = load_feedback_data("dummy_feedback.db")
        self.assertTrue(result.empty)
        # 피드백 함수는 단순 빈 df가 아니라 특정 컬럼이 세팅된 df를 반환해야 함
        self.assertListEqual(list(result.columns), ["user_id", "ticker", "preference", "reason"])

    @patch('data.data_loader.sqlite3.connect')
    @patch('data.data_loader.pd.read_sql_query')
    @patch('data.data_loader.os.path.exists')
    def test_load_feedback_success(self, mock_exists, mock_read_sql, mock_connect):
        """피드백 DB에서 정상적으로 데이터를 불러오는지 테스트"""
        mock_exists.return_value = True
        
        dummy_df = pd.DataFrame({
            "user_id": [1], 
            "ticker": ["삼성전자"], 
            "preference": [1.0], 
            "reason": ["실적 호조"]
        })
        mock_read_sql.return_value = dummy_df
        
        result = load_feedback_data("dummy_feedback.db")
        
        self.assertFalse(result.empty)
        self.assertEqual(result.iloc[0]["ticker"], "삼성전자")
        mock_connect.return_value.close.assert_called_once()

    @patch('data.data_loader.sqlite3.connect')
    @patch('data.data_loader.os.path.exists')
    def test_load_feedback_exception(self, mock_exists, mock_connect):
        """피드백 로드 중 에러 발생 시 지정된 4개의 컬럼을 가진 빈 DataFrame을 반환하는지 테스트"""
        mock_exists.return_value = True
        mock_connect.side_effect = Exception("쿼리 실행 에러 시뮬레이션")
        
        result = load_feedback_data("dummy_feedback.db")
        self.assertTrue(result.empty)
        self.assertListEqual(list(result.columns), ["user_id", "ticker", "preference", "reason"])

if __name__ == '__main__':
    unittest.main()

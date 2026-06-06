import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
import os

# updater 파일에서 사용할 함수들을 가져옵니다.
from data.updater import get_latest_date_in_db, get_latest_date_from_db, run_daily_updater

class TestUpdater(unittest.TestCase):
    
    # ========================================================
    # 1. get_latest_date_in_db() 함수 테스트 파트
    # ========================================================

    @patch('data.updater.os.path.exists')
    def test_get_latest_date_no_db(self, mock_exists):
        """1. DB 파일이 없을 때 30일 전 날짜를 안전하게 반환하는지 테스트"""
        mock_exists.return_value = False
        result = get_latest_date_in_db()
        expected = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.assertEqual(result, expected)

    @patch('data.updater.sqlite3.connect')
    @patch('data.updater.pd.read_sql')
    @patch('data.updater.os.path.exists')
    def test_get_latest_date_success_first_table(self, mock_exists, mock_read_sql, mock_connect):
        """2. daily_stock_data 테이블에서 마지막 날짜를 잘 가져와 다음 날을 반환하는지 테스트"""
        mock_exists.return_value = True
        mock_read_sql.return_value = pd.DataFrame({'MAX(Date)': ['2026-04-15']})
        result = get_latest_date_in_db()
        # 15일의 다음 날인 16일이 반환되어야 함
        self.assertEqual(result, '2026-04-16')

    @patch('data.updater.sqlite3.connect')
    @patch('data.updater.pd.read_sql')
    @patch('data.updater.os.path.exists')
    def test_get_latest_date_success_second_table(self, mock_exists, mock_read_sql, mock_connect):
        """3. 첫 번째 테이블 조회가 실패했을 때, 두 번째 테이블(daily_prices)에서 잘 가져오는지 테스트"""
        mock_exists.return_value = True
        # 첫 번째 쿼리(side_effect[0])는 강제 에러, 두 번째 쿼리(side_effect[1])는 정상 반환
        mock_read_sql.side_effect = [Exception("Table not found"), pd.DataFrame({'MAX(Date)': ['2026-04-15']})]
        result = get_latest_date_in_db()
        self.assertEqual(result, '2026-04-16')

    @patch('data.updater.sqlite3.connect')
    @patch('data.updater.os.path.exists')
    def test_get_latest_date_exception(self, mock_exists, mock_connect):
        """4. DB가 심하게 꼬여서 조회 중 에러가 나면 뻗지 않고 30일 전 날짜로 폴백하는지 테스트"""
        mock_exists.return_value = True
        mock_connect.side_effect = Exception("DB Connection Error")
        result = get_latest_date_in_db()
        expected = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.assertEqual(result, expected)

    @patch('data.updater.get_latest_date_in_db')
    def test_get_latest_date_from_db_alias(self, mock_func):
        """5. 호환용 별칭 함수가 원본 함수를 잘 물고 들어가는지 테스트"""
        mock_func.return_value = '2026-04-16'
        result = get_latest_date_from_db()
        self.assertEqual(result, '2026-04-16')

    # ========================================================
    # 2. run_daily_updater() 메인 루프 테스트 파트
    # ========================================================

    @patch('data.updater.get_latest_date_in_db')
    def test_run_updater_already_up_to_date(self, mock_get_date):
        """6. DB의 최신 날짜가 내일 이후일 때(이미 최신) 쿨하게 스킵하는지 테스트"""
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        mock_get_date.return_value = future_date
        # 함수가 아무것도 안하고 즉시 리턴해야 함
        run_daily_updater()

    @patch('data.updater.os.path.exists')
    @patch('data.updater.get_latest_date_in_db')
    def test_run_updater_no_csv(self, mock_get_date, mock_exists):
        """7. 종목 리스트(stocks.csv) 파일이 아예 없을 때 오류를 뱉고 안전 종료하는지 테스트"""
        mock_get_date.return_value = '2026-01-01'
        mock_exists.return_value = False 
        run_daily_updater()

    @patch('data.updater.time.sleep')
    @patch('data.updater.save_daily_data')
    @patch('data.updater.fdr.DataReader')
    @patch('data.updater.pd.read_csv')
    @patch('data.updater.os.path.exists')
    @patch('data.updater.get_latest_date_in_db')
    def test_run_updater_main_logic(self, mock_get_date, mock_exists, mock_read_csv, mock_fdr, mock_save, mock_sleep):
        """8. 메인 루프: 정상, 상장폐지, 컬럼 누락, 통신 에러 등 4가지 악조건을 모두 돌려보는 종합 검증"""
        mock_get_date.return_value = '2026-04-10'
        mock_exists.return_value = True 
        
        # 4가지 케이스를 강제로 태우기 위한 가짜 종목 리스트
        mock_read_csv.return_value = pd.DataFrame({
            'ticker': ['005930', '000000', '111111', '999999'],
            'name': ['정상종목', '상장폐지', '누락종목', '통신장애']
        })

        # --- 가짜 주가 데이터 세팅 ---
        # 케이스 1. 정상 (Change 컬럼이 없어서 로직 내부에서 pct_change()로 자동 계산되는지도 함께 체크)
        df_normal = pd.DataFrame({
            'Date': ['2026-04-10', '2026-04-11'], 
            '시가': [100, 110], '고가': [200, 210], '저가': [50, 60], '종가': [150, 165], '거래량': [1000, 1100]
        }).set_index('Date') 

        # 케이스 2. 상장폐지/주말 (비어있음)
        df_empty = pd.DataFrame()

        # 케이스 3. 일부 컬럼 누락 (Open만 있고 Close나 Volume이 없음)
        df_missing = pd.DataFrame({
            'Date': ['2026-04-10'], 'Open': [100] 
        }).set_index('Date')

        # fdr.DataReader가 종목코드별로 각기 다른 악조건을 반환하도록 설계
        def fdr_side_effect(ticker, start):
            if ticker == '005930': return df_normal
            if ticker == '000000': return df_empty
            if ticker == '111111': return df_missing
            if ticker == '999999': raise Exception("API 서버 터짐")

        mock_fdr.side_effect = fdr_side_effect

        # 대망의 함수 실행
        run_daily_updater()

        # [검증 1] 4종목 중 오직 '정상종목(005930)' 1개만 save_daily_data에 도달했어야 함!
        self.assertEqual(mock_save.call_count, 1)
        
        # [검증 2] try~finally 구조 특성상 중간에 continue나 에러가 났어도 sleep은 4번 모두 호출되어야 함!
        self.assertEqual(mock_sleep.call_count, 4)

if __name__ == "__main__":
    unittest.main()

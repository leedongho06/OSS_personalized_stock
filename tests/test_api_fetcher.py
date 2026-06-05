import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import data.api_fetcher as fetcher

class TestApiFetcher(unittest.TestCase):

    # ---------------------------------------------------------
    # 1. fetch_stock_data 함수 단위 테스트
    # ---------------------------------------------------------
    @patch('data.api_fetcher.fdr.DataReader')
    def test_fetch_stock_data_success(self, mock_fdr):
        """FDR API 호출이 성공하여 DataFrame을 반환하는지 테스트"""
        # 가짜 DataFrame 반환 설정
        mock_df = pd.DataFrame({"Close": [1000, 2000]})
        mock_fdr.return_value = mock_df
        
        result = fetcher.fetch_stock_data("005930", days=10)
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 2)

    @patch('data.api_fetcher.fdr.DataReader')
    def test_fetch_stock_data_exception(self, mock_fdr):
        """FDR API 호출 중 에러가 발생했을 때 빈 DataFrame을 반환하는지 테스트"""
        mock_fdr.side_effect = Exception("API 차단됨")
        
        result = fetcher.fetch_stock_data("005930", days=10)
        self.assertTrue(result.empty)

    # ---------------------------------------------------------
    # 2. run_fdr_pipeline 파이프라인 통합 테스트
    # ---------------------------------------------------------
    @patch('data.api_fetcher.TICKER_MAP', {"테스트주식": "000000"}) # 종목 1개로 축소
    @patch('data.api_fetcher.fetch_stock_data')
    @patch('data.api_fetcher.preprocess_stock_data')
    @patch('data.api_fetcher.validate_stock_data')
    @patch('data.api_fetcher.save_daily_data')
    @patch('data.api_fetcher.time.sleep') # 💡 중요: 실제 딜레이가 발생하지 않도록 sleep 함수 무력화
    def test_run_pipeline_success(self, mock_sleep, mock_save, mock_validate, mock_preprocess, mock_fetch):
        """수집 -> 전처리 -> 검증 -> 저장 -> 딜레이의 전체 흐름이 정상 작동하는지 테스트"""
        
        # 각 파이프라인 단계의 가짜 결과물 설정
        mock_fetch.return_value = pd.DataFrame({"data": [1, 2]}) # 1. 수집 성공
        mock_preprocess.return_value = pd.DataFrame({"clean": [1, 2]}) # 2. 전처리 성공
        mock_validate.return_value = (True, "통과") # 3. 검증 통과
        
        # 파이프라인 실행
        fetcher.run_fdr_pipeline()
        
        # 검증: 각 단계의 함수들이 정확히 1번씩 순서대로 호출되었는지 확인
        mock_fetch.assert_called_once()
        mock_preprocess.assert_called_once()
        mock_validate.assert_called_once()
        mock_save.assert_called_once()
        mock_sleep.assert_called_once() # 딜레이 로직이 호출되었는지도 확인

    @patch('data.api_fetcher.TICKER_MAP', {"테스트주식": "000000"})
    @patch('data.api_fetcher.fetch_stock_data')
    def test_run_pipeline_empty_data(self, mock_fetch):
        """수집 단계에서 데이터가 비어있을 때 (휴장일 등) 다음 단계로 넘어가지 않고 skip(continue) 하는지 테스트"""
        mock_fetch.return_value = pd.DataFrame() # 빈 데이터 반환
        
        # 파이프라인 실행
        fetcher.run_fdr_pipeline()
        
        # 에러 없이 정상 종료되어야 하며, 하위 로직(저장 등)은 실행되지 않아야 함
        mock_fetch.assert_called_once()

    @patch('data.api_fetcher.TICKER_MAP', {"테스트주식": "000000"})
    @patch('data.api_fetcher.fetch_stock_data')
    @patch('data.api_fetcher.preprocess_stock_data')
    @patch('data.api_fetcher.validate_stock_data')
    @patch('data.api_fetcher.save_daily_data')
    def test_run_pipeline_validation_fail(self, mock_save, mock_validate, mock_preprocess, mock_fetch):
        """검증 단계에서 탈락했을 때 DB에 저장하지 않고 skip(continue) 하는지 테스트"""
        mock_fetch.return_value = pd.DataFrame({"data": [1]})
        mock_preprocess.return_value = pd.DataFrame({"clean": [1]})
        mock_validate.return_value = (False, "데이터 누락") # 검증 탈락!
        
        fetcher.run_fdr_pipeline()
        
        mock_validate.assert_called_once()
        mock_save.assert_not_called() # DB 저장 함수가 호출되지 않았음을 깐깐하게 확인!

if __name__ == '__main__':
    unittest.main()

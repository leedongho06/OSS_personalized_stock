import unittest
from unittest.mock import MagicMock, PropertyMock
import pandas as pd
import numpy as np
from data.validator import validate_stock_data

class TestValidator(unittest.TestCase):

    def setUp(self):
        """매 테스트마다 사용할 정상적인 기본(Sample) 데이터 세팅"""
        self.valid_df = pd.DataFrame({
            'date': ['2026-04-16', '2026-04-17'],
            'open': [72000, 73000],
            'high': [73000, 74000],
            'low': [71000, 72000],
            'close': [72500, 73500],
            'volume': [1000000, 1200000]
        })

    def test_empty_or_none_df(self):
        """1. 데이터가 아예 없거나 None일 때 실패하는지 테스트"""
        is_ok, msg = validate_stock_data(None, "TEST")
        self.assertFalse(is_ok)
        self.assertIn("데이터가 존재하지 않습니다", msg)

        is_ok, msg = validate_stock_data(pd.DataFrame(), "TEST")
        self.assertFalse(is_ok)
        self.assertIn("데이터가 존재하지 않습니다", msg)

    def test_multiindex_columns(self):
        """2-1. yfinance 특유의 MultiIndex 컬럼이 들어왔을 때 평탄화가 잘 되는지 테스트"""
        df = self.valid_df.copy()
        # MultiIndex 강제 생성 (예: 'Close', '005930.KS')
        df.columns = pd.MultiIndex.from_tuples([(col.capitalize(), '005930.KS') for col in df.columns])
        
        is_ok, msg = validate_stock_data(df, "TEST")
        self.assertTrue(is_ok)
        self.assertEqual(msg, "Success")

    def test_column_flattening_exception(self):
        """2-2. 컬럼명 변환 중 예기치 않은 에러(Exception)가 발생했을 때 프로그램이 죽지 않고 방어되는지 테스트"""
        # mock 객체로 DataFrame을 위장한 뒤, columns 속성에 접근할 때 강제로 에러 발생
        mock_df = MagicMock()
        mock_df.empty = False
        type(mock_df).columns = PropertyMock(side_effect=Exception("강제 에러 발생"))
        
        is_ok, msg = validate_stock_data(mock_df, "TEST")
        self.assertFalse(is_ok)
        self.assertIn("컬럼명 평탄화 및 소문자 변환 실패", msg)

    def test_missing_required_columns(self):
        """3. 필수 컬럼 중 하나라도 누락되면 실패하는지 테스트"""
        df = self.valid_df.drop(columns=['volume']) # 볼륨 컬럼 삭제
        is_ok, msg = validate_stock_data(df, "TEST")
        self.assertFalse(is_ok)
        self.assertIn("필수 컬럼 누락", msg)

    def test_nan_in_numeric_columns(self):
        """4. 수치형 데이터에 결측치(NaN)가 있으면 실패하는지 테스트"""
        df = self.valid_df.copy()
        df.loc[0, 'close'] = np.nan # 종가 하나를 결측치로 훼손
        is_ok, msg = validate_stock_data(df, "TEST")
        self.assertFalse(is_ok)
        self.assertIn("누락된 값(NaN)이 존재합니다", msg)

    def test_zero_or_negative_values(self):
        """5. 주가나 거래량이 0 이하일 때 실패하는지 테스트"""
        df = self.valid_df.copy()
        df.loc[1, 'volume'] = 0 # 거래량을 0으로 훼손
        is_ok, msg = validate_stock_data(df, "TEST")
        self.assertFalse(is_ok)
        self.assertIn("0 이하의 잘못된 값", msg)

    def test_low_greater_than_high(self):
        """6. 저가가 고가보다 높은 말도 안되는 데이터일 때 실패하는지 테스트"""
        df = self.valid_df.copy()
        df.loc[0, 'low'] = 80000 # 저가를 8만원으로 변경 (고가는 7.3만원)
        is_ok, msg = validate_stock_data(df, "TEST")
        self.assertFalse(is_ok)
        self.assertIn("저가가 고가보다 높은 데이터 오류", msg)

    def test_duplicated_dates(self):
        """7. 날짜가 중복되어 들어왔을 때 DB 충돌 방지를 위해 실패하는지 테스트"""
        df = self.valid_df.copy()
        df.loc[1, 'date'] = '2026-04-16' # 두 번째 날짜를 첫 번째 날짜와 똑같이 변경
        is_ok, msg = validate_stock_data(df, "TEST")
        self.assertFalse(is_ok)
        self.assertIn("날짜가 중복된 데이터", msg)

    def test_valid_data_success(self):
        """8. 모든 검증을 통과한 완벽한 데이터일 때 Success를 반환하는지 테스트"""
        is_ok, msg = validate_stock_data(self.valid_df, "TEST")
        self.assertTrue(is_ok)
        self.assertEqual(msg, "Success")

if __name__ == "__main__":
    unittest.main()

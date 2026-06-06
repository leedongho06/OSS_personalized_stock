import unittest
import pandas as pd
import numpy as np
from data.preprocessor import preprocess_stock_data

class TestPreprocessor(unittest.TestCase):

    def test_empty_or_none_df(self):
        """1. 데이터가 None이거나 비어있을 때 빈 데이터프레임을 반환하는지 테스트"""
        # None 입력 시
        self.assertTrue(preprocess_stock_data(None).empty)
        
        # 빈 데이터프레임 입력 시
        empty_df = pd.DataFrame()
        self.assertTrue(preprocess_stock_data(empty_df).empty)

    def test_column_lowercasing_and_drop_change(self):
        """2 & 7. 컬럼명이 소문자로 잘 통일되는지, 그리고 'change' 컬럼이 삭제되는지 테스트"""
        df = pd.DataFrame({
            'Date': ['2026-04-15'],
            'Close': [70000],
            'Change': [0.5], # 대문자 Change 입력
            'Volume': [10000]
        })
        result = preprocess_stock_data(df)
        
        # 소문자로 변환되어 'date', 'close', 'volume'만 남아야 함
        self.assertIn('date', result.columns)
        self.assertIn('close', result.columns)
        self.assertIn('volume', result.columns)
        
        # 대문자 'Date'나 소문자로 변환 후 삭제된 'change'는 없어야 함
        self.assertNotIn('Date', result.columns)
        self.assertNotIn('change', result.columns)

    def test_missing_values_and_ffill(self):
        """3. 종가가 없는 행은 삭제(dropna)되고, 중간에 빈 값은 이전 값으로 채워지는지(ffill) 테스트"""
        df = pd.DataFrame({
            'Date': ['2026-04-15', '2026-04-16', '2026-04-17'],
            'Close': [70000, np.nan, 72000],  # 16일 종가가 누락됨 -> 16일 행은 아예 삭제되어야 함
            'Volume': [1000, np.nan, np.nan]  # 17일 거래량이 누락됨 -> 15일 거래량(1000)으로 채워져야 함
        })
        result = preprocess_stock_data(df)
        
        # 종가가 결측치인 두 번째 행이 날아갔으므로 총 2줄만 남아야 함
        self.assertEqual(len(result), 2)
        
        # 2026-04-17 데이터(인덱스 1번)의 볼륨 값이 15일 값인 1000.0으로 ffill 채워졌는지 확인
        self.assertEqual(result.iloc[1]['volume'], 1000.0)

    def test_date_formatting_and_duplicates(self):
        """4 & 5. 날짜 형식이 YYYY-MM-DD로 잘 포맷팅되고 중복 날짜가 제거되는지 테스트"""
        df = pd.DataFrame({
            # 이상한 날짜 포맷과 중복된 날짜 섞어 넣기
            'Date': ['2026/04/15 15:30:00', '2026-04-15', '2026-04-16'], 
            'Close': [70000, 71000, 72000]
        })
        result = preprocess_stock_data(df)
        
        # 첫 번째와 두 번째 행이 모두 '2026-04-15'로 변환되므로 중복이 제거되어 총 2행만 남음
        self.assertEqual(len(result), 2)
        
        # 날짜 포맷팅 확인
        self.assertEqual(result.iloc[0]['date'], '2026-04-15')
        self.assertEqual(result.iloc[1]['date'], '2026-04-16')

        # 중복 데이터 중 첫 번째 행(70000)이 보존되었는지 확인
        self.assertEqual(result.iloc[0]['close'], 70000)

if __name__ == "__main__":
    unittest.main()

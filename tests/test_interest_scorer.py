import unittest
import news.interest_scorer as is_module

class TestInterestScorer(unittest.TestCase):

    def test_calculate_interest_normal(self):
        """정상적인 데이터가 들어왔을 때 섹터별 평균이 정확히 계산되는지 테스트"""
        rated_news = [
            {"sector": "IT", "rating": 5},
            {"sector": "IT", "rating": 4},
            {"sector": "금융", "rating": 2},
            {"sector": "헬스케어", "rating": 5}
        ]
        
        # IT: (5+4)/2 = 4.5 | 금융: 2/1 = 2.0 | 헬스케어: 5/1 = 5.0
        expected = {
            "IT": 4.5,
            "금융": 2.0,
            "헬스케어": 5.0
        }
        result = is_module.calculate_interest(rated_news)
        self.assertEqual(result, expected)

    def test_calculate_interest_empty(self):
        """빈 리스트가 들어왔을 때 에러 없이 빈 딕셔너리를 반환하는지 테스트"""
        result = is_module.calculate_interest([])
        self.assertEqual(result, {})

    def test_calculate_interest_rounding(self):
        """무한 소수가 나올 때 소수점 둘째 자리까지 반올림(round)이 잘 적용되는지 테스트"""
        rated_news = [
            {"sector": "IT", "rating": 5},
            {"sector": "IT", "rating": 5},
            {"sector": "IT", "rating": 4}
        ]
        
        # 14 / 3 = 4.66666... -> 소수점 둘째 자리 반올림 시 4.67이 되어야 함
        result = is_module.calculate_interest(rated_news)
        self.assertEqual(result["IT"], 4.67)

if __name__ == '__main__':
    unittest.main()

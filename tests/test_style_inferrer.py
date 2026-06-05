import unittest
import news.style_inferrer as si

class TestStyleInferrer(unittest.TestCase):

    def test_infer_style_empty_interest(self):
        """1. 관심도 데이터가 아예 없을 때 (count == 0) 기본값 분기 검증"""
        style, normalized, analyses = si.infer_style_from_news({})
        
        self.assertEqual(style, "중립형")
        self.assertEqual(normalized, 5)
        self.assertEqual(analyses, [])

    def test_infer_style_aggressive_dominant(self):
        """2. 공격형 섹터(IT 등) 중심일 때 가중치(2) 및 '공격형' 성향 도출 검증"""
        interest = {"IT": 5.0, "커뮤니케이션": 5.0}
        
        # IT score = 2 * (5/5) = 2.0
        # 커뮤니케이션 score = 2 * (5/5) = 2.0
        # total_score = 4.0, count = 2 -> 평균 = 2.0
        # 정규화 점수 = round(2.0 * 4.5) = 9
        style, normalized, analyses = si.infer_style_from_news(interest)
        
        self.assertEqual(style, "공격형")
        self.assertEqual(normalized, 9)
        self.assertEqual(len(analyses), 2)
        self.assertEqual(analyses[0]["score"], 2.0)

    def test_infer_style_neutral_dominant(self):
        """3. 중립형 섹터(헬스케어 등) 중심일 때 가중치(1) 및 '중립형' 성향 도출 검증"""
        interest = {"헬스케어": 5.0}
        
        # 헬스케어 score = 1 * (5/5) = 1.0
        # total_score = 1.0, count = 1 -> 평균 = 1.0
        # 정규화 점수 = round(1.0 * 4.5) = 5
        style, normalized, _ = si.infer_style_from_news(interest)
        
        self.assertEqual(style, "중립형")
        self.assertEqual(normalized, 4)

    def test_infer_style_stable_dominant(self):
        """4. 안정형 섹터(금융 등) 중심일 때 가중치(0) 및 '안정형' 성향 도출 검증"""
        interest = {"금융": 5.0, "유틸리티": 3.0}
        
        # 금융 score = 0 * (5/5) = 0.0
        # 유틸리티 score = 0 * (3/5) = 0.0
        # total_score = 0.0 -> 정규화 점수 = 0
        style, normalized, _ = si.infer_style_from_news(interest)
        
        self.assertEqual(style, "안정형")
        self.assertEqual(normalized, 0)

    def test_infer_style_fallback_bound(self):
        """5. 복합 섹터 점수가 스타일 맵 경계선에 걸칠 때 정상 작동 검증"""
        # IT(공격형) 별점 2점 -> score = 2 * (2/5) = 0.8
        # total_score = 0.8, count = 1 -> 평균 = 0.8
        # 정규화 점수 = round(0.8 * 4.5) = round(3.6) = 4
        # 점수 4는 STYLE_MAP 상 (4, 6) 구간이므로 '중립형'에 해당
        interest = {"IT": 2.0}
        style, normalized, _ = si.infer_style_from_news(interest)
        
        self.assertEqual(style, "중립형")
        self.assertEqual(normalized, 4)

if __name__ == '__main__':
    unittest.main()

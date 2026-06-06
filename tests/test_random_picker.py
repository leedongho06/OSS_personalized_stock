import unittest
import news.random_picker as rp

class TestRandomPicker(unittest.TestCase):

    def setUp(self):
        # 다양한 케이스를 테스트하기 위한 샘플 뉴스 데이터
        self.sample_news = [
            {"title": "News 1", "sector": "IT"},
            {"title": "News 2", "sector": "IT"},
            {"title": "News 3", "sector": "금융"},
            {"title": "News 4", "sector": "헬스케어"},
            {"title": "News 5"}  # sector 키가 없음 -> '기타'로 분류됨
        ]

    def test_pick_random_news_normal(self):
        """전체 뉴스 풀에서 요청한 n개(3개)만큼 정확히 뽑아내는지 테스트"""
        result = rp.pick_random_news(self.sample_news, n=3)
        self.assertEqual(len(result), 3)

    def test_pick_random_news_exceed_limit(self):
        """요청한 n(10개)이 전체 뉴스 개수(5개)보다 많을 때, 뻗지 않고 5개만 반환하는지 테스트"""
        result = rp.pick_random_news(self.sample_news, n=10)
        self.assertEqual(len(result), 5) 

    def test_pick_random_news_empty(self):
        """빈 리스트가 주어졌을 때 에러 없이 빈 리스트를 반환하는지 테스트"""
        result = rp.pick_random_news([], n=5)
        self.assertEqual(result, [])

    def test_pick_random_news_missing_sector(self):
        """'sector' 키가 없는 뉴스가 에러 없이 잘 처리되는지 테스트"""
        missing_sector_news = [{"title": "No Sector News"}]
        result = rp.pick_random_news(missing_sector_news, n=1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "No Sector News")
        
    def test_exhausted_sector_removal(self):
        """특정 섹터의 뉴스를 다 뽑았을 때 발생하는 else 블록(sectors.remove) 커버리지 달성"""
        # 동일한 섹터의 뉴스만 2개 넣고 5개를 뽑으라고 지시
        # 뽑다 보면 IT 섹터가 고갈되어 else 블록으로 진입함
        same_sector_news = [
            {"title": "N1", "sector": "IT"},
            {"title": "N2", "sector": "IT"}
        ]
        result = rp.pick_random_news(same_sector_news, n=5)
        self.assertEqual(len(result), 2)

if __name__ == '__main__':
    unittest.main()

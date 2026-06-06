import unittest
from unittest.mock import patch, MagicMock
from data.news_fetcher import classify_sector, fetch_all_sector_news

class TestNewsFetcher(unittest.TestCase):

    def test_classify_sector(self):
        """1. 제목에 키워드가 있을 때 섹터 분류가 정확히 되는지 테스트"""
        # 정상 분류 케이스
        self.assertEqual(classify_sector("삼성전자, AI 반도체 혁신"), "IT")
        self.assertEqual(classify_sector("카카오와 NAVER의 미래"), "커뮤니케이션")
        
        # 키워드가 겹칠 때 점수가 가장 높은 섹터로 가는지 테스트 (IT키워드 2개, 통신키워드 1개)
        self.assertEqual(classify_sector("SK텔레콤, 삼성전자와 AI 반도체 협력"), "IT")
        
        # 매칭되는 키워드가 없을 때 '기타'로 빠지는지 테스트
        self.assertEqual(classify_sector("오늘의 날씨는 맑음"), "기타")

    @patch('data.news_fetcher.requests.get')
    def test_fetch_all_sector_news_success(self, mock_get):
        """2. 네이버 뉴스 API가 정상 응답했을 때 중복 제거 및 데이터 정제 테스트"""
        
        # 가짜 네이버 API 응답(Mock) 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"title": "<b>삼성전자</b> 역대급 실적 &quot;대박&quot;", "link": "http://test.com/1"},
                {"title": "중복된 기사입니다", "link": "http://test.com/1"}, # link가 같으므로 걸러져야 함
                {"title": "현대차 자율주행 테스트", "link": "http://test.com/2"}
            ]
        }
        mock_get.return_value = mock_response

        # 함수 실행 (디스플레이 개수는 2개로 제한)
        result = fetch_all_sector_news(display_per_keyword=2)

        # 검증 로직
        self.assertTrue(len(result) > 0) # 결과가 비어있지 않아야 함
        
        # 첫 번째 항목 검증 (HTML 태그 제거 및 특수문자 변환, 섹터 분류 확인)
        first_item = [item for item in result if item['url'] == 'http://test.com/1'][0]
        self.assertEqual(first_item['title'], '삼성전자 역대급 실적 "대박"')
        self.assertEqual(first_item['sector'], 'IT')
        
        # 중복 제거 검증: 반환된 리스트에 http://test.com/1 을 가진 딕셔너리가 딱 1개여야 함
        urls = [item['url'] for item in result]
        self.assertEqual(urls.count('http://test.com/1'), 1)

    @patch('data.news_fetcher.requests.get')
    def test_fetch_all_sector_news_exception(self, mock_get):
        """3. API 통신 중 에러가 발생했을 때 프로그램이 죽지 않고 넘어가는지 테스트"""
        
        # 강제로 예외(Exception) 발생
        mock_get.side_effect = Exception("네이버 서버 연결 실패")
        
        # 에러가 나도 빈 리스트([])를 반환하며 우아하게 종료되어야 함
        result = fetch_all_sector_news(display_per_keyword=1)
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()

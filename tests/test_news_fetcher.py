import unittest
from unittest.mock import patch, MagicMock
from data.news_fetcher import classify_sector, fetch_all_sector_news

class TestNewsFetcher(unittest.TestCase):

    def test_classify_sector_with_valid_keyword(self):
        """기사 제목에 키워드가 포함되어 있을 때 정확한 섹터로 분류하는지 테스트"""
        title = "삼성전자, 새로운 AI 반도체 칩 출시 발표"
        # '삼성전자', 'AI', '반도체'가 포함되어 있으므로 IT 점수가 가장 높아야 함
        sector = classify_sector(title)
        self.assertEqual(sector, "IT")

    def test_classify_sector_with_no_match(self):
        """매칭되는 키워드가 전혀 없을 때 '기타'를 반환하는지 테스트"""
        title = "오늘 날씨는 맑음, 주말 나들이 가기 좋은 날"
        sector = classify_sector(title)
        self.assertEqual(sector, "기타")

    @patch('data.news_fetcher.requests.get')
    @patch('data.news_fetcher.time.sleep')  # 테스트 속도를 위해 time.sleep도 모킹하여 대기 시간을 없앱니다.
    def test_fetch_all_sector_news_success(self, mock_sleep, mock_get):
        """네이버 API가 정상적인 데이터를 반환할 때 중복 제거 및 데이터 파싱이 잘 되는지 테스트"""
        
        # 1. 네이버 뉴스 API가 반환할 가짜(Mock) 응답 데이터 정의
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "title": "<b>카카오</b>, 신규 서비스 출시&quot;",
                    "link": "https://news.naver.com/1"
                },
                {
                    "title": "삼성전자 주가 상승세",
                    "link": "https://news.naver.com/2"
                }
            ]
        }
        mock_get.return_value = mock_response

        # 2. 함수 호출 (디스플레이 개수를 1개로 제한하여 테스트 속도 확보)
        results = fetch_all_sector_news(display_per_keyword=1)

        # 3. 결과 검증
        self.assertTrue(len(results) > 0)
        
        # HTML 태그 제거 및 따옴표 치환이 잘 되었는지 확인
        first_news = results[0]
        self.assertEqual(first_news["title"], '카카오, 신규 서비스 출시"')
        self.assertEqual(first_news["sector"], "커뮤니케이션")
        self.assertEqual(first_news["url"], "https://news.naver.com/1")

        # requests.get이 최소 한 번 이상 호출되었는지 확인
        mock_get.assert_called()

    @patch('data.news_fetcher.requests.get')
    @patch('data.news_fetcher.time.sleep')
    def test_fetch_all_sector_news_duplicate_removal(self, mock_sleep, mock_get):
        """동일한 링크(URL)를 가진 기사가 올 때 중복 제거가 정상 작동하는지 테스트"""
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        # 모든 키워드 검색 결과에 똑같은 링크가 반환된다고 설정
        mock_response.json.return_value = {
            "items": [
                {
                    "title": "중복 기사 제목",
                    "link": "https://news.naver.com/duplicate"
                }
            ]
        }
        mock_get.return_value = mock_response

        results = fetch_all_sector_news(display_per_keyword=1)

        # 수많은 키워드를 돌았지만, 링크가 모두 같으므로 전체 결과 리스트에는 딱 1개만 들어있어야 함
        self.assertEqual(len(results), 1)

    @patch('data.news_fetcher.requests.get')
    @patch('data.news_fetcher.time.sleep')
    def test_fetch_all_sector_news_api_failure(self, mock_sleep, mock_get):
        """API 서버가 200이 아닌 에러 코드를 반환하거나 예외(Exception)가 발생했을 때 프로그램이 죽지 않고 빈 배열을 반환하는지 테스트"""
        
        # requests.get 호출 시 예외 강제 발생 설정
        mock_get.side_effect = Exception("네트워크 연결 끊김 예외 발생")

        # 예외가 내부에서 catch되므로 함수가 에러를 던지지 않고 무사히 종료되어야 함
        results = fetch_all_sector_news(display_per_keyword=1)
        
        # 수집된 기사가 없으므로 빈 리스트 반환 확인
        self.assertEqual(results, [])

if __name__ == "__main__":
    unittest.main()

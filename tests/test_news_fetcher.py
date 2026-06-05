import unittest
from unittest.mock import patch, MagicMock

# 테스트할 원본 모듈 임포트
from news.fetcher import fetch_all_news

class TestNewsFetcher(unittest.TestCase):
    
    # 1. 테스트용 가짜(Mock) RSS 데이터 (구글 뉴스 응답과 동일한 형태)
    MOCK_RSS_DATA = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <item>
                <title>삼성전자 10만전자 돌파 기대감 - 뉴스A</title>
                <link>http://test.com/news1</link>
                <pubDate>Thu, 04 Jun 2026 12:00:00 GMT</pubDate>
            </item>
            <item>
                <title>한국은행 기준금리 동결 결정 - 뉴스B</title>
                <link>http://test.com/news2</link>
                <pubDate>Thu, 04 Jun 2026 13:00:00 GMT</pubDate>
            </item>
        </channel>
    </rss>
    """

    # urllib.request.urlopen 함수가 가짜 응답 객체를 반환하도록 가로채기(patch)
    @patch('urllib.request.urlopen')
    def test_fetch_all_news_success(self, mock_urlopen):
        """인터넷 통신이 성공했을 때 정상적으로 뉴스를 파싱하는지 테스트"""
        # 가짜 응답(Response) 객체 만들기
        mock_response = MagicMock()
        # .read()를 호출하면 우리의 가짜 RSS 데이터를 byte 형태로 반환하게 설정
        mock_response.read.return_value = self.MOCK_RSS_DATA.encode('utf-8')
        mock_urlopen.return_value = mock_response

        # 실제 함수 실행! (인터넷으로 나가지 않고 위의 Mock 데이터를 물고 돌아옴)
        result = fetch_all_news()

        # [검증 시작]
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)  # 가짜 데이터에 뉴스를 2개 넣었으므로
        
        # 첫 번째 뉴스 검증
        first_news = result[0]
        self.assertEqual(first_news['title'], "삼성전자 10만전자 돌파 기대감 - 뉴스A")
        self.assertEqual(first_news['description'], "삼성전자 10만전자 돌파 기대감 - 뉴스A")
        self.assertEqual(first_news['link'], "http://test.com/news1")
        self.assertEqual(first_news['pubDate'], "Thu, 04 Jun 2026 12:00:00 GMT")

    @patch('urllib.request.urlopen')
    def test_fetch_all_news_network_error(self, mock_urlopen):
        """인터넷 통신 중 에러(Exception)가 발생했을 때 예외 처리를 잘 하는지 테스트"""
        # urlopen을 호출하면 무조건 강제로 에러를 발생시키도록 설정
        mock_urlopen.side_effect = Exception("강제 네트워크 끊김 에러")

        # 실제 함수 실행! (에러가 발생해도 프로그램이 뻗지 않고 빈 리스트를 반환해야 함)
        result = fetch_all_news()

        # [검증 시작]
        self.assertEqual(result, [])  # 에러 시 빈 리스트를 반환하도록 코딩하셨으므로 통과!

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from news.fetcher import fetch_all_news

class TestNewsFetcherRSS(unittest.TestCase):

    @patch('news.fetcher.urllib.request.urlopen')
    def test_fetch_all_news_success(self, mock_urlopen):
        """1. 구글 뉴스 RSS가 정상적으로 XML 데이터를 반환했을 때 파싱 테스트"""
        
        # 💡 [수정된 부분] b"""...""" 대신 일반 문자열로 작성 후 .encode('utf-8') 적용
        mock_xml_data = """<?xml version="1.0" encoding="UTF-8"?>
        <rss>
            <channel>
                <item>
                    <title>구글 주식 대박 소식</title>
                    <link>http://test.com/news1</link>
                    <pubDate>Thu, 16 Apr 2026 10:00:00 GMT</pubDate>
                </item>
                <item>
                    <title>경제 금리 인상 발표</title>
                    <link>http://test.com/news2</link>
                    <pubDate>Thu, 16 Apr 2026 11:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>
        """.encode('utf-8')  # <--- 이렇게 인코딩을 따로 해줍니다!
        
        # urllib의 응답 객체 모킹 (read() 호출 시 가짜 XML 반환)
        mock_response = MagicMock()
        mock_response.read.return_value = mock_xml_data
        
        # with 문(컨텍스트 매니저)을 사용할 수 있도록 __enter__ 반환값 설정
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # 함수 실행
        result = fetch_all_news()

        # 검증 로직
        self.assertEqual(len(result), 2)
        
        # 첫 번째 기사 검증
        self.assertEqual(result[0]['title'], '구글 주식 대박 소식')
        self.assertEqual(result[0]['description'], '구글 주식 대박 소식') 
        self.assertEqual(result[0]['link'], 'http://test.com/news1')

    @patch('news.fetcher.urllib.request.urlopen')
    def test_fetch_all_news_exception(self, mock_urlopen):
        """2. 네트워크 통신 오류나 HTTP 403 등 예외 발생 시 빈 리스트 반환 테스트"""
        mock_urlopen.side_effect = Exception("HTTP Error 403: Forbidden")
        result = fetch_all_news()
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()

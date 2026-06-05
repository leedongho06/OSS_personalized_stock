import unittest
from unittest.mock import patch, MagicMock
# 현재 디렉토리 구조상 import가 안 될 경우를 대비해 경로 추가
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from news.fetcher import fetch_all_news

class TestNewsFetcher(unittest.TestCase):

    @patch('urllib.request.urlopen')
    def test_fetch_all_news_success(self, mock_urlopen):
        """뉴스 수집 성공 시 데이터를 올바르게 파싱하는지 테스트"""
        
        # 1. 일반 문자열로 작성한 뒤 .encode('utf-8')로 바이트 변환 (에러 방지)
        mock_xml = """<rss><channel>
            <item>
                <title>삼성전자 급등</title>
                <link>http://news.com/1</link>
                <pubDate>Mon, 01 Jan 2026 00:00:00 GMT</pubDate>
            </item>
        </channel></rss>""".encode('utf-8')
        
        # 2. Mocking 설정
        mock_response = MagicMock()
        mock_response.read.return_value = mock_xml
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # 3. 함수 실행
        results = fetch_all_news()

        # 4. 검증
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "삼성전자 급등")
        self.assertEqual(results[0]['link'], "http://news.com/1")

    @patch('urllib.request.urlopen')
    def test_fetch_all_news_failure(self, mock_urlopen):
        """네트워크 에러 발생 시 예외 처리가 잘 되는지 테스트"""
        
        # 1. 에러가 발생하도록 강제 설정
        mock_urlopen.side_effect = Exception("Network Connection Error")

        # 2. 함수 실행
        results = fetch_all_news()

        # 3. 검증 (빈 리스트 반환 확인)
        self.assertEqual(results, [])

if __name__ == "__main__":
    unittest.main()

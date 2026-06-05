import pytest
from unittest.mock import patch, MagicMock
from news.fetcher import fetch_all_news

# 테스트용 가짜 XML 데이터
MOCK_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <item>
            <title>삼성전자 주가 상승</title>
            <link>http://news.com/1</link>
            <pubDate>Fri, 05 Jun 2026 10:00:00 GMT</pubDate>
        </item>
    </channel>
</rss>
"""

@patch("urllib.request.urlopen")
def test_fetch_all_news_success(mock_urlopen):
    """정상적으로 뉴스 데이터를 수집할 때"""
    # 1. 가짜 응답 설정
    mock_response = MagicMock()
    mock_response.read.return_value = MOCK_XML.encode("utf-8")
    mock_urlopen.return_value = mock_response
    
    # 2. 함수 실행
    results = fetch_all_news()
    
    # 3. 검증
    assert len(results) == 1
    assert results[0]["title"] == "삼성전자 주가 상승"
    assert results[0]["link"] == "http://news.com/1"

@patch("urllib.request.urlopen")
def test_fetch_all_news_exception(mock_urlopen):
    """네트워크 에러 등으로 수집 실패 시 빈 리스트 반환"""
    # 1. 에러 발생 설정
    mock_urlopen.side_effect = Exception("네트워크 장애")
    
    # 2. 함수 실행
    results = fetch_all_news()
    
    # 3. 검증
    assert results == []

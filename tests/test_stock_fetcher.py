import pytest
import pandas as pd
from unittest.mock import patch
from data.stock_fetcher import get_kospi_top100

@patch("data.stock_fetcher.stock.get_market_cap_by_ticker")
@patch("data.stock_fetcher.stock.get_market_ticker_name")
def test_get_kospi_top100_success(mock_name, mock_cap):
    """정상적인 상황에서 상위 100개 종목이 필터링되어 잘 나오는지 테스트"""
    
    # 1. 가짜 시장 데이터 생성
    # 105개의 종목 생성 (ETF 5개 포함하여 필터링 로직 검증)
    tickers = [f"{i:06d}" for i in range(100000, 100105)]
    data = {
        "시가총액": range(105, 0, -1), "티커": tickers
    }
    mock_cap.return_value = pd.DataFrame(data, index=tickers)
    
    # 2. 가짜 종목명 설정
    def name_side_effect(ticker):
        if "000005" in ticker: return "KODEX ETF" # 필터링될 이름
        return "일반기업"
    mock_name.side_effect = name_side_effect
    
    # 3. 함수 실행
    result = get_kospi_top100()
    
    # 4. 검증
    assert len(result) <= 100 # 최대 100개 제한
    assert "ticker" in result.columns
    assert "name" in result.columns
    # 'KODEX ETF'는 필터링되어 없어야 함
    assert not any(result["name"].str.contains("KODEX"))

@patch("data.stock_fetcher.stock.get_market_cap_by_ticker")
def test_get_kospi_top100_empty(mock_cap):
    """API에서 데이터가 안 넘어왔을 때(빈 데이터프레임) 처리 테스트"""
    mock_cap.return_value = pd.DataFrame(columns=["티커", "시가총액"])
    
    result = get_kospi_top100()
    assert result.empty

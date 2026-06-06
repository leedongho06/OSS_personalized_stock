import pytest
import pandas as pd
import os
from unittest.mock import patch
import data.build_stocks as bs

# ==============================================================================
# 1. get_recent_business_day() 함수 테스트
# ==============================================================================

@patch("data.build_stocks.stock.get_market_ohlcv_by_date")
def test_get_recent_business_day_found(mock_ohlcv):
    """정상적으로 최근 영업일을 찾았을 때"""
    mock_ohlcv.return_value = pd.DataFrame({"종가": [80000]})
    date = bs.get_recent_business_day()
    assert date is not None
    assert len(date) == 8

@patch("data.build_stocks.stock.get_market_ohlcv_by_date")
def test_get_recent_business_day_not_found(mock_ohlcv):
    """영업일 데이터를 못 찾았을 때 Fallback 날짜 반환"""
    mock_ohlcv.return_value = pd.DataFrame()
    date = bs.get_recent_business_day()
    assert date is not None
    assert len(date) == 8

# ==============================================================================
# 2. build_stocks_csv() 파이프라인 통합 테스트 (커버리지 100%용)
# ==============================================================================

TEST_TICKERS = [
    ("000001", "PER_None", "IT"),      
    ("000002", "PER_Low", "금융"),      
    ("000003", "PER_Mid", "산업재"),    
    ("000004", "PER_High", "헬스케어")  
]

@patch("data.build_stocks.TOP100_TICKERS", TEST_TICKERS)
@patch("data.build_stocks.stock.get_market_fundamental_by_date")
@patch("data.build_stocks.stock.get_market_ohlcv_by_date")
@patch("data.build_stocks.time.sleep") 
@patch("pandas.DataFrame.to_csv")      
def test_build_stocks_csv_success(mock_to_csv, mock_sleep, mock_ohlcv, mock_fund):
    """정상 케이스: 모든 변동성 로직 커버"""
    def fund_side_effect(start, end, ticker):
        if ticker == "000001": return pd.DataFrame() 
        if ticker == "000002": return pd.DataFrame({"PER": [10.0], "PBR": [1.0]})
        if ticker == "000003": return pd.DataFrame({"PER": [20.0], "PBR": [1.5]})
        if ticker == "000004": return pd.DataFrame({"PER": [30.0], "PBR": [2.0]})
    mock_fund.side_effect = fund_side_effect
    
    mock_ohlcv.return_value = pd.DataFrame({"종가": [50000, 51000], "거래량": [1000, 2000]})
    
    bs.build_stocks_csv()
    
    assert mock_sleep.call_count == 4
    assert mock_to_csv.call_count == 1

@patch("data.build_stocks.TOP100_TICKERS", [("000001", "에러주식", "IT")])
@patch("data.build_stocks.stock.get_market_fundamental_by_date")
@patch("data.build_stocks.stock.get_market_ohlcv_by_date")
@patch("data.build_stocks.time.sleep")
@patch("pandas.DataFrame.to_csv")
def test_build_stocks_csv_fundamental_exception(mock_to_csv, mock_sleep, mock_ohlcv, mock_fund):
    """Fundamental API 에러 시 except 블록(167-168) 커버"""
    mock_fund.side_effect = Exception("API 장애")
    mock_ohlcv.return_value = pd.DataFrame({"종가": [1000], "거래량": [100]})
    
    bs.build_stocks_csv()
    assert mock_to_csv.called

# 💡 기존의 test_build_stocks_csv_ohlcv_exception 함수를 이 코드로 교체하세요!

@patch("data.build_stocks.get_recent_business_day", return_value="20260501") 
@patch("data.build_stocks.TOP100_TICKERS", [("000001", "에러주식", "IT")])
@patch("data.build_stocks.stock.get_market_fundamental_by_date")
@patch("data.build_stocks.stock.get_market_ohlcv_by_date")
@patch("data.build_stocks.time.sleep")
@patch("pandas.DataFrame.to_csv")
def test_build_stocks_csv_ohlcv_exception(mock_to_csv, mock_sleep, mock_ohlcv, mock_fund, mock_date):
    """OHLCV 에러 처리(178번 줄) 완벽 커버를 위한 데이터 변조 트릭"""
    # Fundamental은 정상 통과
    mock_fund.return_value = pd.DataFrame({"PER": [10.0], "PBR": [1.0]})
    
    # 💥 필살기: "종가" 컬럼을 없애버려서 판다스 내부에서 자연스럽게 KeyError 발생 유도!
    # 이렇게 하면 178번 줄(except)로 무조건 떨어집니다.
    mock_ohlcv.return_value = pd.DataFrame({"이상한컬럼명": [1000], "거래량": [100]})
    
    bs.build_stocks_csv()
    
    # 튕기지 않고 CSV 저장까지 무사히 도착하는지 확인
    assert mock_to_csv.called

@patch("data.build_stocks.TOP100_TICKERS", [])
@patch("pandas.DataFrame.to_csv")
def test_build_stocks_csv_empty_data(mock_to_csv):
    """데이터가 아예 없을 때 방어 로직 커버"""
    bs.build_stocks_csv()
    mock_to_csv.assert_not_called()

@patch("os.path.exists", return_value=False)
@patch("os.makedirs")
@patch("data.build_stocks.TOP100_TICKERS", [("000001", "테스트", "IT")])
@patch("data.build_stocks.stock.get_market_fundamental_by_date", return_value=pd.DataFrame({"PER": [10.0], "PBR": [1.0]}))
@patch("data.build_stocks.stock.get_market_ohlcv_by_date", return_value=pd.DataFrame({"종가": [50000], "거래량": [1000]}))
@patch("data.build_stocks.time.sleep")
@patch("pandas.DataFrame.to_csv")
def test_build_stocks_csv_makedirs(mock_to_csv, mock_sleep, mock_ohlcv, mock_fund, mock_makedirs, mock_exists):
    """폴더 생성 분기 테스트"""
    bs.build_stocks_csv()
    mock_makedirs.assert_called_once()

    # 💡 178번 줄(else 블록)의 진짜 원인을 타격하는 최종 저격수!
@patch("data.build_stocks.get_recent_business_day", return_value="20260501")
@patch("data.build_stocks.TOP100_TICKERS", [("000001", "빈주식", "IT")])
@patch("data.build_stocks.stock.get_market_fundamental_by_date")
@patch("data.build_stocks.stock.get_market_ohlcv_by_date")
@patch("data.build_stocks.time.sleep")
@patch("pandas.DataFrame.to_csv")
def test_build_stocks_csv_ohlcv_empty_else_block(mock_to_csv, mock_sleep, mock_ohlcv, mock_fund, mock_date):
    """ohlcv API가 에러 없이 '빈 데이터'를 반환할 때의 else 블록(178번 줄) 커버"""

    # Fundamental은 정상 데이터를 반환하게 둠
    mock_fund.return_value = pd.DataFrame({"PER": [10.0], "PBR": [1.0]})

    # 💥 핵심: 에러(Exception)가 아니라 '빈 데이터프레임'을 던져서 else 블록으로 진입시킴!
    mock_ohlcv.return_value = pd.DataFrame()

    bs.build_stocks_csv()

    # 튕기지 않고 무사히 CSV 저장까지 도착하는지 확인
    assert mock_to_csv.called

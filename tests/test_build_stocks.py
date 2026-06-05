import pytest
import pandas as pd
from unittest.mock import patch
from datetime import datetime
import data.build_stocks as bs

# ==============================================================================
# 1. get_recent_business_day() 함수 테스트
# ==============================================================================

@patch("data.build_stocks.stock.get_market_ohlcv_by_date")
def test_get_recent_business_day_found(mock_ohlcv):
    """정상적으로 최근 영업일을 찾았을 때"""
    # API가 비어있지 않은 정상적인 데이터프레임을 반환한다고 가정
    mock_ohlcv.return_value = pd.DataFrame({"종가": [80000]})
    
    date = bs.get_recent_business_day()
    assert date is not None
    assert len(date) == 8  # "YYYYMMDD" 형식인지 확인

@patch("data.build_stocks.stock.get_market_ohlcv_by_date")
def test_get_recent_business_day_not_found(mock_ohlcv):
    """9일 내내 휴장일(명절 등)이라 데이터를 못 찾았을 때 7일 전 날짜를 반환하는지 (Fallback)"""
    # API가 계속 빈 데이터프레임을 반환한다고 가정
    mock_ohlcv.return_value = pd.DataFrame()
    
    date = bs.get_recent_business_day()
    assert date is not None
    assert len(date) == 8

# ==============================================================================
# 2. build_stocks_csv() 파이프라인 통합 테스트
# ==============================================================================

# 테스트 속도를 위해 100개 종목 대신 '변동성(고, 중, 저, 결측치)'을 모두 확인할 수 있는 4개로 축소
TEST_TICKERS = [
    ("000001", "PER_None", "IT"),      # PER 정보 없음 -> 변동성 '중'
    ("000002", "PER_Low", "금융"),      # PER 10 (< 15) -> 변동성 '저'
    ("000003", "PER_Mid", "산업재"),    # PER 20 (15~25) -> 변동성 '중'
    ("000004", "PER_High", "헬스케어")  # PER 30 (> 25) -> 변동성 '고'
]

@patch("data.build_stocks.TOP100_TICKERS", TEST_TICKERS)
@patch("data.build_stocks.stock.get_market_fundamental_by_date")
@patch("data.build_stocks.stock.get_market_ohlcv_by_date")
@patch("data.build_stocks.time.sleep") # 0.2초 대기 무력화
@patch("pandas.DataFrame.to_csv")      # 실제 csv 파일 생성 방지
def test_build_stocks_csv_success(mock_to_csv, mock_sleep, mock_ohlcv, mock_fund):
    """정상적인 상황에서 모든 변동성(저,중,고) 로직을 통과하고 CSV를 저장하는지 테스트"""
    
    # 각 주식(티커)마다 다른 PER 값을 반환하도록 가짜 함수 설정
    def fund_side_effect(start, end, ticker):
        if ticker == "000001": return pd.DataFrame() # 데이터 없음
        if ticker == "000002": return pd.DataFrame({"PER": [10.0], "PBR": [1.0]})
        if ticker == "000003": return pd.DataFrame({"PER": [20.0], "PBR": [1.5]})
        if ticker == "000004": return pd.DataFrame({"PER": [30.0], "PBR": [2.0]})
    mock_fund.side_effect = fund_side_effect
    
    # 이동평균 및 거래량 가짜 데이터
    mock_ohlcv.return_value = pd.DataFrame({"종가": [50000, 51000], "거래량": [1000, 2000]})
    
    bs.build_stocks_csv()
    
    # 검증: 4개 종목을 돌았으므로 sleep이 4번 호출되어야 하고, csv 저장도 1번 실행되어야 함
    assert mock_sleep.call_count == 4
    assert mock_to_csv.call_count == 1


@patch("data.build_stocks.TOP100_TICKERS", [("000001", "에러주식", "IT")])
@patch("data.build_stocks.get_recent_business_day", return_value="20260501") # 날짜 함수 우회 패치
@patch("data.build_stocks.stock.get_market_fundamental_by_date", side_effect=Exception("API 접속 장애"))
@patch("data.build_stocks.stock.get_market_ohlcv_by_date", side_effect=Exception("API 접속 장애"))
@patch("data.build_stocks.time.sleep")
@patch("pandas.DataFrame.to_csv")
def test_build_stocks_csv_exceptions(mock_to_csv, mock_sleep, mock_ohlcv, mock_fund, mock_date):
    """API 장애로 인해 Exception이 발생해도 프로그램이 뻗지 않고 except 블록을 타서 정상 종료되는지 테스트"""
    # Exception이 발생하면 내부 로직에 의해 값들이 None으로 처리되고,
    # pandas 결측치(fillna) 처리 후 무사히 CSV가 저장되어야 함
    bs.build_stocks_csv()
    
    # 에러가 나도 프로그램이 멈추지 않고 끝까지 도달했는지 확인
    assert mock_to_csv.call_count == 1

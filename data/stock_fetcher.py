from pykrx import stock
import pandas as pd
from datetime import datetime, timedelta


def get_kospi_top100() -> pd.DataFrame:
    """코스피 시가총액 상위 100개 종목 가져오기 (ETF 제외)."""

    today = datetime.today().strftime("%Y%m%d")
    yesterday = (datetime.today() - timedelta(days=3)).strftime("%Y%m%d")

    # 코스피 전체 종목 시가총액 순위
    df = stock.get_market_cap_by_ticker(yesterday, market="KOSPI")
    df = df.sort_values("시가총액", ascending=False)
    df = df.reset_index()
    df.rename(columns={"티커": "ticker"}, inplace=True)

    # ETF 제외 (티커 6자리 숫자만)
    df = df[df["ticker"].str.match(r"^\d{6}$")]

    # 종목명 추가
    df["name"] = df["ticker"].apply(
        lambda x: stock.get_market_ticker_name(x)
    )

    # ETF 키워드 제외
    etf_keywords = ["ETF", "KODEX", "TIGER", "KINDEX",
                    "ARIRANG", "KOSEF", "ACE", "HANARO"]
    for kw in etf_keywords:
        df = df[~df["name"].str.contains(kw, na=False)]

    return df.head(100)[["ticker", "name"]].reset_index(drop=True)

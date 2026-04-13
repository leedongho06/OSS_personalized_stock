CREATE TABLE IF NOT EXISTS stocks (
    ticker TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    sector TEXT
);

-- 일별 주가 및 재무 지표 테이블
CREATE TABLE IF NOT EXISTS daily_data (
    ticker TEXT,
    date TEXT,
    close_price REAL,
    per REAL,
    pbr REAL,
    roe REAL,
    dividend_yield REAL,
    PRIMARY KEY (ticker, date),
    FOREIGN KEY (ticker) REFERENCES stocks (ticker)
);

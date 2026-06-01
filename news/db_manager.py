import sqlite3
import os
from datetime import datetime

DB_PATH = "data/stock_data.db"


def init_news_table():
    """뉴스 테이블 생성."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            sector TEXT,
            link TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_news(news_list: list):
    """뉴스 리스트 DB 저장 (중복 제외)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    saved = 0
    for news in news_list:
        cursor.execute(
            "SELECT id FROM news WHERE title = ?",
            (news.get("title", ""),)
        )
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO news (title, description, sector, link, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                news.get("title", ""),
                news.get("description", ""),
                news.get("sector", "기타"),
                news.get("link", ""),
                now
            ))
            saved += 1

    conn.commit()
    conn.close()
    print(f"뉴스 저장 완료: {saved}개")


def load_news(limit: int = 100) -> list:
    """DB에서 최신 뉴스 로드."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, description, sector, link
        FROM news
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "title": row[0],
            "description": row[1],
            "sector": row[2],
            "link": row[3],
        }
        for row in rows
    ]


def get_news_count() -> int:
    """DB에 저장된 뉴스 수 반환."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM news")
        count = cursor.fetchone()[0]
    except Exception:
        count = 0
    conn.close()
    return count


def init_trade_table():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            trade_type TEXT,
            price REAL,
            buy_price REAL,
            sell_price REAL,
            profit_rate REAL,
            rating INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_trade(name: str, trade_type: str, price: float,
               buy_price: float = None, sell_price: float = None,
               rating: int = 0):
    """매매일지 저장."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    profit_rate = None
    if buy_price and sell_price and buy_price > 0:
        profit_rate = round(((sell_price - buy_price) / buy_price) * 100, 2)

    cursor.execute("""
        INSERT INTO trade_journal
        (name, trade_type, price, buy_price, sell_price, profit_rate, rating, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, trade_type, price, buy_price, sell_price, profit_rate, rating, now))

    conn.commit()
    conn.close()


def load_trades() -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, trade_type, price, buy_price, sell_price,
               profit_rate, rating, created_at
        FROM trade_journal
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "trade_type": row[2],
            "price": row[3],
            "buy_price": row[4],
            "sell_price": row[5],
            "profit_rate": row[6],
            "rating": row[7],
            "created_at": row[8],
        }
        for row in rows
    ]



def update_trade_rating(trade_id: int, rating: int):
    """매매일지 만족도 업데이트."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE trade_journal SET rating = ? WHERE id = ?
    """, (rating, trade_id))
    conn.commit()
    conn.close()

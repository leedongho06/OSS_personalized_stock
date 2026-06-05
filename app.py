import os
import sqlite3
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from pykrx import stock as pykrx_stock

# 기존 추천 및 Q-learning 모듈
from recommendation.scorer import infer_style
from recommendation.filter import filter_by_style
from recommendation.recommender import recommend
from q_learning.q_table import load_q_table
from q_learning.agent import choose_action
from q_learning.state_encoder import encode_state
from q_learning.train import train
from q_learning.reward import normalize_reward

# 뉴스 및 트레이딩 저널 모듈
from news.fetcher import fetch_all_news
from news.classifier import add_sector_to_news
from news.random_picker import pick_random_news
from news.interest_scorer import calculate_interest
from news.style_inferrer import infer_style_from_news
from news.db_manager import (
    init_news_table, save_news, load_news, get_news_count, 
    init_trade_table, save_trade, load_trades, update_trade_rating
)

# 💡 새롭게 추가된 DB 대시보드 모듈
from database.db_manager import get_recent_stocks_for_web

app = Flask(__name__)
app.secret_key = "oss_stock_secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "stock_data.db")


# ==========================================
# 💡 [핵심 추가] 동적 추천 도우미 함수 (고인물 방지)
# ==========================================
def get_dynamic_recommendation(style):
    """
    정적 CSV와 최신 DB 주가 데이터를 병합하여, 
    매일 변화하는 시장 상황에 맞춘 동적 추천 결과를 반환합니다.
    """
    df = pd.DataFrame()
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            # 테이블명 유연성 확보 (daily_prices 또는 daily_stock_data)
            try:
                db_df = pd.read_sql_query("SELECT * FROM daily_prices", conn)
            except:
                db_df = pd.read_sql_query("SELECT * FROM daily_stock_data", conn)
            
            # 컬럼명을 소문자로 통일하여 병합 에러 방지
            db_df.columns = [c.lower() for c in db_df.columns]
            conn.close()

            csv_stocks = pd.read_csv(os.path.join(BASE_DIR, "data", "stocks.csv"))
            
            if 'name' in csv_stocks.columns and 'sector' in csv_stocks.columns:
                meta_info = csv_stocks[['ticker', 'name', 'sector']].drop_duplicates()
                
                db_df['ticker'] = db_df['ticker'].astype(str).str.zfill(6)
                meta_info['ticker'] = meta_info['ticker'].astype(str).str.zfill(6)
                
                df = pd.merge(db_df, meta_info, on='ticker', how='inner')
                df = df.sort_values(by=['ticker', 'date']).reset_index(drop=True)
                
                # 20일 이동평균선(ma_20) 동적 생성
                if 'close' in df.columns:
                    df['ma_20'] = df.groupby('ticker')['close'].transform(lambda x: x.rolling(window=20, min_periods=1).mean())
            else:
                df = csv_stocks
        except Exception as e:
            print(f"DB 로드 실패 (CSV로 대체): {e}")
            df = pd.read_csv(os.path.join(BASE_DIR, "data", "stocks.csv"))
    else:
        df = pd.read_csv(os.path.join(BASE_DIR, "data", "stocks.csv"))

    # 최신 날짜 데이터로 압축
    if not df.empty and 'date' in df.columns:
        df_latest = df.sort_values('date').groupby('ticker').last().reset_index()
    else:
        df_latest = df

    # 성향 필터링 및 추천 진행
    filtered = filter_by_style(df_latest, style)
    if filtered.empty:
        filtered = df_latest

    result = recommend(filtered, style, top_n=5)
    
    # 점수 높은 순으로 내림차순 정렬
    if not result.empty and 'score' in result.columns:
        result = result.sort_values(by='score', ascending=False).head(5)
    elif not result.empty:
        result = result.head(5)

    return result


# ==========================================
# 라우트 (웹페이지 연결)
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/portfolio")
def portfolio():
    style = session.get("style", None)
    history = session.get("history", [])
    return render_template("portfolio.html", style=style, history=history)


# 💡 새롭게 추가된 데이터베이스 대시보드 라우트
@app.route("/dashboard")
def dashboard():
    try:
        # DB에서 최신 50개 데이터를 꺼내옵니다.
        stocks = get_recent_stocks_for_web(limit=50)
        return render_template("dashboard.html", stock_data=stocks)
    except Exception as e:
        print(f"대시보드 로딩 오류: {e}")
        return render_template("dashboard.html", stock_data=[])


@app.route("/recommend", methods=["POST"])
def recommend_by_company():
    companies = request.form.getlist("companies")
    companies = [c for c in companies if c.strip()]

    style, score, analyses = infer_style(companies)
    session["style"] = style

    # 💡 정적 CSV 대신 동적 추천 함수 사용
    result = get_dynamic_recommendation(style)
    sector = result.iloc[0]["sector"] if not result.empty else "IT"
    session["sector"] = sector

    q_table = load_q_table()
    state = encode_state(style, sector)
    action = choose_action(q_table, state)
    
    # 💡 Q-learning 탐험 로직 (무조건 0번만 추천하는 고인물 현상 방지)
    if action == 0 and random.random() < 0.4:
        final_idx = random.randint(1, len(result) - 1) if len(result) > 1 else 0
    else:
        final_idx = action % len(result) if len(result) > 0 else 0

    final = result.iloc[final_idx]["name"] if not result.empty else "추천 불가"
    session["final"] = final

    return render_template(
        "result.html",
        style=style,
        result=result.to_dict(orient="records"),
        final=final,
    )


@app.route("/recommend/direct", methods=["POST"])
def recommend_direct():
    style = request.form.get("style", "중립형")
    session["style"] = style
    session["sector"] = "IT"

    df = pd.read_csv("data/stocks.csv")
    filtered = filter_by_style(df, style)
    if filtered.empty:
        filtered = df

    result = recommend(filtered, style, top_n=5)
    sector = result.iloc[0]["sector"]
    session["sector"] = sector

    q_table = load_q_table()
    state = encode_state(style, sector)
    action = choose_action(q_table, state)
    final = result.iloc[action % len(result)]["name"]

    return render_template(
        "result.html",
        style=style,
        result=result.to_dict(orient="records"),
        final=final,
    )


@app.route("/news")
def news_page():
    init_news_table()
    if get_news_count() < 30:
        news = fetch_all_news()
        news = add_sector_to_news(news)
        save_news(news)
    else:
        news = load_news(limit=100)

    picked = pick_random_news(news, n=5)
    session["picked_news"] = picked
    return render_template("news.html", news=picked)


@app.route("/news/rate", methods=["POST"])
def rate_news():
    picked = session.get("picked_news", [])
    rated = []
    for i, n in enumerate(picked):
        rating = int(request.form.get(f"rating_{i}", 3))
        rated.append({"sector": n["sector"], "rating": rating})

    interest = calculate_interest(rated)
    style, score, analyses = infer_style_from_news(interest)
    session["style"] = style

    # 💡 정적 CSV 대신 동적 추천 함수 사용
    result = get_dynamic_recommendation(style)
    sector = result.iloc[0]["sector"] if not result.empty else "IT"
    session["sector"] = sector

    q_table = load_q_table()
    state = encode_state(style, sector)
    action = choose_action(q_table, state)
    
    # 💡 Q-learning 탐험 로직 추가
    if action == 0 and random.random() < 0.4:
        final_idx = random.randint(1, len(result) - 1) if len(result) > 1 else 0
    else:
        final_idx = action % len(result) if len(result) > 0 else 0

    final = result.iloc[final_idx]["name"] if not result.empty else "추천 불가"
    session["final"] = final

    return render_template(
        "result.html",
        style=style,
        result=result.to_dict(orient="records"),
        final=final,
    )


@app.route("/feedback", methods=["POST"])
def feedback():
    score = int(request.form.get("score", 3))
    style = session.get("style", "중립형")
    sector = session.get("sector", "IT")
    reward = normalize_reward(score)
    train(style, sector, reward)

    history = session.get("history", [])
    history.append({
        "name": session.get("final", ""),
        "sector": sector,
        "score": score,
    })
    session["history"] = history

    return redirect(url_for("portfolio"))


@app.route("/journal")
def journal():
    init_trade_table()
    trades = load_trades()

    chart_labels = []
    chart_data = []

    if trades:
        total = sum(t["price"] for t in trades if t["price"])
        name_totals = {}
        for t in trades:
            name_totals[t["name"]] = name_totals.get(t["name"], 0) + (t["price"] or 0)

        for name, amount in name_totals.items():
            chart_labels.append(name)
            chart_data.append(round((amount / total) * 100, 1) if total > 0 else 0)

    return render_template(
        "journal.html",
        trades=trades,
        chart_labels=chart_labels,
        chart_data=chart_data,
    )


@app.route("/journal/add", methods=["POST"])
def add_trade():
    name = request.form.get("name", "")
    trade_type = request.form.get("trade_type", "매수")
    price = float(request.form.get("price", 0))
    save_trade(name, trade_type, price)
    return redirect(url_for("journal"))


@app.route("/journal/rate", methods=["POST"])
def rate_trade():
    trade_id = int(request.form.get("trade_id", 0))
    rating = int(request.form.get("rating", 3))

    update_trade_rating(trade_id, rating)

    style = session.get("style", "중립형")
    sector = session.get("sector", "IT")
    reward = normalize_reward(rating)
    train(style, sector, reward)

    return redirect(url_for("journal"))


@app.route("/kospi")
def kospi_top10():
    try:
        base_date = None
        for i in range(1, 10):
            date = (datetime.today() - timedelta(days=i)).strftime("%Y%m%d")
            df = pykrx_stock.get_market_ohlcv_by_date(date, date, "005930")
            if not df.empty:
                base_date = date
                break

        if not base_date:
            return render_template("kospi.html", stocks=[], updated="-", base_date="-")

        stock_df = pd.read_csv("data/stocks.csv")
        tickers = list(zip(stock_df["ticker"].astype(str).str.zfill(6), stock_df["name"]))

        stocks = []
        for ticker, name in tickers:
            try:
                df = pykrx_stock.get_market_ohlcv_by_date(base_date, base_date, ticker)
                if not df.empty:
                    open_price = int(df["시가"].iloc[0])
                    close = int(df["종가"].iloc[0])
                    volume = int(df["거래량"].iloc[0])
                    marcap = close * volume
                    change = close - open_price
                    change_rate = round((change / open_price) * 100, 2) if open_price > 0 else 0.0

                    stocks.append({
                        "ticker": ticker,
                        "name": name,
                        "close": f"{close:,}",
                        "change": f"{change:+,}",
                        "change_rate": change_rate,
                        "is_up": change >= 0,
                        "marcap": marcap,
                    })
            except Exception:
                continue

        stocks = sorted(stocks, key=lambda x: x["marcap"], reverse=True)[:10]
        now = datetime.now().strftime("%H:%M:%S")
        
        return render_template(
            "kospi.html",
            stocks=stocks,
            updated=now,
            base_date=base_date
        )

    except Exception as e:
        print(f"오류: {e}")
        return render_template("kospi.html", stocks=[], updated="-", base_date="-")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=71671)

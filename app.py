from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from recommendation.scorer import infer_style
from recommendation.filter import filter_by_style
from recommendation.recommender import recommend
from q_learning.q_table import load_q_table
from q_learning.agent import choose_action
from q_learning.state_encoder import encode_state
from q_learning.train import train
from q_learning.reward import normalize_reward
from news.fetcher import fetch_all_news
from news.classifier import add_sector_to_news
from news.random_picker import pick_random_news
from news.interest_scorer import calculate_interest
from news.style_inferrer import infer_style_from_news
from news.db_manager import init_news_table, save_news, load_news, get_news_count, init_trade_table, save_trade, load_trades
from pykrx import stock as pykrx_stock
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = "oss_stock_secret"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/portfolio")
def portfolio():
    style = session.get("style", None)
    history = session.get("history", [])
    return render_template("portfolio.html", style=style, history=history)


@app.route("/recommend", methods=["POST"])
def recommend_by_company():
    companies = request.form.getlist("companies")
    companies = [c for c in companies if c.strip()]

    style, score, analyses = infer_style(companies)
    session["style"] = style

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
    session["final"] = final

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

    # 원형 그래프 데이터 계산
    chart_labels = []
    chart_data = []

    if trades:
        total = sum(t["buy_price"] for t in trades)
        name_totals = {}
        for t in trades:
            name_totals[t["name"]] = name_totals.get(t["name"], 0) + t["buy_price"]

        for name, amount in name_totals.items():
            chart_labels.append(name)
            chart_data.append(round((amount / total) * 100, 1))

    return render_template(
        "journal.html",
        trades=trades,
        chart_labels=chart_labels,
        chart_data=chart_data,
    )


@app.route("/journal/add", methods=["POST"])
def add_trade():
    name = request.form.get("name", "")
    buy_price = float(request.form.get("buy_price", 0))
    sell_price = float(request.form.get("sell_price", 0))

    # DB 저장
    save_trade(name, buy_price, sell_price, rating)

    # Q-learning 학습 반영
    style = session.get("style", "중립형")
    sector = session.get("sector", "IT")
    reward = normalize_reward(rating)
    train(style, sector, reward)

    # 포트폴리오 이력 업데이트
    history = session.get("history", [])
    history.append({
        "name": name,
        "sector": sector,
        "score": rating,
    })
    session["history"] = history

    return redirect(url_for("journal"))

@app.route("/journal/rate", methods=["POST"])
def rate_trade():
    trade_id = int(request.form.get("trade_id", 0))
    rating = int(request.form.get("rating", 3))

    # DB 업데이트
    update_trade_rating(trade_id, rating)

    # Q-learning 학습 반영
    style = session.get("style", "중립형")
    sector = session.get("sector", "IT")
    reward = normalize_reward(rating)
    train(style, sector, reward)

    return redirect(url_for("journal"))


@app.route("/kospi")
def kospi_top10():
    try:
        # 최근 영업일 찾기
        base_date = None
        for i in range(1, 10):
            date = (datetime.today() - timedelta(days=i)).strftime("%Y%m%d")
            df = pykrx_stock.get_market_ohlcv_by_date(date, date, "005930")
            if not df.empty:
                base_date = date
                break

        if not base_date:
            return render_template("kospi.html", stocks=[], updated="-", base_date="-")

        # stocks.csv에서 종목 목록 로드
        stock_df = pd.read_csv("data/stocks.csv")
        tickers = list(zip(stock_df["ticker"].astype(str).str.zfill(6),
                           stock_df["name"]))

        stocks = []
        for ticker, name in tickers:
            try:
                df = pykrx_stock.get_market_ohlcv_by_date(
                    base_date, base_date, ticker
                )
                if not df.empty:
                    open_price = int(df["시가"].iloc[0])
                    close = int(df["종가"].iloc[0])
                    volume = int(df["거래량"].iloc[0])
                    marcap = close * volume  # 시가총액 근사값
                    change = close - open_price
                    change_rate = round(
                        (change / open_price) * 100, 2
                    ) if open_price > 0 else 0.0

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

        # 시가총액 기준 상위 10개 정렬
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
    app.run(debug=True, host="0.0.0.0", port=5000)

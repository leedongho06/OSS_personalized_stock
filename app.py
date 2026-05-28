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
    return render_template("journal.html", trades=trades)


@app.route("/journal/add", methods=["POST"])
def add_trade():
    name = request.form.get("name", "")
    buy_price = float(request.form.get("buy_price", 0))
    sell_price = float(request.form.get("sell_price", 0))
    rating = int(request.form.get("rating", 3))

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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

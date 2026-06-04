from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import requests as req
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
from news.db_manager import init_news_table, save_news, load_news, get_news_count

app = Flask(__name__)
app.secret_key = "oss_stock_secret"
BACKEND_URL = "http://localhost:8080"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recommend", methods=["POST"])
def recommend_by_company():
    companies = request.form.getlist("companies")
    companies = [c for c in companies if c.strip()]

    style, score, analyses = infer_style(companies)
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

@app.route("/recommend/direct", methods=["POST"])
def recommend_direct():
    style = request.form.get("style", "중립형")
    session["style"] = style
    session["sector"] = "IT"

    df = pd.read.csv("data/stocks.csv")
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
    result=result.to_dict(orient="record"),
    final=final,
    )

@app.route("/feedback", methods=["POST"])
def feedback():
    score = int(request.form.get("score", 3))
    style = session.get("style", "중립형")
    sector = session.get("sector", "IT")
    reward = normalize_reward(score)
    train(style, sector, reward)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=71671)

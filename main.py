import pandas as pd
from recommendation.scorer import get_input_companies, infer_style, print_analysis
from recommendation.filter import filter_by_style
from recommendation.recommender import recommend
from q_learning.q_table import load_q_table
from q_learning.agent import choose_action
from q_learning.state_encoder import encode_state
from q_learning.train import train_with_feedback
from news.fetcher import fetch_all_news
from news.classifier import add_sector_to_news
from news.random_picker import pick_random_news
from news.interest_scorer import calculate_interest
from news.style_inferrer import infer_style_from_news


def get_input_method() -> str:
    print("\n[ 투자 성향 파악 방법 선택 ]")
    print("1. 관심 기업 직접 입력")
    print("2. 뉴스 관심도 평가")
    while True:
        choice = input("선택 (1 or 2): ").strip()
        if choice in {"1", "2"}:
            return choice
        print("1 또는 2를 입력해주세요.")


def main():
    print("\n=== OSS Personalized Stock ===\n")

    # 1. 입력 방식 선택
    method = get_input_method()

    if method == "1":
        # 기업 직접 입력
        companies = get_input_companies()
        style, score, analyses = infer_style(companies)
        print_analysis(style, score, analyses)

    else:
        # 뉴스 관심도 평가
        print("\n뉴스 데이터 수집 중...")
        news = fetch_all_news()
        news = add_sector_to_news(news)
        
        # [수정 완료] pick_balanced_news -> pick_random_news로 이름 통일
        picked = pick_random_news(news, n=5)

        print("\n[ 뉴스 관심도 평가 ]")
        print("각 뉴스에 별점을 매겨주세요 (1~5점)\n")

        rated = []
        for i, n in enumerate(picked):
            print(f"{i+1}. [{n['sector']}] {n['title']}")
            while True:
                raw = input("별점 (1~5): ").strip()
                if raw in {"1", "2", "3", "4", "5"}:
                    rated.append({
                        "sector": n["sector"],
                        "rating": int(raw)
                    })
                    break
                print("1~5 사이 숫자를 입력해주세요.")

        interest = calculate_interest(rated)
        style, score, analyses = infer_style_from_news(interest)
        print(f"\n추론된 투자 성향: {style} (점수: {score})\n")

    # 2. 데이터 로드
    df = pd.read_csv("data/stocks.csv")

    # 3. 필터링
    filtered = filter_by_style(df, style)
    if filtered.empty:
        print("조건에 맞는 종목이 없습니다.")
        return

    # 4. 코사인 유사도 추천
    result = recommend(filtered, style, top_n=5)
    print("[ 추천 종목 Top 5 ]")
    print(result.to_string(index=False))

    # 5. Q-learning action 선택
    sector = result.iloc[0]["sector"]
    state = encode_state(style, sector)
    q_table = load_q_table()
    action = choose_action(q_table, state)
    print(f"\nQ-learning 추천 인덱스: {action}")
    print(f"최종 추천 종목: {result.iloc[action % len(result)]['name']}\n")

    # 6. 피드백 받아 Q-learning 학습
    train_with_feedback(style, sector)


if __name__ == "__main__":
    main()

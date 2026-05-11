import pandas as pd
from recommendation.scorer import get_input_companies, infer_style, print_analysis
from recommendation.filter import filter_by_style
from recommendation.recommender import recommend
from q_learning.q_table import load_q_table
from q_learning.agent import choose_action
from q_learning.state_encoder import encode_state
from q_learning.train import train_with_feedback


def main():
    print("\n=== OSS Personalized Stock ===\n")

    # 1. 관심 기업 입력
    companies = get_input_companies()

    # 2. 성향 자동 추론
    style, score, analyses = infer_style(companies)
    print_analysis(style, score, analyses)

    # 3. 데이터 로드
    df = pd.read_csv("data/dummy.csv")

    # 4. 필터링
    filtered = filter_by_style(df, style)
    if filtered.empty:
        print("조건에 맞는 종목이 없습니다.")
        return

    # 5. 코사인 유사도 추천
    result = recommend(filtered, style, top_n=5)
    print("[ 추천 종목 Top 5 ]")
    print(result.to_string(index=False))

    # 6. Q-learning action 선택
    sector = result.iloc[0]["sector"]
    state = encode_state(style, sector)
    q_table = load_q_table()
    action = choose_action(q_table, state)
    print(f"\nQ-learning 추천 인덱스: {action}")
    print(f"최종 추천 종목: {result.iloc[action % len(result)]['name']}\n")

    # 7. 피드백 받아 Q-learning 학습
    train_with_feedback(style, sector)


if __name__ == "__main__":
    main()

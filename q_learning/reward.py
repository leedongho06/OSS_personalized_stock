def normalize_reward(score: int) -> float:

    """"
    사용자 피드백 1-5점을 보상 신호로 변환
    5 -> 1.0 / 3->0.0
    """
    사용자가 입력한 만족도 점수(1~5)를 강화학습 보상 범위(-1.0 ~ 1.0)로 정규화합니다.
    3점을 기준으로 0.0이 되며, 4점은 0.5, 5점은 1.0이 됩니다.
    """
    return (score - 3) / 2.0


def process_feedback():
    """
    사용자로부터 최종 추천 결과에 대한 만족도 피드백을 입력받아
    원래 점수와 정규화된 Reward 값을 반환합니다.
    """
    print("\n[ 추천 결과 평가 ]")
    while True:
        try:
            raw = input("만족도 입력해 주세요 (1-5): ").strip()
            score = int(raw)
            if score in {1, 2, 3, 4, 5}:
                # 내장된 정규화 함수 호출 (NameError 해결)
                reward = normalize_reward(score)
                return score, reward
        except ValueError:
            pass
        print("1에서 5 사이의 정수를 입력해주세요.")

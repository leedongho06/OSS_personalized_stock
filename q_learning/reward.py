def normalize_reward(score: int) -> float:
    """사용자 피드백 1~5점을 보상 신호로 변환. 5점→1.0 / 3점→0.0 / 1점→-1.0"""
    return (score - 3) / 2.0


def get_feedback() -> int:
    """CLI에서 사용자 피드백 점수를 입력받는다."""
    print("\n[ 추천 결과 평가 ]")
    while True:
        raw = input("만족도를 입력해주세요 (1~5점): ").strip()
        if raw in {"1", "2", "3", "4", "5"}:
            return int(raw)
        print("1~5 사이 숫자를 입력해주세요.")


def process_feedback() -> tuple:
    """피드백 입력받아 보상 신호 변환 후 반환."""
    score = get_feedback()
    reward = normalize_reward(score)
    print(f"피드백: {score}점 → 보상 신호: {reward}")
    return score, reward

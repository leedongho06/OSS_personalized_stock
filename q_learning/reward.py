def normaalize_reward(score: int) -> float:
    """"
    사용자 피드백 1-5점을 보상 신호로 변환
    5 -> 1.0 / 3->0.0
    """
    return (score-3)/2.0
    
def get_feedback() -> int:
    """CLI에서 사용자 피드백 받음"""
    print("\n [ 추천 결과 평가 ].")
    while True:
        raw = input("만족도 입력 해주세요(1-5): ").strip()
        if raw in {"1","2","3","4","5"}:
            return int(raw)
        print("1-5 사이 숫자 입력")

def process_feedback() -> tuple:
    """피드백 입력 -> 보상 신호 변환 후 반환"""
    score = get_feedback()
    reward = normalize_reward(score)
    print(f"피드백:{score}점 -> 보상신호:{reward}w")
    return score, reward

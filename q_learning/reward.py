
class RewardManager:
    def __init__(self):
    # 보상 수치 정의
    self.rewards = {
            'like': 1.0,
            'dislike': -1.0,
            'view': 0.1,
            'skip': -0.1,
            'share': 2.0,
            'comment': 1.5
     }

     if custom_rewards:
         self.rewards.update(custom_rewards)

    def calc_reward(self, feedback_type):
    """
    CLI Interface에서 받은 사용자 피드백을 수치로 변환

    :param feedback_type: 사용자가 보낸 반응 (Like, dislike, view, skip)
    :return: 보상값
    :rtype: float
    """
    def calc_reward(self, feedback_type):
        """
        사용자 피드백에 따른 보상값 반환
        
        :param feedback_type: str
        :return: float (정의되지 않은 액션의 경우 0.0)
        """
        # 소문자로 변환하여 입력값 오차 방지 및 .get()으로 안전하게 조회
        action = feedback_type.lower() if feedback_type else ""
        reward = self.rewards.get(action, 0.0)
        
        return reward

    def batch_calc_rewards(self, feedback_list):
        """
        여러 개의 액션을 한 번에 처리 (리스트 처리용)
        """
        return [self.calc_reward(f) for f in feedback_list]

# 예시
if __name__ == "__main__":
    rm = RewardManager()
    
    test_actions = ['like', 'SKIP', 'unknown_action', None, 'view']
    
    print("=== 개별 액션 처리 ===")
    for action in test_actions:
        reward = rm.calc_reward(action)
        print(f"Action: {str(action):<15} -> Reward: {reward}")

    special_rm = RewardManager(custom_rewards={'dislike': -5.0})
    print(f"\n=== 커스텀 보상 설정 (Dislike 페널티 강화) ===")
    print(f"Dislike Reward: {special_rm.calc_reward('dislike')}")

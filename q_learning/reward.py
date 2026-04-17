
class RewardManager:
    def __init__(self):
    # 보상 수치 정의
    self.LIKE_REWARD = 1.0
    self.DISLIKE_REWARD = -1.0
    self.VIEW_REWARD = 0.1
    self.SKIP_REWARD = -0.1

    def calc_reward(self, feedback_type):
    """
    CLI Interface에서 받은 사용자 피드백을 수치로 변환

    :param feedback_type: 사용자가 보낸 반응 (Like, dislike, view, skip)
    :return: 보상값
    :rtype: float
    """
    if feedback_type == 'like':
        return self.LIKE_REWARD
    elif feedback_type == 'dislike':
        return self.DISLIKE_REWARD
    elif feedback_type == 'view':
        return self.VIEW_REWARD
    elif feedback_type == 'skip':
        return self.SKIP_REWARD
    else:
        return 0.0

# 예시
if __name__ == "__main__":
    rm = RewardManager()
    user_action = 'like'
    curr_reward = rm.calc_reward(user_action)
    print(f"Action: {user_action} -> Reward: {current_reward}")

from unittest.mock import patch
from q_learning.agent import choose_action

def test_choose_action_exploitation():
    """확률값이 EPSILON(0.2)보다 클 때, 탐색(Random)이 아닌 최적 액션을 선택하는지 테스트"""
    # random.random()이 0.9를 반환하게 하여 무조건 최적 액션(Exploitation) 선택 유도
    with patch('random.random', return_value=0.9):
        # 액션 1이 보상값이 더 높음
        q_table = {'state1': {'0': 0.1, '1': 0.9}}
        
        # 0.9 > 0.2 이므로 get_best_action이 실행되어야 함
        action = choose_action(q_table, 'state1')
        assert action == 1

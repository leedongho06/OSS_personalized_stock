import pytest
from q_learning.agent import get_best_action

def test_get_best_action():
    # 상태 'state1'에서 액션 0은 0.5, 액션 1은 0.8의 Q값을 가짐
    q_table = {'state1': {'0': 0.5, '1': 0.8}}
    
    best_action = get_best_action(q_table, 'state1')
    assert best_action == 1
rom unittest.mock import patch
from q_learning.agent import choose_action

def test_choose_action_exploration():
    # random.random()이 0.05를 반환하게 하여 무조건 랜덤 액션이 나오게 설정
    with patch('random.random', return_value=0.05):
        q_table = {'state1': {'0': 0.5, '1': 0.8}}
        # EPSILON(0.2)보다 작으므로 random.choice 실행
        action = choose_action(q_table, 'state1')
        assert action in [0, 1]

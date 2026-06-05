import pytest
from unittest.mock import patch
from q_learning.agent import choose_action, get_best_action

def test_choose_action_exploitation():
    """확률값이 EPSILON(0.2)보다 클 때, 탐색(Random)이 아닌 최적 액션을 선택하는지 테스트"""
    # random.random()이 0.9를 반환하게 하여 무조건 최적 액션(Exploitation) 선택 유도
    with patch('random.random', return_value=0.9):
        # 액션 1이 보상값이 더 높음
        q_table = {'state1': {'0': 0.1, '1': 0.9}}
        
        # 0.9 > 0.2 이므로 get_best_action이 실행되어야 함
        action = choose_action(q_table, 'state1')
        assert action == 1
from q_learning.agent import update_q_value

def test_update_q_value_math_robustness():
    """Q-learning 업데이트 공식이 음수 보상이나 0인 상태에서도 정상 작동하는지 테스트"""
    q_table = {'s1': {'0': 0.0}, 's2': {'0': 0.0}}
    # reward -1.0, ALPHA 0.1, GAMMA 0.9, Current Q 0.0, Next Max Q 0.0
    # 0.0 + 0.1 * (-1.0 + 0.9*0.0 - 0.0) = -0.1
    updated = update_q_value(q_table, 's1', 0, -1.0, 's2')
    
    assert updated['s1']['0'] == -0.1
def test_best_action_key_error():
    """존재하지 않는 상태 조회 시 KeyError 발생 여부 확인 (예외 처리 확인)"""
    q_table = {'state1': {'0': 0.5}}
    with pytest.raises(KeyError):
        get_best_action(q_table, 'unknown_state')

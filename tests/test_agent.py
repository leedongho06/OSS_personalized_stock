import pytest
from q_learning.agent import get_best_action

def test_get_best_action():
    # 상태 'state1'에서 액션 0은 0.5, 액션 1은 0.8의 Q값을 가짐
    q_table = {'state1': {'0': 0.5, '1': 0.8}}
    
    best_action = get_best_action(q_table, 'state1')
    assert best_action == 1

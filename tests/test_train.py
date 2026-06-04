import pytest
from q_learning.train import run_episode
from q_learning.q_table import init_q_table

def test_run_episode_functionality():
    """에피소드 한 번이 정상적으로 실행되어 Q-table을 반환하는지 테스트"""
    q_table = init_q_table()
    style, sector, reward = "공격형", "IT", 1.0
    
    # 함수 실행
    updated_q = run_episode(q_table, style, sector, reward)
    
    # Q-table이 갱신되어 반환되었는지 확인
    assert updated_q is not None
    assert isinstance(updated_q, dict)

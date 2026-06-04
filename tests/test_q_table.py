import pytest
from q_learning.q_table import init_q_table, get_state

def test_init_q_table():
    """Q-table 초기화 시 기본 구조가 잘 생성되는지 확인"""
    q_table = init_q_table()
    assert "공격형_IT" in q_table
    assert len(q_table["공격형_IT"]) == 5 # 액션 5개

def test_get_state():
    """성향과 섹터가 합쳐져서 올바른 state 키가 되는지 확인"""
    assert get_state("공격형", "IT") == "공격형_IT"

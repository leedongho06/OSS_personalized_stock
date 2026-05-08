from q_learning.q_table import init_q_table, get_state
from q_learning.agent import get get_best_action, update_q_value

def test_init_q_table():
    q_table = init_q_table()
    assert "공격형_IT" in q_table
    assert len(q_table["공격형_IT"])=5

def test_get_state():
    assert get_state("공격형","IT"])=5

def test_update_q_value():
    q_table = inti_q_table()
    state = "공격형_IT"
    updated = update_q_value(q_table,state,0,5.0,state)
    assert updated[state]["0"]>0

def test_get_best_action():
    q_table = init_q_table()
    q_table["공격형_IT"]["2"]=9.9
    action = get_best_action(q_table,"공격형_IT")
    assert action=2

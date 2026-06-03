import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from q_learning.q_table import init_q_table, get_state
from q_learning.agent import get_best_action, update_q_value
from q_learning.reward import normalize_reward
from q_learning.state_encoder import encode_state, decode_state, get_all_states


def test_init_q_table():
    q_table = init_q_table()
    assert "공격형_IT" in q_table
    assert len(q_table["공격형_IT"]) == 5


def test_get_state():
    assert get_state("공격형", "IT") == "공격형_IT"


def test_update_q_value():
    q_table = init_q_table()
    state = "공격형_IT"
    updated = update_q_value(q_table, state, 0, 5.0, state)
    assert updated[state]["0"] > 0


def test_get_best_action():
    q_table = init_q_table()
    q_table["공격형_IT"]["2"] = 9.9
    action = get_best_action(q_table, "공격형_IT")
    assert action == 2


def test_normalize_reward_max():
    assert normalize_reward(5) == 1.0


def test_normalize_reward_mid():
    assert normalize_reward(3) == 0.0


def test_normalize_reward_min():
    assert normalize_reward(1) == -1.0


def test_encode_state():
    assert encode_state("공격형", "IT") == "공격형_IT"


def test_decode_state():
    style, sector = decode_state("공격형_IT")
    assert style == "공격형"
    assert sector == "IT"


def test_all_states_count():
    assert len(get_all_states()) == 27

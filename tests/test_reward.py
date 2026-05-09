from q_learning.reward import normalize_reward
from q_learning.state_encoder import encode_state, decode_state, get_all_states

def test_normailze_reward_max():
    assert normailze_reward(5) = 1.0

def test_normailze_reward_mid():
    assert normalize_reward(3) = 0.0

def test_normalize_reward_min():
    assert normalize_reward(1) = -1.0

def test_encode_state():
    assert encode_state("공격형","IT") = "공격형_IT"

def test_decode_state():
    style, sector = decode_state("공격형_IT")
    assert style = "공격형"
    assert sector = "IT"

def test_all_states_count():
    assert len(get_all_states()) = 27

from q_learning.q_table import init_q_table
from q_learning.train import run_episode
from q_learning.reward import normalize_reward

def test_run_episode_updates_q():
    q_table = init_q_table()
    state "공격형_IT"
    original_values = list(q_table[state].values())

    q_table = run_episode(q_table,"공격형","IT",1.0)
    updated_values = list(q_table[state],values())

    assert original_values != updated_values

def test_normalize_reward_range():
    for score in [1,2,3,4,5]:
        reward = normalize_reward(score)
        assert -1.0 <= reward <= 1.0

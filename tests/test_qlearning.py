import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from q_learning.q_table import init_q_table, get_state, save_q_table, load_q_table
from q_learning.agent import get_best_action, update_q_value, choose_action
from q_learning.reward import normalize_reward
from q_learning.state_encoder import encode_state, decode_state, get_all_states
from q_learning.train import run_episode


def test_init_q_table():
    """Q-table 초기화 확인"""
    q_table = init_q_table()
    assert "공격형_IT" in q_table
    assert len(q_table["공격형_IT"]) == 5


def test_get_state():
    """state 키 생성 확인"""
    assert get_state("공격형", "IT") == "공격형_IT"


def test_update_q_value():
    """Q값 업데이트 확인"""
    q_table = init_q_table()
    state = "공격형_IT"
    updated = update_q_value(q_table, state, 0, 5.0, state)
    assert updated[state]["0"] > 0


def test_get_best_action():
    """최선 action 선택 확인"""
    q_table = init_q_table()
    q_table["공격형_IT"]["2"] = 9.9
    action = get_best_action(q_table, "공격형_IT")
    assert action == 2


def test_normalize_reward_max():
    """5점 → 1.0 확인"""
    assert normalize_reward(5) == 1.0


def test_normalize_reward_mid():
    """3점 → 0.0 확인"""
    assert normalize_reward(3) == 0.0


def test_normalize_reward_min():
    """1점 → -1.0 확인"""
    assert normalize_reward(1) == -1.0


def test_normalize_reward_range():
    """1~5점 보상 신호 범위 확인"""
    for score in [1, 2, 3, 4, 5]:
        reward = normalize_reward(score)
        assert -1.0 <= reward <= 1.0


def test_encode_state():
    """state 인코딩 확인"""
    assert encode_state("공격형", "IT") == "공격형_IT"


def test_decode_state():
    """state 디코딩 확인"""
    style, sector = decode_state("공격형_IT")
    assert style == "공격형"
    assert sector == "IT"


def test_all_states_count():
    """전체 state 수 확인 (3 x 9 = 27)"""
    assert len(get_all_states()) == 27


def test_all_states_content():
    """모든 state가 올바른 형식인지 확인"""
    states = get_all_states()
    for state in states:
        assert "_" in state


def test_encode_invalid_style():
    """잘못된 성향 입력 시 예외 발생 확인"""
    with pytest.raises(ValueError):
        encode_state("없는성향", "IT")


def test_decode_invalid_state():
    """잘못된 state 입력 시 예외 발생 확인"""
    with pytest.raises(ValueError):
        decode_state("잘못된state형식")


def test_run_episode_updates_q():
    """에피소드 실행 후 Q값 업데이트 확인"""
    q_table = init_q_table()
    original = list(q_table["공격형_IT"].values())
    q_table = run_episode(q_table, "공격형", "IT", 1.0)
    updated = list(q_table["공격형_IT"].values())
    assert original != updated


def test_save_and_load_q_table():
    """Q-table 저장 및 로드 확인"""
    q_table = init_q_table()
    q_table["공격형_IT"]["0"] = 9.9
    save_q_table(q_table)
    loaded = load_q_table()
    assert loaded["공격형_IT"]["0"] == 9.9


def test_choose_action_returns_valid():
    """choose_action이 유효한 action 반환하는지 확인"""
    q_table = init_q_table()
    state = "공격형_IT"
    action = choose_action(q_table, state)
    assert action in [0, 1, 2, 3, 4]

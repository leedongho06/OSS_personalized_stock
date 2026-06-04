import pytest
from q_learning.reward import normalize_reward

def test_normalize_reward_mapping():
    """1~5점의 피드백 점수가 공식에 맞게 소수점 보상 신호로 치환되는지 검증"""
    assert normalize_reward(5) == 1.0   # (5-3)/2 = 1.0
    assert normalize_reward(4) == 0.5   # (4-3)/2 = 0.5
    assert normalize_reward(3) == 0.0   # (3-3)/2 = 0.0
    assert normalize_reward(1) == -1.0  # (1-3)/2 = -1.0

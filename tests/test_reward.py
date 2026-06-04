import pytest
from q_learning.reward import normalize_reward

def test_normalize_reward_mapping():
    """1~5점의 피드백 점수가 공식에 맞게 소수점 보상 신호로 치환되는지 검증"""
    assert normalize_reward(5) == 1.0   # (5-3)/2 = 1.0
    assert normalize_reward(4) == 0.5   # (4-3)/2 = 0.5
    assert normalize_reward(3) == 0.0   # (3-3)/2 = 0.0
    assert normalize_reward(1) == -1.0  # (1-3)/2 = -1.0
from unittest.mock import patch
from q_learning.reward import get_feedback

def test_get_feedback_immediate_valid():
    """처음부터 올바른 숫자(5)를 입력했을 때 즉시 int형으로 반환하는지 테스트"""
    with patch('builtins.input', return_value="5"):
        assert get_feedback() == 5

def test_get_feedback_invalid_then_valid():
    """잘못된 값(6)을 입력해 경고문 분기를 밟은 후, 올바른 값(2)을 입력했을 때 루프가 정상 작동하는지 검증"""
    # input()이 첫 번째 호출엔 "6", 두 번째 호출엔 "2"를 반환하도록 시뮬레이션
    with patch('builtins.input', side_effect=["6", "2"]):
        assert get_feedback() == 2

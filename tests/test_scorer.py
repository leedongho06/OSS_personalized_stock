import pytest
from unittest.mock import patch
# 프로젝트 구조에 맞게 임포트 경로를 확인하세요 (예: recommendation.scorer)
from recommendation.scorer import get_input_companies, infer_style, print_analysis

# ==============================================================================
# 1. get_input_companies() 함수 테스트 (사용자 입력 분기 완벽 커버)
# ==============================================================================

def test_get_input_companies_all_valid():
    """시나리오 1: 사용자가 3개 모두 정상적인 기업을 입력했을 때"""
    inputs = ["삼성전자", "SK하이닉스", "NAVER"]
    with patch("builtins.input", side_effect=inputs):
        result = get_input_companies()
    assert result == ["삼성전자", "SK하이닉스", "NAVER"]


def test_get_input_companies_with_empty_and_invalid():
    """시나리오 2: 목록에 없는 기업 입력, 중복 입력, 중간에 엔터 쳐서 탈출하는 경우"""
    inputs = ["애플", "삼성전자", "삼성전자", ""]
    with patch("builtins.input", side_effect=inputs):
        result = get_input_companies()
    assert result == ["삼성전자"]


def test_get_input_companies_completely_empty():
    """시나리오 3: 처음부터 그냥 엔터만 쳐서 아무것도 입력하지 않았을 때"""
    inputs = ["", "", ""]
    with patch("builtins.input", side_effect=inputs):
        result = get_input_companies()
    assert result == []

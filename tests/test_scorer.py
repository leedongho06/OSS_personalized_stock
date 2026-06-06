import pytest
from unittest.mock import patch
from recommendation.scorer import get_input_companies, infer_style, print_analysis

# ==============================================================================
# 1. get_input_companies() 함수 테스트
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


# ==============================================================================
# 2. infer_style() 함수 테스트 (Missing 라인 완벽 커버)
# ==============================================================================

def test_infer_style_empty_input():
    """기업 리스트가 비어있을 때 중립형, 5점을 반환하는지 테스트"""
    style, normalized, analyses = infer_style([])
    assert style == "중립형"
    assert normalized == 5
    assert analyses == []

def test_infer_style_conservative():
    """점수가 낮아 '안정형'이 나오는 케이스 테스트"""
    style, normalized, analyses = infer_style(["신한지주", "SK텔레콤"])
    assert style == "안정형"
    assert normalized == 0
    assert len(analyses) == 2

def test_infer_style_neutral():
    """점수가 중간이라 '중립형'이 나오는 케이스 테스트"""
    style, normalized, analyses = infer_style(["LG화학"])
    assert style == "중립형"
    assert normalized == 4

def test_infer_style_aggressive():
    """점수가 높아 '공격형'이 나오는 케이스 테스트"""
    style, normalized, analyses = infer_style(["카카오"])
    assert style == "공격형"
    assert normalized == 9

# 💡 [핵심 추가 1] 56번, 67번 줄 완벽 커버
def test_infer_style_unknown_company():
    """목록에 아예 없는 이상한 기업을 입력했을 때 예외 처리 테스트"""
    # 1. 목록에 없으므로 continue 실행 (56번 줄 커버)
    # 2. analyses가 비어있게 되므로 return "중립형", 5, [] 실행 (67번 줄 커버)
    style, normalized, analyses = infer_style(["우주제일컴퍼니", "화성전자"])
    assert style == "중립형"
    assert normalized == 5
    assert analyses == []

# 💡 [핵심 추가 2] 75번 줄 완벽 커버
def test_infer_style_fallback(monkeypatch):
    """범위를 벗어나는 예외적인 점수가 나왔을 때 맨 아래의 fallback 로직을 타는지 테스트"""
    import recommendation.scorer as scorer
    
    # 정상적인 방법으로는 STYLE_MAP 범위를 벗어날 수 없으므로,
    # STYLE_MAP 자체를 강제로 빈 딕셔너리로 만들어버려 무조건 맨 마지막 줄로 빠지게 유도!
    monkeypatch.setattr(scorer, "STYLE_MAP", {})
    
    style, normalized, analyses = infer_style(["삼성전자"])
    assert style == "중립형"


# ==============================================================================
# 3. print_analysis() 함수 테스트
# ==============================================================================

def test_print_analysis(capsys):
    """화면 인쇄 함수가 예외 없이 정상 출력되는지 테스트"""
    sample_analyses = [
        {"name": "삼성전자", "sector": "IT", "volatility": "중", "score": 3}
    ]
    
    print_analysis("공격형", 7, sample_analyses)
    
    captured = capsys.readouterr()
    assert "[ 선호 기업 분석 결과 ]" in captured.out
    assert "삼성전자" in captured.out
    assert "추론된 투자 성향: 공격형" in captured.out

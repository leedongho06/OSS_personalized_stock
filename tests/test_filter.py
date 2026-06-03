import pytest
import pandas as pd
# 프로젝트 구조에 맞게 임포트 경로를 확인하세요
from recommendation.filter import filter_by_style

# ==============================================================================
# 1. 방어 코드 테스트 (컬럼 누락, 대문자 컬럼 들어온 상황)
# ==============================================================================

def test_filter_by_style_rename_uppercase_columns():
    """시나리오 1: 소문자 per/pbr 대신 대문자 PER/PBR이 들어왔을 때 소문자로 바꾸는지 테스트"""
    # 대문자로 구성된 가짜 데이터프레임 생성
    df = pd.DataFrame({'PER': [10.0], 'PBR': [1.2]})
    
    # 함수 실행 (Value 스타일로 실행하면 per가 10이라 1개가 필터링되어 나와야 함)
    result = filter_by_style(df, "Value")
    
    assert len(result) == 1
    # 결과 컬럼이 소문자 'per'로 바뀌어 있는지 확인
    assert 'per' in result.columns


def test_filter_by_style_assign_default_values():
    """시나리오 2: per, pbr 컬럼이 아예 누락되었을 때 기본값(15.0, 1.0)을 채우는지 테스트"""
    # per, pbr 컬럼이 아예 없는 데이터
    df = pd.DataFrame({'ticker': ['005930']})
    
    # 함수 실행 (기본값 per=15.0이 채워지므로 Growth 스타일 적용 시 결과에 포함되어야 함)
    result = filter_by_style(df, "Growth")
    
    assert len(result) == 1
    assert result.iloc[0]['per'] == 15.0
    assert result.iloc[0]['pbr'] == 1.0

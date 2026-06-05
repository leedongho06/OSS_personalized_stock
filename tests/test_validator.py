import pytest
import pandas as pd
from recommendation.validator import DataValidator

# [1] 데이터가 비어있을 때 테스트
def test_validate_stock_data_empty():
    df = pd.DataFrame()
    with pytest.raises(ValueError, match="데이터프레임이 비어있습니다"):
        DataValidator.validate_stock_data(df)

# [2] 필수 컬럼 누락 테스트
def test_validate_stock_data_missing_columns():
    # 'ticker' 하나만 있고 나머지는 누락된 상황
    df = pd.DataFrame({'ticker': ['005930']})
    with pytest.raises(ValueError, match="필수 컬럼이 누락되었습니다"):
        DataValidator.validate_stock_data(df)
# [3] 숫자형 타입 체크 테스트
def test_validate_stock_data_type_error():
    # 'per' 컬럼이 숫자형이 아닌 문자열인 경우
    df = pd.DataFrame({
        'ticker': ['005930'], 'name': ['삼성'], 'sector': ['IT'],
        'per': ['15'], 'pbr': [1.0], 'ma_20': [70000.0], 'volume': [1000]
    })
    with pytest.raises(TypeError, match="숫자형 데이터여야 계산이 가능합니다"):
        DataValidator.validate_stock_data(df)

# [4] 정상 데이터 테스트
def test_validate_stock_data_success():
    df = pd.DataFrame({
        'ticker': ['005930'], 'name': ['삼성'], 'sector': ['IT'],
        'per': [15.2], 'pbr': [1.0], 'ma_20': [70000.0], 'volume': [1000]
    })
    assert DataValidator.validate_stock_data(df) == True
# [5] 피드백 데이터가 비어있을 때 (서비스 초기) 테스트
def test_validate_feedback_data_empty():
    df = pd.DataFrame()
    assert DataValidator.validate_feedback_data(df) == True

# [6] 피드백 필수 컬럼 누락 테스트
def test_validate_feedback_data_missing_columns():
    df = pd.DataFrame({'user_id': ['user1']}) # 나머지 필수 컬럼 누락
    with pytest.raises(ValueError, match="피드백 필수 컬럼이 누락되었습니다"):
        DataValidator.validate_feedback_data(df) # 참고: 여기는 feedback으로 수정해야 할 수도 있음

# [7] 선호도 값 범위 에러 테스트
def test_validate_feedback_preference_error():
    # preference에 0, 1이 아닌 2가 들어간 경우
    df = pd.DataFrame({
        'user_id': ['u1'], 'ticker': ['005930'], 
        'preference': [2], 'reason': ['좋아요']
    })
    with pytest.raises(ValueError, match="선호도.*값은 0.*또는 1.*구성"):
        DataValidator.validate_feedback_data(df)

# [8] 정상 피드백 테스트
def test_validate_feedback_success():
    df = pd.DataFrame({
        'user_id': ['u1'], 'ticker': ['005930'], 
        'preference': [1], 'reason': ['좋아요']
    })
    assert DataValidator.validate_feedback_data(df) == True

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

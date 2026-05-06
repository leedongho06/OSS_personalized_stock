import pandas as pd

class DataValidator:
    # 동호님의 코드(profile.py, recommender.py)에 맞춘 필수 컬럼
    REQUIRED_STOCK_COLUMNS = ["ticker", "name", "sector", "per", "pbr", "ma_20", "volume"]
    
    # 추천 시스템 고도화를 위한 피드백 필수 컬럼 (상세 이유 포함)
    REQUIRED_FEEDBACK_COLUMNS = ["user_id", "ticker", "preference", "reason"]

    @classmethod
    def validate_stock_data(cls, df: pd.DataFrame) -> bool:
        if df.empty:
            raise ValueError("데이터프레임이 비어있습니다. 수집된 주식 데이터가 없습니다.")

        # 1. 필수 컬럼 누락 확인
        missing_cols = [col for col in cls.REQUIRED_STOCK_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"필수 컬럼이 누락되었습니다: {missing_cols}")

        # 2. 동호님 모델의 MinMaxScaler에 들어갈 피처들의 데이터 타입 확인
        numeric_cols = ["per", "pbr", "ma_20", "volume"]
        for col in numeric_cols:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise TypeError(f"'{col}' 컬럼은 숫자형 데이터여야 계산이 가능합니다.")

        # 결측치는 recommender.py의 fillna(df[cols].median())에서 처리되므로 경고만 출력
        if df[numeric_cols].isnull().any().any():
            print("INFO: 일부 수치형 데이터에 결측치가 존재하며, 추천 모듈에서 중앙값으로 대체됩니다.")

        return True

    @classmethod
    def validate_feedback_data(cls, df: pd.DataFrame) -> bool:
        if df.empty:
            return True # 서비스 초기에는 피드백 데이터가 없을 수 있음

        missing_cols = [col for col in cls.REQUIRED_FEEDBACK_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"피드백 필수 컬럼이 누락되었습니다: {missing_cols}")
            
        if not df['preference'].isin([0, 1]).all():
            raise ValueError("preference(선호도) 값은 0(싫어요) 또는 1(좋아요)로 구성되어야 합니다.")
            
        return True

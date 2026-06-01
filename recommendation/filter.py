import pandas as pd

def filter_by_style(df: pd.DataFrame, style: str) -> pd.DataFrame:
    """
    사용자의 투자 성향(style)에 맞춰 데이터프레임을 필터링합니다.
    FDR/pykrx 수집 실패로 인해 per, pbr 컬럼이 누락된 경우 자동 방어 코드가 가동됩니다.
    """
    # 안전장치: per 또는 pbr 컬럼이 없는 경우 방어 코드 작동
    if 'per' not in df.columns or 'pbr' not in df.columns:
        # 대문자로 들어온 경우 소문자로 복구
        if 'PER' in df.columns:
            df = df.rename(columns={'PER': 'per', 'PBR': 'pbr'})
        else:
            # 아예 없을 경우 에러 방지를 위한 기본값 임시 부여
            if 'per' not in df.columns:
                df['per'] = 15.0
            if 'pbr' not in df.columns:
                df['pbr'] = 1.0

    # 스타일별 필터링 진행
    if style == "Value":
        # 저평가 가치주: PER가 존재하고 0보다 크며 15 미만인 종목 필터링
        filtered_df = df[(df['per'] > 0) & (df['per'] < 15)].dropna(subset=['per']).copy()
    elif style == "Growth":
        # 성장주: 모멘텀 혹은 임시 기준 처리
        filtered_df = df[df['per'] >= 15].dropna(subset=['per']).copy()
    else:
        # 기본 필터링
        filtered_df = df[df['per'] > 0].dropna(subset=['per']).copy()
        
    return filtered_df

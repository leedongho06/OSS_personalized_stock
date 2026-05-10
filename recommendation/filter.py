import pandas as pd

def filter_by_style(df: pd.DataFrame, style: str) -> pd.DataFrame:
    if df.empty:
        return df

    # 안전장치: 컬럼들을 숫자 타입으로 강제 변환 (에러 방지)
    for col in ['per', 'pbr', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 1. 공통 필터링: PER이 0 이하(적자)이거나 데이터가 없는(NaN) 종목 제거
    filtered_df = df[df['per'] > 0].dropna(subset=['per']).copy()
    
    # 2. 성향별 맞춤 필터링
    # style 문자열의 대소문자 구분 없이 처리하기 위해 .capitalize() 사용
    target_style = style.capitalize() if style else "Middle"

    if target_style == "안정형":
        filtered_df = filtered_df[(filtered_df['per'] <= 50) & (filtered_df['pbr'] <= 2.0)]
        
    elif target_style == "공격형":
        # volume 컬럼이 있을 때만 필터링
        if 'volume' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['volume'] >= 100000]
            
    return filtered_df

def filter_by_sector(df: pd.DataFrame, preferred_sectors: list) -> pd.DataFrame:
    if not preferred_sectors or df.empty:
        return df
        
    return df[df['sector'].isin(preferred_sectors)].copy()

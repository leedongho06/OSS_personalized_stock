AGGRESSIVE_SECTORS = ["IT", "커뮤니케이션", "임의소비재"]
STABLE_SECTORS = ["금융", "유틸리티", "필수소비재"]
NEUTRAL_SECTORS = ["헬스케어", "산업재", "소재"]

STYLE_MAP = {
    (0, 3): "안정형",
    (4, 6): "중립형",
    (7, 9): "공격형",
}


def infer_style_from_news(interest: dict) -> tuple:
    """
    섹터별 관심도 → 투자 성향 추론
    반환: (성향, 점수, 분석결과)
    """
    total_score = 0
    count = 0
    analyses = []

    for sector, avg_rating in interest.items():
        # 별점 1~5 → 섹터 가중치 적용
        if sector in AGGRESSIVE_SECTORS:
            sector_weight = 2
        elif sector in NEUTRAL_SECTORS:
            sector_weight = 1
        else:
            sector_weight = 0

        # 별점 높을수록 해당 섹터 성향 강화
        score = sector_weight * (avg_rating / 5)
        total_score += score
        count += 1

        analyses.append({
            "sector": sector,
            "avg_rating": avg_rating,
            "score": round(score, 2)
        })

    if count == 0:
        return "중립형", 5, []

    # 0~9 구간으로 정규화
    normalized = round((total_score / count) * (9 / 2))
    normalized = max(0, min(9, normalized))

    for (lo, hi), style in STYLE_MAP.items():
        if lo <= normalized <= hi:
            return style, normalized, analyses

    return "중립형", normalized, analyses

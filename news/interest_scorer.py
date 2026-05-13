def calculate_interest(rated_news: list) -> dict:
    """
    rated_news = [
        {"sector": "IT", "rating": 5},
        {"sector": "금융", "rating": 2},
        ...
    ]
    → 섹터별 평균 관심도 반환
    """
    sector_scores = {}
    sector_counts = {}

    for item in rated_news:
        sector = item["sector"]
        rating = item["rating"]

        if sector not in sector_scores:
            sector_scores[sector] = 0
            sector_counts[sector] = 0

        sector_scores[sector] += rating
        sector_counts[sector] += 1

    # 섹터별 평균 계산
    interest = {}
    for sector in sector_scores:
        interest[sector] = round(
            sector_scores[sector] / sector_counts[sector], 2
        )

    return interest

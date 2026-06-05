import random

def pick_random_news(news_list: list, n: int = 5) -> list:
    """전체 뉴스에서 섹터 균형 맞춰 무작위 n개 선택."""
    # 섹터별로 균형있게 선택
    sector_groups = {}
    for news in news_list:
        sector = news.get("sector", "기타")
        if sector not in sector_groups:
            sector_groups[sector] = []
        sector_groups[sector].append(news)

    selected = []
    sectors = list(sector_groups.keys())

    while len(selected) < n and sectors:
        sector = random.choice(sectors)
        if sector_groups[sector]:
            selected.append(sector_groups[sector].pop(
                random.randint(0, len(sector_groups[sector])-1)
            ))
        else:
            sectors.remove(sector)

    return selected

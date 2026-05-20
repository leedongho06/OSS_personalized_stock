COMPANY_PROFILE = {
    "삼성전자": {"sector": "IT",           "per": 15.2, "volatility": "중"},
    "SK하이닉스": {"sector": "IT",          "per": 22.1, "volatility": "고"},
    "NAVER":     {"sector": "커뮤니케이션", "per": 38.4, "volatility": "고"},
    "신한지주":  {"sector": "금융",          "per": 7.8,  "volatility": "저"},
    "SK텔레콤":  {"sector": "유틸리티",      "per": 12.3, "volatility": "저"},
    "셀트리온":  {"sector": "헬스케어",      "per": 45.2, "volatility": "고"},
    "카카오":    {"sector": "커뮤니케이션",  "per": 55.0, "volatility": "고"},
    "현대차":    {"sector": "산업재",        "per": 6.5,  "volatility": "중"},
    "LG화학":    {"sector": "소재",          "per": 20.1, "volatility": "중"},
}

VOLATILITY_SCORE = {"저": 0, "중": 1, "고": 2}
SECTOR_SCORE = {
    "금융": 0, "유틸리티": 0, "필수소비재": 0,
    "헬스케어": 1, "산업재": 1, "소재": 1,
    "IT": 2, "커뮤니케이션": 2, "임의소비재": 2,
}
STYLE_MAP = {
    (0, 3): "안정형",
    (4, 6): "중립형",
    (7, 9): "공격형",
}


def get_input_companies() -> list:
    print("\n[ 관심 기업 입력 ]")
    print(f"입력 가능: {', '.join(COMPANY_PROFILE.keys())}\n")
    companies = []
    for i in range(1, 4):
        name = input(f"관심 기업 {i} (없으면 엔터): ").strip()
        if not name:
            break
        if name not in COMPANY_PROFILE:
            print(f"  '{name}'은 목록에 없어요. 건너뜁니다.")
            continue
        if name in companies:
            print(f"  '{name}'은 이미 입력했어요. 건너뜁니다.")
            continue
        companies.append(name)

    if not companies:
        print("  입력된 기업이 없어 중립형으로 설정합니다.")

    return companies


def infer_style(companies: list) -> tuple:
    if not companies:
        return "중립형", 5, []

    analyses, total = [], 0
    for name in companies:
        p = COMPANY_PROFILE[name]
        score = VOLATILITY_SCORE[p["volatility"]] + SECTOR_SCORE.get(p["sector"], 1)
        analyses.append({
            "name": name,
            "sector": p["sector"],
            "volatility": p["volatility"],
            "score": score,
        })
        total += score

    normalized = round((total / len(companies)) * (9 / 4))

    for (lo, hi), style in STYLE_MAP.items():
        if lo <= normalized <= hi:
            return style, normalized, analyses

    return "중립형", normalized, analyses


def print_analysis(style: str, score: int, analyses: list):
    print("\n[ 선호 기업 분석 결과 ]")
    print(f"{'기업명':<12} {'섹터':<14} {'변동성':<6} 점수")
    print("-" * 42)
    for a in analyses:
        print(f"{a['name']:<12} {a['sector']:<14} {a['volatility']:<6} {a['score']}")
    print("-" * 42)
    print(f"추론된 투자 성향: {style} (점수: {score})\n")

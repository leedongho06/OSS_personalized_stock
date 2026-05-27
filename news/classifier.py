SECTOR_KEYWORDS = {
    "IT": ["삼성전자", "SK하이닉스", "반도체", "AI", "인공지능", "클라우드", "소프트웨어", "칩"],
    "커뮤니케이션": ["카카오", "NAVER", "네이버", "구글", "메타", "유튜브", "SNS", "플랫폼"],
    "금융": ["신한", "KB", "하나", "우리은행", "증권", "금리", "펀드", "보험", "은행"],
    "헬스케어": ["셀트리온", "삼성바이오", "제약", "바이오", "신약", "의료", "병원", "헬스"],
    "산업재": ["현대차", "기아", "조선", "건설", "철강", "두산", "HD현대", "자동차"],
    "유틸리티": ["한전", "SK텔레콤", "KT", "LGU+", "가스", "전기", "통신"],
    "소재": ["LG화학", "롯데케미칼", "화학", "소재", "배터리"],
    "필수소비재": ["CJ", "농심", "오리온", "식품", "생활용품"],
    "임의소비재": ["롯데쇼핑", "이마트", "패션", "여행", "호텔"],
}

# [추가됨] 기업명보다 우선해서 걸러낼 '사회/이슈' 키워드
EXCEPTION_KEYWORDS = ["파업", "노조", "시위", "집회", "투쟁", "횡령", "배임", "갑질", "수사"]

def classify_sector(title: str, description: str = "") -> str:
    """뉴스 제목 + 내용으로 섹터 자동 분류."""
    text = title + " " + description
    
    # 1. 예외 규칙 먼저 검사 (파업 등 이슈 키워드가 있으면 '사회/이슈'로 강제 분류)
    for exc_kw in EXCEPTION_KEYWORDS:
        if exc_kw in text:
            return "사회/이슈"

    # 2. 기존 산업 섹터 분류 로직
    scores = {sector: 0 for sector in SECTOR_KEYWORDS}
    for sector, keywords in SECTOR_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                scores[sector] += 1

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "기타"

def add_sector_to_news(news_list: list) -> list:
    """뉴스 리스트에 섹터 필드 추가."""
    result = []
    for news in news_list:
        title = news.get("title", "").replace("<b>", "").replace("</b>", "")
        description = news.get("description", "")
        
        sector = classify_sector(title, description)
        
        result.append({
            "title": title,
            "description": description,
            "sector": sector,
            "link": news.get("link", ""),
            "pubDate": news.get("pubDate", ""),
        })
    return result

SECTOR_KEYWORDS = {
    "IT": [
        "삼성전자", "SK하이닉스", "반도체", "AI", "인공지능",
        "클라우드", "소프트웨어", "칩", "HBM", "파운드리",
        "LG이노텍", "삼성전기", "삼성SDS", "SK스퀘어"
    ],
    "커뮤니케이션": [
        "카카오", "NAVER", "네이버", "구글", "메타",
        "유튜브", "SNS", "플랫폼", "하이브", "엔씨소프트",
        "JYP", "에스엠", "넷마블", "게임", "엔터"
    ],
    "금융": [
        "신한", "KB금융", "하나금융", "우리금융", "기업은행",
        "증권", "금리", "펀드", "보험", "배당", "은행",
        "삼성생명", "한화생명", "미래에셋", "삼성카드"
    ],
    "헬스케어": [
        "셀트리온", "삼성바이오", "한미약품", "제약", "바이오",
        "신약", "의료", "병원", "헬스", "바이오시밀러",
        "SK바이오", "유한양행", "휴젤", "한미사이언스"
    ],
    "산업재": [
        "현대차", "기아", "조선", "건설", "두산",
        "HD현대", "한화", "대한항공", "한진", "GTX",
        "현대건설", "한국항공우주", "한화오션", "HMM"
    ],
    "유틸리티": [
        "한전", "한국전력", "SK텔레콤", "KT", "LGU+",
        "가스", "전기요금", "통신", "한국가스공사"
    ],
    "소재": [
        "포스코", "LG화학", "롯데케미칼", "화학", "배터리",
        "철강", "소재", "고려아연", "금호석유", "OCI",
        "포스코퓨처엠", "삼성SDI", "SK이노베이션"
    ],
    "필수소비재": [
        "CJ", "농심", "오리온", "식품", "생활용품",
        "하이트진로", "KT&G", "롯데"
    ],
    "임의소비재": [
        "이마트", "롯데쇼핑", "패션", "여행", "호텔",
        "호텔신라", "아모레", "GS리테일", "코웨이"
    ],
}


def classify_sector(title: str, description: str = "") -> str:
    text = title + " " + description
    scores = {sector: 0 for sector in SECTOR_KEYWORDS}

    for sector, keywords in SECTOR_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                scores[sector] += 1

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "기타"


def add_sector_to_news(news_list: list) -> list:
    result = []
    for news in news_list:
        title = news.get("title", "").replace("<b>", "").replace("</b>", "")
        description = news.get("description", "").replace("<b>", "").replace("</b>", "")
        sector = classify_sector(title, description)
        result.append({
            "title": title,
            "description": description,
            "sector": sector,
            "link": news.get("link", ""),
        })
    return result

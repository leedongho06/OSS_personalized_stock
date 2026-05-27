import os
import requests
import time

CLIENT_ID = os.environ.get("NAVER_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET", "")

SEARCH_QUERIES = [
    "삼성전자", "SK하이닉스", "POSCO홀딩스", "현대차", "기아",
    "NAVER", "LG화학", "삼성SDI", "카카오", "셀트리온",
    "LG", "삼성물산", "현대모비스", "SK이노베이션", "SK텔레콤",
    "KT", "신한지주", "KB금융", "하나금융", "우리금융",
    "삼성생명", "삼성전기", "삼성SDS", "SK", "HMM",
    "고려아연", "넷마블", "LG전자", "한화솔루션", "대한항공",
    "아모레퍼시픽", "S-Oil", "한국타이어", "삼성화재", "기업은행",
    "이마트", "LG이노텍", "CJ제일제당", "CJ", "코웨이",
    "SK스퀘어", "GS", "유한양행", "한화생명", "한국금융지주",
    "호텔신라", "한온시스템", "금호석유", "한미반도체", "현대건설",
    "한화시스템", "포스코퓨처엠", "SK바이오팜", "삼성바이오로직스", "한미약품",
    "엔씨소프트", "위메이드", "펄어비스", "JYP", "에스엠",
    "미래에셋증권", "삼성증권", "삼성카드", "한진칼", "하이트진로",
    "GS리테일", "현대제철", "OCI홀딩스", "현대해상", "LS",
    "DB손해보험", "아모레G", "롯데케미칼", "롯데쇼핑", "롯데지주",
    "KT&G", "한국항공우주", "HD한국조선해양", "삼성중공업", "한화오션",
    "HD현대", "HD현대중공업", "한국전력", "한국가스공사", "두산",
    "두산에너빌리티", "두산밥캣", "하이브", "한미사이언스", "휴젤",
    "반도체 주식", "바이오 주식", "금융 주식", "자동차 주식", "IT 주식",
]

# [추가됨] 누락되었던 가짜 뉴스 제공 함수 (테스트용)
def fetch_dummy_news() -> list:
    return [
        {
            "title": "삼성전자, 새로운 <b>AI</b> 반도체 혁신 발표",
            "description": "최신 인공지능 기술이 탑재된 칩을 다음 달 공개합니다.",
            "link": "#",
            "pubDate": "2026-05-27"
        },
        {
            "title": "전국 철도 <b>노조 파업</b> 돌입, 교통 마비 우려",
            "description": "임금 인상을 요구하며 무기한 파업과 시위 투쟁에 나섰습니다.",
            "link": "#",
            "pubDate": "2026-05-27"
        },
        {
            "title": "현대차, 글로벌 시장에서 전기차 판매량 1위 달성",
            "description": "글로벌 자동차 산업의 새로운 역사를 쓰고 있습니다.",
            "link": "#",
            "pubDate": "2026-05-26"
        },
        {
            "title": "모 은행 대규모 <b>횡령</b> 사태 발생, 당국 수사 착수",
            "description": "직원 배임 및 횡령 의혹으로 금융권에 큰 충격을 주고 있습니다.",
            "link": "#",
            "pubDate": "2026-05-26"
        },
        {
            "title": "네이버, 신규 플랫폼 서비스로 시장 공략",
            "description": "커뮤니케이션과 쇼핑을 결합한 새로운 플랫폼을 런칭합니다.",
            "link": "#",
            "pubDate": "2026-05-25"
        }
    ]

def fetch_news(query: str, display: int = 5) -> list:
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
    }
    params = {
        "query": query,
        "display": display,
        "sort": "date",
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"API 오류: {response.status_code}")
        return []
    return response.json().get("items", [])

def fetch_all_news(display_per_query: int = 10) -> list:
    all_news = []
    for query in SEARCH_QUERIES:
        news = fetch_news(query, display=display_per_query)
        if news:  # 성공한 것만 추가
            all_news.extend(news)
        if len(all_news) >= 50:  # 50개 모이면 중단
            break
        time.sleep(0.5)  # 0.5초로 줄이기

    # API 실패시 더미 뉴스로 대체
    if not all_news:
        print("API 제한 - 더미 뉴스로 대체합니다.")
        all_news = fetch_dummy_news()

    return all_news

import requests
import json

CLIENT_ID = os.environ.get('NAVER_CLIENT_ID')
CLIENT_SECRET = os.environ.get('NAVER_CLIENT_SECRET')

if not CLIENT_ID or not CLIENT_SECRET:
    print("[경고]")

# 섹터 분류 키워드 (성현님 제공 로직)
SECTOR_KEYWORDS = {
    "IT": ["삼성전자", "SK하이닉스", "반도체", "AI", "인공지능", "클라우드", "소프트웨어", "IT", "칩"],
    "커뮤니케이션": ["카카오", "NAVER", "네이버", "구글", "메타", "유튜브", "SNS", "플랫폼"],
    "금융": ["신한", "KB", "하나", "우리은행", "증권", "금리", "주식", "펀드", "보험"],
    "헬스케어": ["셀트리온", "삼성바이오", "제약", "바이오", "신약", "의료", "병원"],
    "산업재": ["현대차", "기아", "조선", "건설", "철강", "두산", "HD현대"],
    "유틸리티": ["한전", "SK텔레콤", "KT", "LGU+", "가스", "전기", "통신"],
    "소재": ["LG화학", "롯데케미칼", "화학", "소재", "배터리"],
    "필수소비재": ["CJ", "농심", "오리온", "식품", "생활용품"],
    "임의소비재": ["롯데쇼핑", "이마트", "패션", "여행", "호텔"],
}

def classify_sector(title: str) -> str:
    scores = {sector: 0 for sector in SECTOR_KEYWORDS}
    for sector, keywords in SECTOR_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title:
                scores[sector] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "기타"

def fetch_news_as_list(query, display=10):
    """
    뉴스 데이터를 [{title, sector, url}, ...] 형식의 리스트로 반환합니다.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.naver.com/'
    }

    params = {
        'where': 'news',
        'query': query,
        'sort': '1',
        'nso': 'so:dd,p:all,a:all'
    }

    url = f"https://search.naver.com/search.naver?where=news&query={query}&sort=1"
    
    news_list = []
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("[오류] 네이버 접속 실패 (상태 코드: {respose.staus_code})")
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('ul.list_news > li.bx')
        
        for item in items[:display]:
            title_tag = item.select_one('a.news_tit')
            if not title_tag: continue
            
            title = title_tag.text
            link = title_tag['href']
            
            # 섹터 분류 수행
            sector = classify_sector(title)
            
            # 요청하신 데이터 형식으로 구성
            news_list.append({
                "title": title,
                "sector": sector,
                "url": link
            })
            
    except Exception as e:
        print(f"크롤링 에러: {e}")
        
    return news_list

if __name__ == "__main__":
    # 테스트 실행
    search_keyword = "엔비디아 반도체"
    result_data = fetch_news_as_list(search_keyword, display=5)
    
    # 결과 출력
    import json
    print(json.dumps(result_data, indent=4, ensure_ascii=False))

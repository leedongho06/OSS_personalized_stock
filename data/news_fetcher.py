
import os
import requests
import json
import time

# 환경변수 로드
CLIENT_ID = os.environ.get('NAVER_CLIENT_ID')
CLIENT_SECRET = os.environ.get('NAVER_CLIENT_SECRET')

# 성현님의 섹터 키워드
SECTOR_KEYWORDS = {
    "IT": ["삼성전자", "SK하이닉스", "반도체", "AI"],
    "커뮤니케이션": ["카카오", "NAVER", "플랫폼"],
    "금융": ["신한", "KB", "우리은행", "금리"],
    "헬스케어": ["셀트리온", "삼성바이오", "제약"],
    "산업재": ["현대차", "기아", "조선"],
    "유틸리티": ["한전", "SK텔레콤", "통신"],
    "소재": ["LG화학", "롯데케미칼", "배터리"],
    "필수소비재": ["CJ", "농심", "식품"],
    "임의소비재": ["롯데쇼핑", "이마트", "여행"],
}

def classify_sector(title: str) -> str:
    """기사 제목을 분석해 섹터 분류"""
    scores = {sector: 0 for sector in SECTOR_KEYWORDS}
    for sector, keywords in SECTOR_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title:
                scores[sector] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "기타"

def fetch_all_sector_news(display_per_keyword=5):
    """모든 섹터의 키워드를 순회하며 뉴스를 수집합니다."""
    all_news = []
    seen_urls = set() # 중복 기사 제거용
    
    # 1. 모든 섹터와 그 안의 키워드들을 추출
    search_targets = []
    for sector, keywords in SECTOR_KEYWORDS.items():
        search_targets.extend(keywords)
    
    print(f"총 {len(search_targets)}개의 키워드로 수집을 시작합니다...")

    for kw in search_targets:
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
        params = {"query": kw, "display": display_per_keyword, "sort": "date"} # 최신순 수집

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                items = response.json().get('items', [])
                for item in items:
                    link = item['link']
                    if link not in seen_urls: # 중복 제거
                        title = item['title'].replace('<b>','').replace('</b>','').replace('&quot;','"')
                        all_news.append({
                            "title": title,
                            "sector": classify_sector(title),
                            "url": link
                        })
                        seen_urls.add(link)
            
            # API 과부하 방지 및 차단 예방을 위한 아주 짧은 휴식
            time.sleep(0.1) 
            
        except Exception as e:
            print(f"'{kw}' 수집 중 에러: {e}")

    return all_news

if __name__ == "__main__":
    total_results = fetch_all_sector_news(display_per_keyword=3)
    print(f"\n✅ 수집 완료! 총 {len(total_results)}개의 유니크한 기사를 가져왔습니다.")
    print(json.dumps(total_results[:10], indent=4, ensure_ascii=False)) # 상위 10개만 출력

import urllib.request
import xml.etree.ElementTree as ET

def fetch_all_news():
    """실시간 경제, 주식, 기업 뉴스를 수집하여 반환합니다."""
    # API 키 없이 실시간 한국 뉴스를 가져오기 가장 안정적인 뉴스 RSS 주소
    url = "https://news.google.com/rss/search?q=주식+OR+경제+OR+기업+OR+증권&hl=ko&gl=KR&ceid=KR:ko"
    
    result = []
    try:
        # 봇(Bot) 차단을 막기 위해 일반 브라우저인 것처럼 위장 (예전 차단 에러 방지)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req).read()
        root = ET.fromstring(response)
        
        # 가장 따끈따끈한 최신 뉴스 10개를 긁어옵니다
        for item in root.findall('./channel/item')[:10]:
            title = item.find('title').text
            link = item.find('link').text
            pubDate = item.find('pubDate').text
            
            result.append({
                "title": title,
                "description": title,  # 제미나이가 문맥을 파악할 수 있도록 전달
                "link": link,
                "pubDate": pubDate
            })
        return result
        
    except Exception as e:
        print(f"실시간 뉴스 수집 에러 발생: {e}")
        return []

if __name__ == "__main__":
    # 코드가 잘 작동하는지 단독으로 테스트
    news_list = fetch_all_news()
    for n in news_list:
        print(n['title'])

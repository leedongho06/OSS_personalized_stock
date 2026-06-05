import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET


def fetch_all_news():
    """실시간 경제, 주식, 기업 뉴스를 수집하여 반환합니다."""
    query = urllib.parse.quote("주식 OR 경제 OR 기업 OR 증권")
    url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"

    result = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req).read()
        root = ET.fromstring(response)

        for item in root.findall('./channel/item')[:10]:
            title = item.find('title').text
            link = item.find('link').text
            pubDate = item.find('pubDate').text

            result.append({
                "title": title,
                "description": title,
                "link": link,
                "pubDate": pubDate
            })
        return result

    except Exception as e:
        print(f"실시간 뉴스 수집 에러 발생: {e}")
        return []


if __name__ == "__main__":
    news_list = fetch_all_news()
    for n in news_list:
        print(n['title'])

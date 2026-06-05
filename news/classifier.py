import os
import google.generativeai as genai


# 1. 터미널에 등록한 제미나이 키 가져오기
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# 2. 분류 카테고리 목록
SECTORS = ["IT", "커뮤니케이션", "금융", "헬스케어", "산업재", "유틸리티", "소재", "필수소비재", "임의소비재", "사회/이슈", "기타"]

def classify_sector(title: str, description: str = "") -> str:

    """제미나이(Gemini) AI를 이용해 아주 엄격한 기준으로 뉴스 문맥을 분석합니다."""

    text = title + " " + description
    
    if not GEMINI_API_KEY:
        return "기타"
        
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 💡 예시를 제거하여 편향을 없앤 완벽한 프롬프트
        prompt = f"""
        너는 여의도 최고의 주식 시장 애널리스트야.
        다음 뉴스의 제목과 내용을 꼼꼼히 읽고, 아래의 [섹터별 엄격한 분류 기준]을 적용하여 가장 핵심이 되는 주제 하나만 정확하게 골라.
        
        [섹터별 엄격한 분류 기준]
        1. IT: 반도체, 스마트폰, 디스플레이, 전자기기 하드웨어
        2. 커뮤니케이션: 인터넷 플랫폼, 검색엔진, SNS, 게임, 통신사
        3. 금융: 은행, 증권, 보험, 금리 인상/인하, 환율, 거시경제 지표
        4. 헬스케어: 제약, 신약 개발, 바이오, 의료기기, 병원/의료 정책
        5. 산업재: 자동차, 기계, 조선(배), 건설, 항공, 우주
        6. 유틸리티: 전력, 가스, 수도, 원전 등 공공 인프라
        7. 소재: 2차전지(배터리), 화학, 철강, 정유
        8. 필수소비재: 식음료, 마트, 생필품
        9. 임의소비재: 백화점, 의류, 화장품, 호텔, 여행
        10. 사회/이슈: 파업, 시위, 횡령, 배임, 갑질, 정치인 공약, 선거, 수사 등 기업 본업(돈 버는 일)과 무관한 사회적 사건사고
        
        [특별 주의사항]
        - 기사 안에 여러 산업군의 단어가 섞여 있어도 헷갈리지 마. 기사의 '가장 중심이 되는 핵심 주제' 하나만 선택해.
        - 정치나 사건사고 뉴스는 무조건 '사회/이슈'로 빼.
        
        [카테고리 목록]: {', '.join(SECTORS)}
        
        [뉴스 제목]: {title}
        [뉴스 내용]: {description}
        
        답변 (설명은 일절 하지 말고 오직 카테고리 이름만 하나 출력해):
        """
        
        response = model.generate_content(prompt)
        answer = response.text.strip()
        
        for sector in SECTORS:
            if sector in answer:
                return sector
        return "기타"
        
    except Exception as e:
        print(f"제미나이 API 연동 에러 발생: {e}")
        return "기타"

def add_sector_to_news(news_list: list) -> list:
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

        })
    return result

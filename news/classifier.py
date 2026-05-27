import os
import google.generativeai as genai

# 1. 터미널에 등록한 제미나이 키 가져오기
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# 2. 분류 카테고리 목록
SECTORS = ["IT", "커뮤니케이션", "금융", "헬스케어", "산업재", "유틸리티", "소재", "필수소비재", "임의소비재", "사회/이슈", "기타"]

def classify_sector(title: str, description: str = "") -> str:
    """제미나이(Gemini) AI를 이용해 뉴스 문맥을 분석하고 카테고리를 분류합니다."""
    text = title + " " + description
    
    # 키가 제대로 안 들어갔을 경우를 대비한 안전장치
    if not GEMINI_API_KEY:
        return "기타"
        
    try:
        # 제미나이 AI 모델 불러오기
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # AI에게 내릴 명령(프롬프트) 작성
        prompt = f"""
        너는 주식 시장의 뉴스를 분석하는 최고 수준의 AI 애널리스트야.
        다음 뉴스의 제목과 내용을 읽고, 문맥을 파악해서 아래 카테고리 중 가장 알맞은 하나만 정확하게 골라서 대답해줘.
        
        [특별 규칙]
        만약 파업, 노조, 시위, 횡령, 배임, 갑질, 수사 같은 사회적 이슈나 사건/사고라면 기업 이름이 있어도 무조건 '사회/이슈'로 분류해.
        
        [카테고리 목록]: {', '.join(SECTORS)}
        
        [뉴스 제목]: {title}
        [뉴스 내용]: {description}
        
        답변 (설명 없이 오직 카테고리 이름만 하나 출력해):
        """
        
        # AI에게 프롬프트 던지고 답변 받기
        response = model.generate_content(prompt)
        answer = response.text.strip()
        
        # 대답한 카테고리가 목록에 있는지 확인 후 반환
        for sector in SECTORS:
            if sector in answer:
                return sector
        return "기타"
        
    except Exception as e:
        print(f"제미나이 API 연동 에러 발생: {e}")
        return "기타"

def add_sector_to_news(news_list: list) -> list:
    """뉴스 리스트에 섹터 필드 추가."""
    result = []
    for news in news_list:
        title = news.get("title", "").replace("<b>", "").replace("</b>", "")
        description = news.get("description", "")
        
        # 이제 제미나이 AI가 뉴스를 읽고 판단합니다!
        sector = classify_sector(title, description)
        
        result.append({
            "title": title,
            "description": description,
            "sector": sector,
            "link": news.get("link", ""),
            "pubDate": news.get("pubDate", ""),
        })
    return result


import json
import os

def save_metadata(ticker, data):
    """
    특정 종목(ticker)의 메타데이터 딕셔너리를 JSON 파일로 저장합니다.
    """
    file_name = f"{ticker}_meta.json"
    
    # ensure_ascii=False 를 통해 한글이 깨지지 않게 저장합니다.
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"[{ticker}] 메타데이터 JSON({file_name}) 저장 성공!")

def load_metadata(ticker):
    """
    특정 종목(ticker)의 메타데이터를 JSON 파일에서 불러옵니다.
    """
    file_name = f"{ticker}_meta.json"
    
    # 파일이 존재하는지 먼저 확인
    if not os.path.exists(file_name):
        print(f"[{ticker}] 메타데이터 파일이 존재하지 않습니다.")
        return None
        
    with open(file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    return data

# --- 여기서부터 테스트 실행 파트 ---
if __name__ == "__main__":
    print("--- JSON 데이터 관리 테스트 시작 ---")
    
    # 1. 저장할 가짜 메타데이터 생성 (종목명, 섹터, 설명 등)
    sample_meta = {
        "ticker": "005930",
        "name": "삼성전자",
        "sector": "정보기술",
        "description": "한국의 대표 반도체 및 스마트폰 제조 기업",
        "update_freq": "daily"
    }
    
    # 2. JSON 파일로 저장 테스트
    save_metadata('005930', sample_meta)
    
    # 3. 저장된 JSON 파일 불러오기 테스트
    loaded_data = load_metadata('005930')
    
    print("\n--- 불러온 데이터 확인 ---")
    print(loaded_data)
    print("--- 테스트 종료 ---")

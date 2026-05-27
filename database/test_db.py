import sys
import os

# 현재 파일 위치에서 상위 폴더(최상위 디렉토리)로 경로 연결
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import insert_user, get_user

def test_user_database():
    print("--- 🧪 DB 사용자 저장 및 조회 자동 테스트 시작 ---")
    
    # 1. 가짜 사용자 데이터 입력 (저장 테스트)
    test_id = "test_user_001"
    test_name = "홍길동"
    test_type = "안정형"
    
    print(f"1. [{test_name}] 사용자 데이터를 DB에 저장합니다...")
    insert_user(test_id, test_name, test_type)
    
    # 2. 방금 넣은 데이터 다시 빼오기 (조회 테스트)
    print(f"2. DB에서 [{test_id}] 데이터를 다시 불러옵니다...")
    user_data = get_user(test_id)
    
    # 3. 파이썬이 자동으로 정답 채점 
    # user_data는 ('test_user_001', '홍길동', '안정형') 형태의 튜플로 반환됩니다.
    if user_data and user_data[1] == test_name and user_data[2] == test_type:
        print("\n✅ [테스트 통과] 데이터베이스 저장 및 조회가 완벽하게 작동합니다!")
        print(f"불러온 데이터: {user_data}")
    else:
        print("\n❌ [테스트 실패] 저장된 데이터가 일치하지 않거나 불러오지 못했습니다.")

if __name__ == "__main__":
    test_user_database()

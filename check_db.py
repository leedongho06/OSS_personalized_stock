import sqlite3

# DB 파일 경로 설정 (경로가 맞는지 꼭 확인하세요!)
DB_PATH = "data/stock_data.db"

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 존재하는 모든 테이블 목록 조회
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("=== [1] 생성된 테이블 목록 ===")
    if not tables:
        print("⚠️ DB에 생성된 테이블이 하나도 없습니다!")
    for table in tables:
        table_name = table[0]
        print(f"📌 테이블명: {table_name}")
        
        # 2. 각 테이블의 컬럼 정보(이름, 타입 등) 조회
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print("    [컬럼 정보]")
        for col in columns:
            # col[1]: 컬럼명, col[2]: 데이터 타입
            print(f"    - {col[1]} ({col[2]})")
        print("-" * 40)
        
    conn.close()

except Exception as e:
    print(f"❌ DB 구조 조회 중 오류 발생: {e}")

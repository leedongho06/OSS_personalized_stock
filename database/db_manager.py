import sqlite3

# 실제 데이터베이스 파일 경로
DB_PATH = 'stock_data.db'

# [A1(크롤링) 팀원과 연결될 부분]
# A1이 주식 종목과 이름을 수집해오면, 이 함수를 호출하여 DB에 저장하게 됩니다.
def insert_stock(ticker, name):
    """
    A1이 수집한 주식 데이터를 DB에 넣는 함수
    :param ticker: 주식 종목 코드 (예: '005930')
    :param name: 주식 종목명 (예: '삼성전자')
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 중복 데이터는 무시하고 새로운 데이터만 삽입
    cursor.execute('INSERT OR IGNORE INTO stocks (ticker, name) VALUES (?, ?)', (ticker, name))
    
    conn.commit()
    conn.close()
    # 나중에 로그 확인용으로 print를 남겨두면 협업 시 편리합니다.
    # print(f"데이터 저장 완료: {name}({ticker})")

# [A3/A4(분석 및 UI) 팀원과 연결될 부분]
# 추천 알고리즘을 이나 화면에 출력하는  데이터를 요구할 때 호출됩니다
def get_all_stocks():
    """
    저장된 모든 주식 목록을 불러와서 반환하는 함수
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM stocks')
    rows = cursor.fetchall()
    
    conn.close()
    return rows

# [실제 프로그램 실행 시에는 무시되는 테스트 구역]
# 이 파일(db_manager.py)을 직접 실행했을 때만 작동하며, 나중에 통합 시에는 실행되지 않습니다.
if __name__ == "__main__":
    print("--- DB 관리 모듈 개별 테스트 시작 ---")
    
    # 1. 테스트용 임의 데이터 (나중에 A1의 실제 데이터로 대체될 부분)
    test_ticker = '005930'
    test_name = 'Samsung'
    
    print(f"테스트 데이터를 삽입합니다: {test_name}")
    insert_stock(test_ticker, test_name)
    
    # 2. 저장 결과 확인 (나중에 사용할 기능)
    print("DB에 저장된 내용을 확인합니다...")
    stocks = get_all_stocks()
    
    if stocks:
        for s in stocks:
            print(f"조회 성공: {s}")
    else:
        print("데이터가 없습니다. init_db.py를 먼저 실행했는지 확인하세요.")
        
    print("--- 테스트 종료 ---")

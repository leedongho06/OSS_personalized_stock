import sqlite3
import os

def initialize_database():
    db_path = 'stock_data.db'
    schema_path = 'database/schema.sql'

    # 기존 DB가 있으면 삭제하고 새로 시작
    if os.path.exists(db_path):
        os.remove(db_path)

    # DB 연결 및 작업자(cursor) 생성
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 설계도 읽기
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_script = f.read()

    # 설계도대로 테이블 생성
    cursor.executescript(schema_script)

    conn.commit()
    conn.close()
    print("성공: stock_data.db 파일이 생성되었습니다.")

if __name__ == "__main__":
    initialize_database()

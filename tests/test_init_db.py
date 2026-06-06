import pytest
from unittest.mock import patch, mock_open, MagicMock
from database.init_db import initialize_database

# 테스트용 가짜 스키마 텍스트
MOCK_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY);
"""

@patch("database.init_db.sqlite3.connect")
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_SCHEMA_SQL)
@patch("database.init_db.os.remove")
@patch("database.init_db.os.path.exists")
def test_initialize_database_with_existing_db(mock_exists, mock_remove, mock_file_open, mock_connect):
    """기존 DB 파일이 존재할 때: 삭제 후 새로 생성하는지 테스트"""
    
    # 1. 가짜 환경 설정
    mock_exists.return_value = True # 기존 파일이 있다고 속임
    
    # DB 커서 및 연결 가짜 객체 설정
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    
    # 2. 함수 실행
    initialize_database()
    
    # 3. 검증
    # 파일 존재 확인 및 삭제가 각각 1번씩 실행되어야 함
    mock_exists.assert_called_once_with('stock_data.db')
    mock_remove.assert_called_once_with('stock_data.db')
    
    # 파일 열기와 스크립트 실행이 정상적으로 호출되었는지 확인
    mock_file_open.assert_called_once_with('database/schema.sql', 'r', encoding='utf-8')
    mock_cursor.executescript.assert_called_once_with(MOCK_SCHEMA_SQL)
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("database.init_db.sqlite3.connect")
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_SCHEMA_SQL)
@patch("database.init_db.os.remove")
@patch("database.init_db.os.path.exists")
def test_initialize_database_without_existing_db(mock_exists, mock_remove, mock_file_open, mock_connect):
    """기존 DB 파일이 없을 때: 삭제 과정 없이 새로 생성하는지 테스트"""
    
    # 1. 가짜 환경 설정
    mock_exists.return_value = False # 기존 파일이 없다고 속임
    
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    
    # 2. 함수 실행
    initialize_database()
    
    # 3. 검증
    mock_exists.assert_called_once_with('stock_data.db')
    mock_remove.assert_not_called() # 💡 핵심: 파일이 없으니 삭제(remove)가 불리지 않아야 함
    
    mock_cursor.executescript.assert_called_once_with(MOCK_SCHEMA_SQL)
    mock_conn.commit.assert_called_once()

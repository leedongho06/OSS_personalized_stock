import pytest
import json
from unittest.mock import patch, mock_open
from database.json_manager import save_metadata, load_metadata

# 테스트에서 사용할 가짜 데이터
MOCK_TICKER = "005930"
MOCK_DATA = {
    "ticker": "005930",
    "name": "삼성전자",
    "sector": "정보기술"
}
# json.dumps는 파이썬 딕셔너리를 JSON 문자열로 바꿔줍니다.
MOCK_JSON_STR = json.dumps(MOCK_DATA, ensure_ascii=False, indent=4)

# =====================================================================
# 1. save_metadata() 테스트
# =====================================================================
@patch("builtins.open", new_callable=mock_open)
def test_save_metadata(mock_file):
    """주어진 데이터를 JSON 파일로 정상적으로 저장(쓰기)하는지 테스트"""
    
    # 함수 실행
    save_metadata(MOCK_TICKER, MOCK_DATA)
    
    # 검증: 올바른 파일명('005930_meta.json')으로 쓰기 모드('w')로 열었는가?
    mock_file.assert_called_once_with(f"{MOCK_TICKER}_meta.json", 'w', encoding='utf-8')
    
    # 검증: 파일에 기록된 내용(문자열)을 전부 모아서, 원래 MOCK_JSON_STR과 동일한지 확인
    # json.dump는 내부적으로 write()를 여러 번 호출할 수 있으므로, 인자들을 합쳐서 비교합니다.
    handle = mock_file()
    written_content = "".join(call.args[0] for call in handle.write.mock_calls)
    assert written_content == MOCK_JSON_STR


# =====================================================================
# 2. load_metadata() 테스트
# =====================================================================
@patch("database.json_manager.os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data=MOCK_JSON_STR)
def test_load_metadata_success(mock_file, mock_exists):
    """파일이 존재할 때 JSON 파일을 정상적으로 읽어오는지 테스트"""
    # 가짜 환경: 파일이 존재한다고 설정
    mock_exists.return_value = True
    
    # 함수 실행
    result = load_metadata(MOCK_TICKER)
    
    # 검증
    mock_exists.assert_called_once_with(f"{MOCK_TICKER}_meta.json")
    mock_file.assert_called_once_with(f"{MOCK_TICKER}_meta.json", 'r', encoding='utf-8')
    
    # 반환된 결과가 원래 딕셔너리와 정확히 일치하는지 확인
    assert result == MOCK_DATA


@patch("database.json_manager.os.path.exists")
def test_load_metadata_not_found(mock_exists):
    """파일이 존재하지 않을 때 None을 반환하는지 테스트"""
    # 가짜 환경: 파일이 없다고 설정
    mock_exists.return_value = False
    
    # 함수 실행
    result = load_metadata("999999")
    
    # 검증
    mock_exists.assert_called_once_with("999999_meta.json")
    assert result is None

import pytest
from q_learning.q_table import init_q_table, get_state

def test_init_q_table():
    """Q-table 초기화 시 기본 구조가 잘 생성되는지 확인"""
    q_table = init_q_table()
    assert "공격형_IT" in q_table
    assert len(q_table["공격형_IT"]) == 5 # 액션 5개

def test_get_state():
    """성향과 섹터가 합쳐져서 올바른 state 키가 되는지 확인"""
    assert get_state("공격형", "IT") == "공격형_IT"
import os
from q_learning.q_table import save_q_table, load_q_table

def test_save_and_load_q_table_success(monkeypatch, tmp_path):
    """Q-table이 파일로 잘 저장되고 동기화되는지 성공 케이스 테스트"""
    # 프로젝트의 실제 q_table.json을 건드리지 않도록 임시 경로로 격리합니다.
    fake_path = tmp_path / "q_table.json"
    monkeypatch.setattr("q_learning.q_table.Q_TABLE_PATH", str(fake_path))
    
    q_table = init_q_table()
    q_table["공격형_IT"]["0"] = 9.9
    
    # 저장 후 파일이 진짜 생겼는지 확인
    save_q_table(q_table)
    assert os.path.exists(str(fake_path))
    
    # 다시 불러왔을 때 데이터가 유지되는지 확인
    loaded = load_q_table()
    assert loaded["공격형_IT"]["0"] == 9.9

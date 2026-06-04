import pytest
from q_learning.train import run_episode
from q_learning.q_table import init_q_table

def test_run_episode_functionality():
    """에피소드 한 번이 정상적으로 실행되어 Q-table을 반환하는지 테스트"""
    q_table = init_q_table()
    style, sector, reward = "공격형", "IT", 1.0
    
    # 함수 실행
    updated_q = run_episode(q_table, style, sector, reward)
    
    # Q-table이 갱신되어 반환되었는지 확인
    assert updated_q is not None
    assert isinstance(updated_q, dict)
from q_learning.train import train

def test_train_io_cycle(monkeypatch, tmp_path):
    """load-run-save의 전체 흐름이 에러 없이 실행되는지 통합 테스트"""
    fake_path = tmp_path / "q_table.json"
    monkeypatch.setattr("q_learning.q_table.Q_TABLE_PATH", str(fake_path))
    
    # 학습 실행 (파일이 없으면 새로 만들어짐)
    train("중립형", "금융", 0.5)
    
    # 파일이 정상적으로 저장되었는지 확인
    assert fake_path.exists()

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
from unittest.mock import patch
from q_learning.train import train_with_feedback

def test_train_with_feedback_pipeline(monkeypatch, tmp_path):
    """사용자 피드백을 받아 학습까지 이어지는 전체 파이프라인 테스트"""
    fake_path = tmp_path / "q_table.json"
    monkeypatch.setattr("q_learning.q_table.Q_TABLE_PATH", str(fake_path))
    
    # process_feedback은 사용자 입력을 받으므로 5점(Reward 1.0)을 받은 것으로 Mocking
    with patch('q_learning.train.process_feedback', return_value=(5, 1.0)):
        train_with_feedback("안정형", "헬스케어")
        
    assert fake_path.exists()


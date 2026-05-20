import json
import os

STYLES = ["안정형", "중립형", "공격형"]
SECTORS = ["IT", "커뮤니케이션", "금융", "유틸리티",
           "헬스케어", "산업재", "소재", "필수소비재", "임의소비재"]
ACTIONS = [0, 1, 2, 3, 4]
Q_TABLE_PATH = "q_learning/q_table.json"


def init_q_table() -> dict:
    q_table = {}
    for style in STYLES:
        for sector in SECTORS:
            state = f"{style}_{sector}"
            q_table[state] = {str(a): 0.0 for a in ACTIONS}
    return q_table


def save_q_table(q_table: dict):
    with open(Q_TABLE_PATH, "w", encoding="utf-8") as f:
        json.dump(q_table, f, ensure_ascii=False, indent=2)
    print(f"Q-table 저장 완료: {Q_TABLE_PATH}")


def load_q_table() -> dict:
    if os.path.exists(Q_TABLE_PATH):
        with open(Q_TABLE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    print("Q-table 없음. 새로 초기화합니다.")
    return init_q_table()


def get_state(style: str, sector: str) -> str:
    return f"{style}_{sector}"

import json
import os

#state  - (성향 섹터 ) 조합
STYLES = ["안정형","중립형","공격형"]
SECTORS = ["IT","커뮤니케이션","금융","유틸리티","헬스케어","산업재","소재","필수소비재","임의소비재"]

#action = recommendation stock index
ACTIONS = [0,1,2,3,4]

Q_TABLE = {}

def init_q_table() -> dict:
	"""모든 state-action 쌍을 0으로 초기화"""
	q_table = {}
	for style in STYLEX:
	    for sector in SECTORS:
		state = f"{style}_{sector}"
		q_table[state] = {str(a): 0.0 for a in ACTIONS}
	return q_table

def save_q_table(q_table: dict):
	""" Q-table을 Json파일로 저장"""
	with open(Q_TABLE_PATH,"w",encoding ="utf-8") as f:
	     json.dump(q_table,f,ensure_ascii=False,indent=2)
	print(f"Complete:saving Q-table:{Q_TABLE_PATH}")

def load_q_table() -> dict:
	"""저장된 Q-table을 로드 없으면 초기"""
	if os.path.exists(Q_TABLE_PATH):
	    with open(Q_TABLE_PATH,"r",encoding="utf-8") as f:
		return json.load(f)
	print("Q-table 없음 새로 초기화")
	return init_q_table()

def get_state(style:str, sector:str) -> str:
	"""성향 + 섹터 조합으로 state키를 반환 """
	return f"{style}_{sector}"

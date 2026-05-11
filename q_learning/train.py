from q_learning.q_table import load_q_table, save_q_table, get_state
from q_learning.agent import choose_action, update_q_value
from q_learning.state_encoder import encode_state
from q_learning.reward import process_feedback

def run_episode(q_table: dict, style: str, sector: str, reward: float) -> dict:
	"""단일 에피소드 실행 
	   사용자 피드백을 받아 q_table 업데이트 
	"""
	state = get_state(style, sector)
	action = choose_action(q_table,state)
	
	next_state = state
	q_table = update_q_value(q_table,state,action,reward,next_state)
	
	print(f"state:{state} | action: {action} | reward: {reward}"
	return q_table

def train(style: str, sector: str, reward: float)
	"""Q_table 로드 -> 실행 -> 저장"""
	q_table = load_q_table()
	q_table = run_episode(q_table, style, sector, reward)
	save_q_table(q_table)

def train_with_feedback(style: str, sector: str):
    """CLI 피드백 입력 받아 학습 실행"""
    score, reward = process_feedback()
    train(style,sector,reward)
    print(f"학습완료 -> 다음 추천에 반영됩니다.\n")

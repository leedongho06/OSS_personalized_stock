import random
import q_learning.q_table import ACTIONS, get_state

ALPHA = 0.1 # 학습률
GAMMA = 0.9 #할인율
EPSILON= 0.2 #탐색률

def get_best_action(q_table:dict , state:str) -> int:
	"""Q-value가 가장 높은 action을 반환 """
 	return int(max(q_table[state], key=q_table[state].get))

def choose_action(q_table: dict, state:str) -> int:
	if random.random() < EPSILON:
	   return random.choice(ACTIONS) #탐색 
        return get_best_action(q_table,state)

def update_q_value(q_table: dict, state:str, action:int, reward:float, next_state:str) -> dict:
	"""Q-learning 업데이트 공식을 적용 """"
	current_q = q_table[state][str(action)]
	next_max_q = max(q_table[next_state].values())

	new_q = current_q + ALPHA*(reward + GAMMA*next_max_q -current_q)
	q_table[state][str(action)] = round(new_q,4)
	return q_table

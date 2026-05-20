import random
from q_learning.q_table import ACTIONS, get_state

ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.2


def get_best_action(q_table: dict, state: str) -> int:
    return int(max(q_table[state], key=q_table[state].get))


def choose_action(q_table: dict, state: str) -> int:
    if random.random() < EPSILON:
        return random.choice(ACTIONS)
    return get_best_action(q_table, state)


def update_q_value(q_table: dict, state: str, action: int,
                   reward: float, next_state: str) -> dict:
    current_q = q_table[state][str(action)]
    next_max_q = max(q_table[next_state].values())
    new_q = current_q + ALPHA * (reward + GAMMA * next_max_q - current_q)
    q_table[state][str(action)] = round(new_q, 4)
    return q_table

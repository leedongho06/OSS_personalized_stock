from q_learning.q_table import load_q_table, save_q_table
from q_learning.agent import choose_action, update_q_value
from q_learning.state_encoder import encode_state
from q_learning.reward import process_feedback


def run_episode(q_table: dict, style: str, sector: str, reward: float) -> dict:
    state = encode_state(style, sector)
    action = choose_action(q_table, state)
    next_state = state
    q_table = update_q_value(q_table, state, action, reward, next_state)
    print(f"state: {state} | action: {action} | reward: {reward}")
    return q_table


def train(style: str, sector: str, reward: float):
    q_table = load_q_table()
    q_table = run_episode(q_table, style, sector, reward)
    save_q_table(q_table)


def train_with_feedback(style: str, sector: str):
    score, reward = process_feedback()
    train(style, sector, reward)
    print(f"학습 완료 → 다음 추천에 반영됩니다.\n")

from q_learning.q_table import load_q_table, init_q_table, save_q_table
from q_learning.agent import choose_action, get_best_action
from q_learning.state_encoder import encode_state
from q_learning.train import train_with_feedback

def main():
    print("\n[추천 시스템 테스트]\n")

    #테스트용 성향 + 섹터 고정
    style = " 공격형"
    sector = "IT"
    state = encode_state(style,sector)
    #Q-table로드
    q_table = load_q_table()
    print(f"현재 state: {state}")
    print(f"현재 Q값: {q_table[state]}") 
    #최선의 action 출력 
    best = get_best_action(q_table,state)
    print(f"현재 최선 추천 인덱스:{best}") 
    #피드백 받아 확습
    train_with_feedback(style,sector)
    #업데이트 후 값 확인
    q_table = load_q_table()
    print(f"업데이트 후 Q값: {q_table[state]}")

if __name__ == "__main__"
    main()

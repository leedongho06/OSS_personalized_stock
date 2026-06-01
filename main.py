import os
import sqlite3
import pandas as pd
import sys

# 기존 추천 및 뉴스 모듈 임포트
from recommendation.scorer import get_input_companies, infer_style, print_analysis
from recommendation.filter import filter_by_style
from recommendation.recommender import recommend
from q_learning.q_table import load_q_table
from q_learning.agent import choose_action
from q_learning.state_encoder import encode_state
from q_learning.train import train_with_feedback
from news.fetcher import fetch_all_news
from news.classifier import add_sector_to_news
from news.random_picker import pick_random_news
from news.interest_scorer import calculate_interest
from news.style_inferrer import infer_style_from_news
from news.db_manager import init_news_table, save_news, load_news, get_news_count

# ★ feature_datacollector 브랜치에서 완성한 updater 엔진 임포트
from data.updater import run_daily_updater

# 실행 위치에 영향받지 않도록 절대 경로 설정 (data/stock_data.db)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "stock_data.db")


def get_input_method() -> str:
    print("\n[ 투자 성향 파악 방법 선택 ]")
    print("1. 관심 기업 직접 입력")
    print("2. 뉴스 관심도 평가")
    while True:
        choice = input("선택 (1 or 2): ").strip()
        if choice in {"1", "2"}:
            return choice
        print("1 또는 2를 입력해주세요.")


def main():
    print("\n=== OSS Personalized Stock ===\n")

    # ==========================================
    # 0. 데이터 자동 부분 최신화 가동
    # ==========================================
    # 프로그램이 켜지자마자 DB 날짜를 체크하고 누락된 주가 데이터를 FDR로 채워 넣습니다.
    run_daily_updater()

    # 1. 입력 방식 선택 (동호 설계 흐름)
    method = get_input_method()

    if method == "1":
        # 기업 직접 입력
        companies = get_input_companies()
        style, score, analyses = infer_style(companies)
        print_analysis(style, score, analyses)

    else:
        # 뉴스 관심도 평가
        init_news_table()
        print("\n뉴스 데이터 수집 중...")

        if get_news_count() < 30:
            print("API에서 뉴스 수집 중...")
            news = fetch_all_news()
            news = add_sector_to_news(news)
            save_news(news)
        else:
            print("DB에서 뉴스 로드 중...")
            news = load_news(limit=100)

        picked = pick_random_news(news, n=5)

        print("\n[ 뉴스 관심도 평가 ]")
        print("각 뉴스에 별점을 매겨주세요 (1~5점)\n")

        rated = []
        for i, n in enumerate(picked):
            print(f"{i+1}. [{n['sector']}] {n['title']}")
            while True:
                raw = input("별점 (1~5): ").strip()
                if raw in {"1", "2", "3", "4", "5"}:
                    rated.append({
                        "sector": n["sector"],
                        "rating": int(raw)
                    })
                    break
                print("1~5 사이 숫자를 입력해주세요.")

        interest = calculate_interest(rated)
        style, score, analyses = infer_style_from_news(interest)
        print(f"\n추론된 투자 성향: {style} (점수: {score})\n")

    # ==========================================
    # 2. 정적 CSV 대신 최신화된 DB 데이터 로드
    # ==========================================
    print("\n[Data] 추천 알고리즘을 위한 최신 주가 데이터 로드 중...")
    
    db_loaded = False  # DB 데이터 정상 로드 여부 플래그
    df = pd.DataFrame()

    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            
            # per, pbr 컬럼 호출 보장
            query = """
                SELECT ticker, open, high, low, close, volume, per, pbr, date
                FROM daily_prices
            """
            db_df = pd.read_sql_query(query, conn)
            conn.close()
            
            # 추천에 필요한 기업명(name)과 섹터(sector)는 기본 stocks.csv에서 로드
            csv_stocks = pd.read_csv(os.path.join(BASE_DIR, "data", "stocks.csv"))
            
            if 'name' in csv_stocks.columns and 'sector' in csv_stocks.columns:
                # 메타 정보 추출 및 중복 제거
                meta_info = csv_stocks[['ticker', 'name', 'sector']].drop_duplicates()
                
                # 조인을 위해 ticker 타입을 6자리 문자열로 매칭 통일
                db_df['ticker'] = db_df['ticker'].astype(str).str.zfill(6)
                meta_info['ticker'] = meta_info['ticker'].astype(str).str.zfill(6)
                
                # 판다스 merge를 통해 결합
                df = pd.merge(db_df, meta_info, on='ticker', how='inner')
                
                # 시계열 정렬 및 메모리 카피 보장 (SettingWithCopyWarning 방지)
                df = df.sort_values(by=['ticker', 'date']).reset_index(drop=True).copy()
                
                # 동호님 알고리즘에서 요구하는 ma_20(20일 이동평균선) 동적 생성
                df['ma_20'] = df.groupby('ticker')['close'].transform(lambda x: x.rolling(window=20, min_periods=1).mean())
                
                print(f"✅ DB 로드 및 결합 완료: 총 {len(df)}건의 시계열 데이터를 기반으로 추천 알고리즘을 가동합니다.")
                db_loaded = True
            else:
                print("⚠️ CSV 파일에 name 또는 sector 컬럼이 없어 기존 CSV 데이터로 대체합니다.")
                df = csv_stocks

        except Exception as e:
            import traceback
            print(f"❌ DB 로드 실패 구체적 원인:")
            traceback.print_exc()
            print("안전지책으로 기존 CSV 데이터를 사용합니다.")
            df = pd.read_csv(os.path.join(BASE_DIR, "data", "stocks.csv"))
    else:
        print("⚠️ DB 파일이 존재하지 않아 기본 CSV 데이터를 사용합니다.")
        df = pd.read_csv(os.path.join(BASE_DIR, "data", "stocks.csv"))

    # ==========================================
    # 3. 중복 시계열 압축 및 성향 필터링 
    # ==========================================
    print("[Data] 추천 전 종목별 최신 기준일 데이터로 압축 처리 중...")
    if not df.empty and 'date' in df.columns:
        df_latest = df.sort_values('date').groupby('ticker').last().reset_index()
    else:
        df_latest = df

    # 최신 날짜 데이터 셋을 기반으로 성향 필터 가동
    filtered = filter_by_style(df_latest, style)
    
    if filtered.empty:
        print("조건에 맞는 종목이 없어 전체 종목에서 추천합니다.")
        filtered = df_latest

    # ==========================================
    # 4. 코사인 유사도 추천 및 열 맞춤(Table) 출력
    # ==========================================
    result = recommend(filtered, style, top_n=5)
    
    # 추천 점수(score)가 높은 순서대로 내림차순 정렬 후 상위 5개 추출
    if not result.empty and 'score' in result.columns:
        result = result.sort_values(by='score', ascending=False).head(5)
    elif not result.empty:
        result = result.head(5)

    print("\n" + "="*80)
    print(" 🎯 [추천 종목 Top 5] 투자 성향 맞춤 리스트")
    print("="*80)
    
    # 헤더 정렬 방식을 왼쪽 정렬(:<)로 통일하여 왜곡 방지
    print(f" {'No':<4} | {'ticker':<8} | {'name':<14} | {'sector':<14} | {'per':<8} | {'pbr':<7} | {'score':<7}")
    print("-"*80)
    
    if not result.empty:
        # 한글 글자 수만큼 공백을 보정해주는 내부 함수 (터미널 열 맞춤용)
        def pad_korean(text, total_width):
            text_str = str(text)
            korean_count = sum(1 for char in text_str if '\uac00' <= char <= '\ud7a3')
            adjusted_width = max(0, total_width - korean_count)
            return f"{text_str:<{adjusted_width}}"

        # 각 행을 순회하며 열 단위로 자릿수를 맞추어 출력
        for i, (_, row) in enumerate(result.iterrows(), start=1):
            ticker = row.get('ticker', '-')
            name = row.get('name', '-')
            sector = row.get('sector', '-')
            
            # 숫자 데이터 포맷팅 후, 왼쪽 정렬에 맞추어 문자열로 변환
            per = f"{row['per']:.2f}" if pd.notnull(row.get('per')) else "-"
            pbr = f"{row['pbr']:.2f}" if pd.notnull(row.get('pbr')) else "-"
            score = f"{row['score']:.4f}" if pd.notnull(row.get('score')) else "-"
            
            # 한글 문자열 가로폭 보정
            padded_name = pad_korean(name, 14)
            padded_sector = pad_korean(sector, 14)
            
            # 모든 속성을 왼쪽 정렬(:<)로 고정하여 깔끔한 Vertical Alignment 구현
            print(f" [{i}]  | {ticker:<8} | {padded_name} | {padded_sector} | {per:<8} | {pbr:<7} | {score:<7}")
        print("="*80)
    else:
        print(" ⚠️ 데이터 부족으로 추천 종목을 산출할 수 없습니다.")
        print("="*80)
        return

    # ==========================================
    # 5. Q-learning Action 선택 및 학습
    # ==========================================
    try:
        sector = result.iloc[0]["sector"]
        state = encode_state(style, sector)
        q_table = load_q_table()
        action = choose_action(q_table, state)
        
        # 안전장치 가드: 결과 데이터 길이에 유연하게 매칭
        chosen_idx = action % len(result) if len(result) > 0 else 0
        final_stock_name = result.iloc[chosen_idx]['name']
        
        print(f"\nQ-learning 추천 인덱스: {action}")
        print(f"최종 추천 종목: {final_stock_name}\n")

        # 6. 피드백 받아 Q-learning 학습 및 자동 저장
        train_with_feedback(style, sector)
        
    except IndexError:
        print("⚠️ 추천 결과 셋의 인덱스를 참조할 수 없어 Q-learning 단계를 건너뜁니다.")


if __name__ == "__main__":
    main()

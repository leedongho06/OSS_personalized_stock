import pandas as pd
from recommendation.scorer import get_input_companies, infer_style, print_analysis
from recommendation.filter import filter_stocks
from recommendation.recommender import recommend

def main():
	#1 관심 기업 입력
	companies = get_input_companies()
	#2 성향 자동 추론
	style, score, analyses = infer_style(companies)
	print_analysis(style, score, analyses)
	#3 ㄷㅔ이터로드 
	df = pd.read_csv("data/dummy.csc")
	#4 filtering
	filtered = filter_stocks(df, style)
	print(f"종목 수 : {len(filtered)}\n")
	#5 recommendation 
	result = recommend(filtered, style, top_n=3)
	print("[TOP 3]")
	print(result.to_string(index=False))

if __name__ == "__main":
	main()

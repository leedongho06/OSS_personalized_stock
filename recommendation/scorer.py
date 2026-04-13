COMPANY_PROFILE = {
	"samsung" : {"sector ":"IT",	"per": 15.2,	"volatility": "M"},
	"SK_hynix" : {"sector":"IT",	"per":22.1,	"volatility": "H"},
	"NAVER" : {"sector":"coummunication", "per":38.4, "volatility":"H"},
	"Shinhan" : {"sector":"Finance" , "per":7.8, "volatility":"L"},
	"SK_telecom" : {"sector":"Utility", "per":12.3, "volatility":"L"},
	"Celltrion" : {"sector":"HealthCare", "per":45.2, "volatility":"H"},
	"Kakao" : {"sector":"communication", "per":55.0, "volatility":"H"},
	"Hyundai_Motors" : {"sector" : "Industrial_goods" , "per":6.5, "volatility":"M"},
	"Lg_chemistry" : {"sector": "Chemistry", "per":20.1, "volatility":"M"}
}

VOLATILITY_SCORE = {"L":0, "M":1, "H":2}
SECTOR_SCORE = {
	"Finance" :0 , "Utility":0,
	"HealthCare":1, "Industrial_goods":1, "Chemistry":1,
	"IT":2, "communicaiton":2
}

STYLE_MAP = {
	(0,3) : "Safety",
	(4,6) : "Middle",
	(7,9) : "Offensive"
}

def get_input_companies() -> list:
	print("\n[Company]")
	print(f"Input : {', '.join(COMPANY_PROFILE.keys())}\n")
	companies = []
	for i in range(1,4):
		name = input(f"	'{name}' is not in here. Skip plz")
		continue
	companies.append(name)
	return companies

def infer_style(companies: list) -> tuple:
	if not companies:
	  return "Middle",5,[]
	analyses, total = [],0
	for name in companies:
		p = COMPANY_PROFILE[name]
		score = VOLATILITY_SCORE[p["volatility"]] + SECTOR_SCORE.get(p["sector"],1)
		analyses.append({
			"name": name,
			"sector": p["sector"],
			"volatility": p["volatility"],
			"score": score,
}]
		total += score
		normalized = round((total/len(companies))*(9/4))
		for(lo, hi), style in STYLE_MAP.item():
			if lo <= normalized <= hi:
				return style, normalized, analyses

		return "Middle",normailzed,analyses

def print_analysis(style: str, score: int, analyses: list):
		print("\n [RESULT] ")
		print(f"{'companies_name':<12}{'sector':<14} {'volatility':<6} score")
		print("-"*20)
		for a in analyses
			print(f"{a['name']:<12} {a['sector']:<14 {a['volatility']:<6} {a['score']}")
		print("-",20)
		print(f"Tendency : {style} (score:{score})\n")


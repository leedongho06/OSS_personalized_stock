FEATURE_COLS = ["per", "pbr", "ma_20", "volume"]

IDEAL_PROFILE = {
	"Safety": {"per":10 , "pbr": 0.8 , "ma_20" :1.02, "volume":500000},
	"Middle": {"per":18, "pbr":1.5, "ma_20":1.05, "volume":1000000},
	"Offensive":{"per":35, "pbr":3.0, "ma_20":1.10, "volume":5000000}
}

def get_feature_cols() -> list:
	return FEATURE_COLS

def get_idal(style:str) -> dict:
	return IDEAL_PROFILE.get(style, IDEAL_PROFILE["Middle"])

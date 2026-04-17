import numpy as np

class StateEncoder:
    def __init__(self):
    # 섹터 숫자 매핑
    self.sector = {
        "에너지": 0,
        "소재": 1,
        "산업재": 2,
        "임의소비재": 3,
        "필수소비재": 4,
        "헬스케어": 5,
        "금융": 6,
        "IT": 7,
        "통신": 8,
        "유틸리티": 9,
        "부동산": 10
    }

    def encode(self, stock_data, user_profile):
    """
    주식 정보 및 사용자 성향 리스트로 합치기
    :param stock_data: 주식 정보
    :param user_profile: 사용자 성향
    :return: 정규화된 리스트
    :rtype: numpy array
    """
    price_change = stock_data.get('price_change', 0.0)
    sector_index = self.sector.get(stock_data.get('sector'), 0)
    norm_sector = sector_index / len(self.sector)
    
    risk = user_profile.get('risk', 0.5)

    state_vector = np.array([price_change, norm_sector, risk], dtype = float)

    return state_vector

if __name__ == "__main__":
    encoder = StateEncoder()
    sample_stock = {'price_change': 0.05, 'sector': 'IT'}
    sample_user = {'risk': 0.9}

    encoded_state = encoder.encode(sample_stock, sample_user)
    print(f"Encoded State Vector: {encoded_state}")

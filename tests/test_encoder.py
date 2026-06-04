import pytest
from q_learning.state_encoder import encode_state, decode_state

def test_encode_decode_integrity():
    """인코딩 후 디코딩했을 때 원래 값이 그대로 나오는지 무결성 테스트"""
    style, sector = "안정형", "IT"
    encoded = encode_state(style, sector)
    decoded_style, decoded_sector = decode_state(encoded)
    
    assert decoded_style == style
    assert decoded_sector == sector
def test_encode_invalid_input():
    """정의되지 않은 style이나 sector 입력 시 ValueError 예외 처리 검증"""
    with pytest.raises(ValueError):
        encode_state("슈퍼공격형", "IT")  # 잘못된 스타일
    with pytest.raises(ValueError):
        encode_state("안정형", "우주항공") # 잘못된 섹터

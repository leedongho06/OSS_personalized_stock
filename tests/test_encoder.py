import pytest
from q_learning.state_encoder import encode_state, decode_state

def test_encode_decode_integrity():
    """인코딩 후 디코딩했을 때 원래 값이 그대로 나오는지 무결성 테스트"""
    style, sector = "안정형", "IT"
    encoded = encode_state(style, sector)
    decoded_style, decoded_sector = decode_state(encoded)
    
    assert decoded_style == style
    assert decoded_sector == sector

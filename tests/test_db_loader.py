import pytest
import pandas as pd
from data.data_loader import load_data_from_db

def test_load_data_no_db_file():
    """시나리오 1: 데이터베이스 파일이 없을 때 빈 DataFrame 반환 확인"""
    df = load_data_from_db("non_existent.db")
    assert df.empty == True

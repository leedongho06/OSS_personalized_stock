import json
import os

PROFILE_FILE = 'user_profile.json'

def load_profile() -> dict:
    """JSON 파일에서 사용자 프로파일을 불러옵니다."""
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_profile(data: dict) -> None:
    """사용자 프로파일을 JSON 파일로 저장합니다."""
    with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


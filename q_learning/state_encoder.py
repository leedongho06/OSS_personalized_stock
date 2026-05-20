STYLES = ["안정형", "중립형", "공격형"]
SECTORS = [
    "IT", "커뮤니케이션", "금융", "유틸리티",
    "헬스케어", "산업재", "소재", "필수소비재", "임의소비재"
]


def encode_state(style: str, sector: str) -> str:
    if style not in STYLES:
        raise ValueError(f"유효하지 않은 성향: {style}")
    if sector not in SECTORS:
        raise ValueError(f"유효하지 않은 섹터: {sector}")
    return f"{style}_{sector}"


def decode_state(state: str) -> tuple:
    parts = state.split("_", 1)
    if len(parts) != 2:
        raise ValueError(f"유효하지 않은 state: {state}")
    return parts[0], parts[1]


def get_all_states() -> list:
    return [f"{s}_{sec}" for s in STYLES for sec in SECTORS]

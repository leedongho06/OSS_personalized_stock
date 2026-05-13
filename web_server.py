from flask import Flask, jsonify

app = Flask(__name__)

# 1. 기본 접속 확인용 화면
@app.route('/')
def home():
    return "DB 연결 없이 단독으로 실행되는 백엔드 서버입니다!"

# 2. 프론트엔드가 주가 데이터를 요청할 때 사용할 주소(API)
@app.route('/api/stock/<ticker>', methods=['GET'])
def get_stock_data(ticker):
    
    # DB에 연결하는 대신, 서버 코드 안에서 직접 가짜 데이터를 만들어줍니다.
    dummy_data = [
        {"date": "2026-04-15", "open": 70000, "high": 72000, "low": 69000, "close": 71000, "volume": 1000000},
        {"date": "2026-04-16", "open": 71000, "high": 73000, "low": 70000, "close": 72000, "volume": 1100000},
        {"date": "2026-04-17", "open": 72000, "high": 74000, "low": 71000, "close": 73000, "volume": 1200000}
    ]
    
    # 요청 들어온 종목 코드가 삼성전자(005930)일 때만 가짜 데이터 전송
    if ticker == '005930':
        return jsonify(dummy_data)
    else:
        return jsonify({"error": "해당 종목의 데이터가 없습니다."}), 404

if __name__ == '__main__':
    # 서버 가동
    app.run(host='0.0.0.0', port=5000, debug=True)

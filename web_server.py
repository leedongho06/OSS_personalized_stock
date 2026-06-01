from flask import Flask, jsonify
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.db_manager import get_daily_prices, get_user

app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 질문자님의 완벽한 DB가 연동된 강력한 백엔드 서버입니다!"

@app.route('/api/stock/<ticker>', methods=['GET'])
def get_stock_data(ticker):
    try:
        df = get_daily_prices(ticker)
        if df.empty:
            return jsonify({"error": f"[{ticker}] 종목의 데이터가 DB에 없습니다."}), 404
        real_data = df.to_dict(orient='records')
        return jsonify(real_data)
    except Exception as e:
        return jsonify({"error": f"서버 내부 에러 발생: {str(e)}"}), 500

@app.route('/api/user/<user_id>', methods=['GET'])
def get_user_info(user_id):
    try:
        user_data = get_user(user_id)
        if user_data:
            result = {
                "user_id": user_data,
                "username": user_data,
                "investment_type": user_data
            }
            return jsonify(result)
        else:
            return jsonify({"error": "해당 사용자를 찾을 수 없습니다."}), 404
            
    except Exception as e:
        return jsonify({"error": f"서버 내부 에러 발생: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

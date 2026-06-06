import unittest
from unittest.mock import patch, MagicMock
import os
import importlib
import news.classifier as cl

class TestNewsClassifier(unittest.TestCase):
    def setUp(self):
        self.original_key = cl.GEMINI_API_KEY
        cl.GEMINI_API_KEY = "fake_test_key"

    def tearDown(self):
        cl.GEMINI_API_KEY = self.original_key

    def test_classify_sector_no_api_key(self):
        cl.GEMINI_API_KEY = ""
        result = cl.classify_sector("삼성전자 실적 발표", "반도체 이익 증가")
        self.assertEqual(result, "기타")

    @patch('news.classifier.genai')
    def test_classify_sector_success(self, mock_genai):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "IT" 
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = cl.classify_sector("반도체 호황", "SK하이닉스 주가 상승")
        self.assertEqual(result, "IT")

    @patch('news.classifier.genai')
    def test_classify_sector_extraction(self, mock_genai):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "이 뉴스는 금융 카테고리에 해당합니다."
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = cl.classify_sector("금리 인상 소식", "은행권 긴장")
        self.assertEqual(result, "금융")

    @patch('news.classifier.genai')
    def test_classify_sector_api_error(self, mock_genai):
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API 에러")
        mock_genai.GenerativeModel.return_value = mock_model

        result = cl.classify_sector("테스트 뉴스", "테스트 내용")
        self.assertEqual(result, "기타")

    @patch('news.classifier.classify_sector')
    def test_add_sector_to_news(self, mock_classify):
        mock_classify.return_value = "헬스케어"
        dummy_news = [{"title": "<b>셀트리온</b>", "description": "바이오", "link": ""}]
        result = cl.add_sector_to_news(dummy_news)
        self.assertEqual(result[0]["title"], "셀트리온")
        self.assertEqual(result[0]["sector"], "헬스케어")

    # ==============================================================================
    # 💡 [새로 추가된 핵심 코드] 8번 줄 및 60번 줄 완벽 저격!
    # ==============================================================================

    @patch('news.classifier.genai')
    def test_classify_sector_unknown_response(self, mock_genai):
        """60번 줄 커버: 제미나이가 카테고리에 없는 엉뚱한 대답을 했을 때의 Fallback 처리"""
        mock_model = MagicMock()
        mock_response = MagicMock()
        # SECTORS 리스트에 없는 완전히 엉뚱한 텍스트 반환
        mock_response.text = "알수없음" 
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = cl.classify_sector("외계인 침공", "지구 멸망 위기")
        self.assertEqual(result, "기타") # 60번 줄의 return "기타"를 타게 됨!

    def test_global_api_key_configure(self):
        """8번 줄 커버: 프로그램 시작(import) 시점에 환경변수가 있을 때의 설정 로직"""
        # 환경변수를 강제로 세팅하고 모듈을 재시동(reload)하여 8번 줄을 타게 만듭니다.
        os.environ["GEMINI_API_KEY"] = "test_key"
        importlib.reload(cl)
        
        # 테스트 완료 후 원상복구 (다른 테스트에 영향이 가지 않도록)
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        importlib.reload(cl)

if __name__ == '__main__':
    unittest.main()

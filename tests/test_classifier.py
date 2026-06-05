import unittest
from unittest.mock import patch, MagicMock
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

    # 💡 수정된 부분: GenerativeModel 대신 genai 모듈 전체를 가로챕니다!
    @patch('news.classifier.genai')
    def test_classify_sector_success(self, mock_genai):
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "IT" 
        mock_model.generate_content.return_value = mock_response
        # genai.GenerativeModel()이 호출되면 우리의 mock_model을 주도록 설정
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

if __name__ == '__main__':
    unittest.main()

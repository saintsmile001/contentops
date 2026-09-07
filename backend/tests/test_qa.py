import asyncio
import unittest
from app.ai.client import AIClient
from app.core.config import Settings
from app.schemas.qa import QAReport
class QATests(unittest.TestCase):
 def test_mock_qa_has_valid_scores_and_status(self):
  qa=asyncio.run(AIClient(Settings(ai_mock_mode=True)).generate_structured('i','context',QAReport))
  self.assertEqual(qa.status,'PASS'); self.assertTrue(0<=qa.faithfulness_score<=100)

import asyncio
import unittest
from app.ai.client import AIClient
from app.core.config import Settings
from app.schemas.campaign import CampaignCreateRequest, CampaignStrategy

class CampaignTests(unittest.TestCase):
 def test_mock_strategy_has_seven_days(self):
  strategy=asyncio.run(AIClient(Settings(ai_mock_mode=True)).generate_structured('instructions','dna',CampaignStrategy))
  self.assertEqual(len(strategy.days),7)
  self.assertEqual([day.day for day in strategy.days],list(range(1,8)))
 def test_campaign_requires_seven_days(self):
  request=CampaignCreateRequest(source_id='source',name='Campaign')
  self.assertEqual(request.duration,7)
 def test_mock_strategy_uses_threads_when_selected(self):
  strategy=asyncio.run(AIClient(Settings(ai_mock_mode=True)).generate_structured('instructions',"{'platforms': ['threads']}",CampaignStrategy))
  self.assertEqual({day.platform for day in strategy.days},{'threads'})

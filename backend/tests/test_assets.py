import asyncio
import unittest
from app.ai.client import AIClient
from app.core.config import Settings
from app.schemas.asset import SEOAsset, SocialAsset
from app.schemas.asset import AssetUpdateRequest, RegenerateRequest
class AssetTests(unittest.TestCase):
 def test_mock_social_asset_is_valid(self):
  asset=asyncio.run(AIClient(Settings(ai_mock_mode=True)).generate_structured('i',"{'platform': 'instagram'}",SocialAsset)); self.assertEqual(asset.platform,'instagram')
 def test_mock_seo_asset_is_valid(self):
  seo=asyncio.run(AIClient(Settings(ai_mock_mode=True)).generate_structured('i','dna',SEOAsset)); self.assertTrue(seo.url_slug)
 def test_asset_edit_and_regeneration_instruction_validate(self):
  update=AssetUpdateRequest(title="Title",content="Body")
  self.assertEqual(update.title,"Title")
  self.assertEqual(RegenerateRequest(instruction="Make it shorter.").instruction,"Make it shorter.")

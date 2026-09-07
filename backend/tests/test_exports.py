import unittest
from app.services.export_service import campaign_csv, campaign_json, campaign_markdown

class ExportTests(unittest.TestCase):
 def setUp(self):
  self.campaign={"name":"Campaign"}; self.strategy={"days":[{"day":1}]}; self.assets=[{"platform":"linkedin","content_type":"post","title":"Title","content":"Body","cta":"CTA","status":"READY","scheduled_for":None}]
 def test_json_export_contains_campaign(self): self.assertIn('Campaign',campaign_json(self.campaign,self.strategy,self.assets))
 def test_markdown_export_contains_asset(self): self.assertIn('# Campaign',campaign_markdown(self.campaign,self.strategy,self.assets))
 def test_csv_export_has_header(self): self.assertTrue(campaign_csv(self.strategy,self.assets).startswith('day,platform'))

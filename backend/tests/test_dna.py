import asyncio
import unittest

from app.ai.client import AIClient
from app.core.config import Settings
from app.schemas.dna import ContentDNA

class DNATests(unittest.TestCase):
    def test_mock_analysis_returns_valid_content_dna(self) -> None:
        client = AIClient(Settings(ai_mock_mode=True))
        dna = asyncio.run(client.generate_structured('instructions', 'Creators can reduce repetitive work. They should review every output.', ContentDNA))
        self.assertIsInstance(dna, ContentDNA)
        self.assertTrue(dna.main_thesis)
        self.assertEqual(dna.statistics, [])

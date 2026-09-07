import asyncio
import unittest

from app.api.routes.health import health
from app.core.config import Settings


class HealthTests(unittest.TestCase):
    def test_health_reports_ok_when_database_is_not_configured(self) -> None:
        response = asyncio.run(health(Settings()))
        self.assertEqual(response["data"]["status"], "ok")
        self.assertEqual(response["data"]["database"], "not_configured")
        self.assertIsNone(response["error"])

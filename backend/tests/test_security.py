import asyncio
import unittest
from time import monotonic

from app.core.config import Settings
from app.core.exceptions import AppError
from app.core.security import AuthenticatedUser, _verified_tokens, get_current_user


class SecurityTests(unittest.TestCase):
    def test_missing_bearer_token_is_rejected(self) -> None:
        with self.assertRaises(AppError) as error:
            asyncio.run(get_current_user(None, Settings()))
        self.assertEqual(error.exception.status_code, 401)
        self.assertEqual(error.exception.code, "UNAUTHENTICATED")

    def test_recently_verified_token_skips_network_check(self) -> None:
        _verified_tokens["cached-token"] = (AuthenticatedUser(id="user-1"), monotonic() + 60)
        user = asyncio.run(get_current_user("Bearer cached-token", Settings()))
        self.assertEqual(user.id, "user-1")

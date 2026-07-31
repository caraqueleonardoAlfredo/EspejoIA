import os
import unittest
from unittest.mock import patch

from presence_timeout import (
    DEFAULT_SCREEN_OFF_DELAY_SECONDS,
    PresenceTimeout,
    get_screen_off_delay_seconds,
)


class PresenceTimeoutTests(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    def test_default_delay_is_thirty_minutes(self):
        self.assertEqual(
            get_screen_off_delay_seconds(),
            DEFAULT_SCREEN_OFF_DELAY_SECONDS,
        )
        self.assertEqual(DEFAULT_SCREEN_OFF_DELAY_SECONDS, 1800.0)

    @patch.dict(os.environ, {"SCREEN_OFF_DELAY_SECONDS": "90"}, clear=True)
    def test_delay_is_configurable(self):
        self.assertEqual(get_screen_off_delay_seconds(), 90.0)

    def test_momentary_presence_loss_does_not_expire(self):
        timeout = PresenceTimeout(delay_seconds=1800)
        timeout.detected(now=100)

        self.assertFalse(timeout.has_expired(now=101))
        self.assertFalse(timeout.has_expired(now=1899))
        self.assertTrue(timeout.has_expired(now=1900))

    def test_new_detection_restarts_delay(self):
        timeout = PresenceTimeout(delay_seconds=1800)
        timeout.detected(now=100)
        timeout.detected(now=1000)

        self.assertFalse(timeout.has_expired(now=2799))
        self.assertTrue(timeout.has_expired(now=2800))

    @patch.dict(os.environ, {"SCREEN_OFF_DELAY_SECONDS": "invalid"}, clear=True)
    def test_invalid_delay_uses_default(self):
        self.assertEqual(
            get_screen_off_delay_seconds(),
            DEFAULT_SCREEN_OFF_DELAY_SECONDS,
        )


if __name__ == "__main__":
    unittest.main()

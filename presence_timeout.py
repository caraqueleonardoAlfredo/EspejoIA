import os

from dotenv import load_dotenv


DEFAULT_SCREEN_OFF_DELAY_SECONDS = 1800.0
load_dotenv()


def get_screen_off_delay_seconds() -> float:
    raw_value = os.getenv("SCREEN_OFF_DELAY_SECONDS", "").strip()

    if not raw_value:
        return DEFAULT_SCREEN_OFF_DELAY_SECONDS

    try:
        delay = float(raw_value)
    except ValueError:
        return DEFAULT_SCREEN_OFF_DELAY_SECONDS

    return delay if delay > 0 else DEFAULT_SCREEN_OFF_DELAY_SECONDS


class PresenceTimeout:
    def __init__(self, delay_seconds: float):
        self.delay_seconds = delay_seconds
        self.last_detection_at = None

    def detected(self, now: float) -> None:
        self.last_detection_at = now

    def has_expired(self, now: float) -> bool:
        if self.last_detection_at is None:
            return False

        return now - self.last_detection_at >= self.delay_seconds

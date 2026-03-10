import orjson
from redis import Redis

from app.config.config import settings


class OtpService:
    def __init__(self):
        self.redis_client = Redis.from_url(settings.REDIS_URL)

    def _get_registration_key(self, phone: str) -> str:
        return f"registration:{phone}"

    def save_user_before_registration(self, phone: str, user_data: dict, expire_time=300):
        _key = self._get_registration_key(phone)
        self.redis_client.set(_key, orjson.dumps(user_data), ex=expire_time)
        return True

    def _get_otp_phone_key(self, phone: str) -> str:
        return f"send_otp_phone:{phone}"

    def send_otp_by_phone(self, phone: str, code: int, expire_time=120) -> tuple[bool, int]:
        _key = self._get_otp_phone_key(phone)
        _ttl = self.redis_client.ttl(_key)
        if _ttl > 0:
            return False, _ttl

        self.redis_client.set(_key, code, expire_time)

        print(f"[TEST SMS] phone={phone}, code={code}")

        return True, 0

    def verify_otp_by_phone(self, phone: str, code: int) -> bool:
        _key = self._get_otp_phone_key(phone)
        saved_code = self.redis_client.get(_key)
        if saved_code is None:
            return False
        return str(saved_code.decode()) == str(code)

    def get_user_before_registration(self, phone: str) -> dict | None:
        _key = self._get_registration_key(phone)
        data = self.redis_client.get(_key)
        if not data:
            return None
        return orjson.loads(data)

    def delete_user_before_registration(self, phone: str):
        _key = self._get_registration_key(phone)
        self.redis_client.delete(_key)

import orjson
from redis import Redis

from app.config.config import settings


class OtpService:
    def __init__(self):
        self.redis_client = Redis.from_url(settings.REDIS_URL)

    def _get_registration_key(self, phone: str) -> str:
        return f"registration:{phone}"

    def _get_password_reset_key(self, phone: str) -> str:
        return f"password-reset:{phone}"

    def _get_otp_phone_key(self, phone: str, purpose: str) -> str:
        return f"otp:{purpose}:{phone}"

    def _get_otp_cooldown_key(self, phone: str, purpose: str) -> str:
        return f"otp-cooldown:{purpose}:{phone}"

    def _get_otp_attempts_key(self, phone: str, purpose: str) -> str:
        return f"otp-attempts:{purpose}:{phone}"

    def _get_refresh_token_key(self, user_id: str, jti: str) -> str:
        return f"refresh-token:{user_id}:{jti}"

    def save_user_before_registration(
        self,
        phone: str,
        user_data: dict,
        expire_time: int = settings.REGISTRATION_DATA_EXPIRE_SECONDS,
    ):
        _key = self._get_registration_key(phone)
        self.redis_client.set(_key, orjson.dumps(user_data), ex=expire_time)
        return True

    def save_password_reset_request(
        self,
        phone: str,
        payload: dict,
        expire_time: int = settings.PASSWORD_RESET_DATA_EXPIRE_SECONDS,
    ):
        _key = self._get_password_reset_key(phone)
        self.redis_client.set(_key, orjson.dumps(payload), ex=expire_time)
        return True

    def send_otp_by_phone(
        self,
        phone: str,
        code: int,
        purpose: str,
        expire_time: int = settings.OTP_EXPIRE_SECONDS,
        resend_time: int = settings.OTP_RESEND_SECONDS,
    ) -> tuple[bool, int]:
        _cooldown_key = self._get_otp_cooldown_key(phone, purpose)
        _ttl = self.redis_client.ttl(_cooldown_key)
        if _ttl > 0:
            return False, _ttl

        _otp_key = self._get_otp_phone_key(phone, purpose)
        _attempts_key = self._get_otp_attempts_key(phone, purpose)
        self.redis_client.set(_otp_key, code, ex=expire_time)
        self.redis_client.set(_cooldown_key, "1", ex=resend_time)
        self.redis_client.delete(_attempts_key)

        print(f"[TEST SMS] purpose={purpose} phone={phone}, code={code}")

        return True, 0

    def verify_otp_by_phone(self, phone: str, code: int, purpose: str) -> tuple[bool, str]:
        _key = self._get_otp_phone_key(phone, purpose)
        _attempts_key = self._get_otp_attempts_key(phone, purpose)
        saved_code = self.redis_client.get(_key)
        if saved_code is None:
            return False, "Invalid or expired OTP"

        if str(saved_code.decode()) == str(code):
            self.redis_client.delete(_key)
            self.redis_client.delete(_attempts_key)
            return True, "OTP verified"

        attempts = self.redis_client.incr(_attempts_key)
        self.redis_client.expire(_attempts_key, settings.OTP_EXPIRE_SECONDS)
        if attempts >= settings.OTP_MAX_ATTEMPTS:
            self.redis_client.delete(_key)
            self.redis_client.delete(_attempts_key)
            return False, "OTP attempts exceeded. Request a new code."
        return False, "Invalid OTP"

    def get_user_before_registration(self, phone: str) -> dict | None:
        _key = self._get_registration_key(phone)
        data = self.redis_client.get(_key)
        if not data:
            return None
        return orjson.loads(data)

    def get_password_reset_request(self, phone: str) -> dict | None:
        _key = self._get_password_reset_key(phone)
        data = self.redis_client.get(_key)
        if not data:
            return None
        return orjson.loads(data)

    def delete_user_before_registration(self, phone: str):
        _key = self._get_registration_key(phone)
        self.redis_client.delete(_key)

    def delete_password_reset_request(self, phone: str):
        _key = self._get_password_reset_key(phone)
        self.redis_client.delete(_key)

    def store_refresh_token(self, user_id: str, jti: str, expire_seconds: int):
        _key = self._get_refresh_token_key(user_id, jti)
        self.redis_client.set(_key, "1", ex=expire_seconds)

    def is_refresh_token_active(self, user_id: str, jti: str) -> bool:
        _key = self._get_refresh_token_key(user_id, jti)
        return self.redis_client.exists(_key) == 1

    def revoke_refresh_token(self, user_id: str, jti: str):
        _key = self._get_refresh_token_key(user_id, jti)
        self.redis_client.delete(_key)

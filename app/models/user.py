import enum

from passlib.context import CryptContext
from sqlalchemy import String, Enum, select
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import Model, db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Model):
    class Role(enum.Enum):
        ADMIN = 'ADMIN'
        USER = 'USER'

    firstname: Mapped[str] = mapped_column(String(255))
    lastname: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(255), unique=True)
    role: Mapped[str] = mapped_column(Enum(Role, name='role'), default=Role.USER)
    # TODO specialist
    # email: Mapped[EmailStr] = mapped_column(String(150), nullable=True, unique=True)
    password: Mapped[str] = mapped_column(String(500), nullable=True)

    # specialty: Mapped[DoctorSpeciality] = mapped_column(Enum(DoctorSpeciality, name="doctorspeciality"),
    #                                                     nullable=True)

    # TODO M2M doctor <-> clinics
    @classmethod
    async def get_by_phone(cls, phone_number: str):
        result = await db.execute(select(cls).where(cls.phone_number == phone_number))
        return result.scalar_one_or_none()

    @property
    def is_admin(self):
        return self.role == User.Role.ADMIN

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

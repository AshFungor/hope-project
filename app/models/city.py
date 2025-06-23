from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.database import Datetime, Ints, ModelBase, VarStrings


class City(ModelBase):
    __tablename__ = "city"

    id: Mapped[Ints.Serial]
    # mayor could be null, since user depends on city, and city must be created first
    mayor_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"), nullable=True)
    prefecture_id: Mapped[Ints.Long] = mapped_column(ForeignKey("prefecture.id"), nullable=True)
    bank_account_id: Mapped[Ints.Long] = mapped_column(ForeignKey("bank_account.id"))
    name: Mapped[VarStrings.Char64]
    location: Mapped[VarStrings.Char64]

    mayor = relationship("User", foreign_keys=mayor_id)
    prefecture = relationship("Prefecture", back_populates="cities")
    users = relationship("User", foreign_keys="User.city_id", back_populates="city")

    def __init__(
        self,
        name: str,
        mayor_id: int | None,
        prefecture_id: int | None,
        bank_account_id: int | None,
        location: str,
    ):
        self.mayor_id = mayor_id
        self.prefecture_id = prefecture_id
        self.bank_account_id = bank_account_id
        self.name = name
        self.location = location


class Office(ModelBase):
    __tablename__ = "office"

    id: Mapped[Ints.Serial]
    city_id: Mapped[Ints.Long] = mapped_column(ForeignKey("city.id"))
    company_id: Mapped[Ints.Long] = mapped_column(ForeignKey("company.id"))
    founded_at: Mapped[Datetime.Datetime]  # type: ignore
    dismissed_at: Mapped[Datetime.DatetimeEmpty]  # type: ignore

    city = relationship("City", foreign_keys=city_id)
    company = relationship("Company", foreign_keys=company_id)


class Prefecture(ModelBase):
    __tablename__ = "prefecture"

    id: Mapped[Ints.Serial]
    name: Mapped[VarStrings.Char64] = mapped_column(nullable=True)
    bank_account_id: Mapped[Ints.Long] = mapped_column(ForeignKey("bank_account.id"))
    prefect_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"), nullable=True)
    economic_assistant_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"), nullable=True)
    social_assistant_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"), nullable=True)

    prefect = relationship("User", foreign_keys=prefect_id)
    economic_assistant = relationship("User", foreign_keys=economic_assistant_id)
    social_assistant = relationship("User", foreign_keys=social_assistant_id)
    cities = relationship("City", back_populates="prefecture")
    infrastructures = relationship("Infrastructure")

    def __init__(
        self,
        name: str,
        bank_account_id: int | None,
        prefect_id: int | None,
        economic_assistant_id: int | None,
        social_assistant_id: int | None,
    ):
        self.bank_account_id = bank_account_id
        self.prefect_id = prefect_id
        self.economic_assistant_id = economic_assistant_id
        self.social_assistant_id = social_assistant_id
        self.name = name


class CityHall(ModelBase):
    __tablename__ = "city_hall"

    id: Mapped[Ints.Serial]
    bank_account_id: Mapped[Ints.Long] = mapped_column(ForeignKey("bank_account.id"))
    mayor_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"))
    economic_assistant_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"))
    social_assistant_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"))


class Infrastructure(ModelBase):
    __tablename__ = "infrastructure"

    id: Mapped[Ints.Serial]
    prefecture_id: Mapped[Ints.Long] = mapped_column(ForeignKey("prefecture.id"))
    name: Mapped[VarStrings.Char64]

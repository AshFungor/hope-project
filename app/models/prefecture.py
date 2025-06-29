from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import User
from app.models.types import Ints, ModelBase, VarStrings


class Prefecture(ModelBase):
    __tablename__ = "prefecture"

    id: Mapped[Ints.Serial]
    name: Mapped[VarStrings.Char64] = mapped_column(nullable=True)
    bank_account_id: Mapped[Ints.Long] = mapped_column(ForeignKey("bank_account.id"))
    prefect_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"), nullable=True)
    economic_assistant_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"), nullable=True)
    social_assistant_id: Mapped[Ints.Long] = mapped_column(ForeignKey("users.id"), nullable=True)

    users = relationship("User", back_populates="prefecture", foreign_keys=User.prefecture_id)
    prefect = relationship("User", foreign_keys=prefect_id)
    economic_assistant = relationship("User", foreign_keys=economic_assistant_id)
    social_assistant = relationship("User", foreign_keys=social_assistant_id)

    def __init__(
        self,
        name: str,
        bank_account_id: int,
        prefect_id: Optional[int] = None,
        economic_assistant_id: Optional[int] = None,
        social_assistant_id: Optional[int] = None,
    ):
        self.bank_account_id = bank_account_id
        self.prefect_id = prefect_id
        self.economic_assistant_id = economic_assistant_id
        self.social_assistant_id = social_assistant_id
        self.name = name

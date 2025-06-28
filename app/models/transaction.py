import datetime
import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.types import Datetime, Ints, ModelBase, VarStrings


class TransactionStatus(enum.StrEnum):
    CREATED = "created"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Transaction(ModelBase):
    __tablename__ = "transaction"

    id: Mapped[Ints.Serial]
    product_id: Mapped[Ints.Long] = mapped_column(ForeignKey("product.id"))
    customer_bank_account_id: Mapped[Ints.Long] = mapped_column(ForeignKey("bank_account.id"))
    seller_bank_account_id: Mapped[Ints.Long] = mapped_column(ForeignKey("bank_account.id"))
    count: Mapped[Ints.Long]
    amount: Mapped[Ints.Long]
    status: Mapped[VarStrings.Char32]
    created_at: Mapped[Datetime.Datetime]
    updated_at: Mapped[Datetime.Datetime] = mapped_column(nullable=True)
    comment: Mapped[VarStrings.Char256] = mapped_column(nullable=True)

    def __init__(
        self,
        product_id: int,  # target product for transaction
        customer_bank_account_id: int,  # customer's account
        seller_bank_account_id: int,  # seller's account
        count: int,  # number of products
        amount: int,  # money
        status: str | TransactionStatus,  # transaction status
        created_at: datetime.datetime,  # creation time
        updated_at: datetime.datetime,  # ???
        comment: str | None,  # our data
    ) -> None:
        self.product_id = product_id
        self.customer_bank_account_id = customer_bank_account_id
        self.seller_bank_account_id = seller_bank_account_id
        self.count = count
        self.amount = amount
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.comment = self.__generate_comment(comment)

    def __generate_comment(self, additional_message: str | None) -> None:
        if additional_message is None:
            return ""
        return f"transaction comment {additional_message}"

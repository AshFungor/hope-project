import hashlib
import uuid

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey

from app.modules.database.handlers import serial
from app.modules.database.handlers import long_int
from app.modules.database.handlers import ModelBase

import app.modules.database.validators as validators


class BankAccount(ModelBase):
    __tablename__ = 'bank_account'

    id: Mapped[long_int] = mapped_column(primary_key=True)

    def __init__(self, id: int | None = None, generator: callable = None, **kwargs: dict[str, object]) -> None:
        if id is None:
            if generator is None:
                generator = BankAccount._generator
            self.id = generator(**kwargs)
        else:
            self.id = id

    @staticmethod
    def make_spec(
        type: str | None = None,
        object: object | None = None
    ) -> dict[str, object]:
        return {
            'type': type,
            'spec': object
        }

    @staticmethod
    def _generator(**kwargs: dict[str, object]) -> int:
        # first digit is type
        resulting = ''
        if 'type' in kwargs:
            supported = {
                'user': 5, 
                'company': 4,
                'city': 3,
                'prefecture': 2, 
                'city-hall': 1
            }
            resulting += str(supported.get(kwargs['type'], 0))
        # 11 allowed digits
        if 'spec' in kwargs:
            return int(resulting + BankAccount._hash_and_squash({'main': kwargs['spec'], 'salt': uuid.uuid4()}, 4))
        raise ValueError(f'no spec given in kwargs: {kwargs}')
    
    @staticmethod
    def _hash_and_squash(obj: object, l: int) -> str:
        hexed = str(int(hashlib.sha3_256(repr(obj).encode()).hexdigest(), base=16))

        # squash to size l
        if len(hexed) > l:
            diff = len(hexed) - l
            cut, hexed = hexed[l:], hexed[:l]
            # ensure difference is divisible of 8
            while len(cut) % 4 != 0:
                cut += '0'
            # xor each excessive block with the rest
            hexed = int(hexed)
            for curr in range(4, len(cut), 4):
                block = cut[curr - 4:curr]
                for i in range(l // 4):
                    hexed = hexed ^ (int(block) << (i * 8))
            # ensure still have l digits
            hexed = '0' * max(l - len(str(hexed)), 0) + str(hexed)
        return hexed
        

class Product2BankAccount(ModelBase):
    __tablename__ = 'product_to_bank_account'

    bank_account_id: Mapped[serial] = mapped_column(ForeignKey('bank_account.id'))
    product_id: Mapped[serial] = mapped_column(ForeignKey('product.id'))
    count: Mapped[long_int]

    def __init__(self, bank_account_id: int, product_id: int, count: int) -> None:
        self.bank_account_id = validators.IntValidator.validate(bank_account_id, 64, True)
        self.product_id = validators.IntValidator.validate(product_id, 64, False)
        self.count = validators.IntValidator.validate(count, 64, True)

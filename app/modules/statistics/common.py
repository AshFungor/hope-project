import numpy as np
import sqlalchemy as orm

import app.models as models
from app.env import env


def get_companies() -> np.ndarray:
    return np.asarray(
        [
            acc.id
            for acc in env.db.impl()
            .session.query(models.BankAccount)
            .join(models.Company, models.Company.bank_account_id == models.BankAccount.id)
            .all()
        ]
    )


def get_users() -> np.ndarray:
    return np.asarray(
        [
            acc.id
            for acc in env.db.impl()
            .session.query(models.BankAccount.id)
            .join(models.User, models.User.bank_account_id == models.BankAccount.id)
            .all()
        ]
    )


def get_government() -> np.ndarray:
    hall = np.asarray(
        [
            acc.id
            for acc in env.db.impl()
            .session.query(models.BankAccount.id)
            .join(models.CityHall, models.CityHall.bank_account_id == models.BankAccount.id)
            .all()
        ]
    )
    cities = np.asarray(
        [
            acc.id
            for acc in env.db.impl()
            .session.query(models.BankAccount.id)
            .join(models.City, models.City.bank_account_id == models.BankAccount.id)
            .all()
        ]
    )
    prefectures = np.asarray(
        [
            acc.id
            for acc in env.db.impl()
            .session.query(models.BankAccount.id)
            .join(models.Prefecture, models.Prefecture.bank_account_id == models.BankAccount.id)
            .all()
        ]
    )
    return np.append(np.append(hall, cities), prefectures)

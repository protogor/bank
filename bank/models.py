#-*-coding: utf-8-*-
from sqlalchemy import Column, Integer, String, DateTime, \
     ForeignKey, Boolean, Float, event, func
from sqlalchemy.orm import backref, relation
from werkzeug import cached_property
from database import Model

import datetime


MONEY_SET = "set"
MONEY_GET = "get"
MONEY_BEETWEN = "btw"

TYPE_TRANSACTION = (
    (MONEY_SET, u"Зачислить средства"),
    (MONEY_GET, u"Списать средства"),
    (MONEY_BEETWEN, u"Перевод между счетами"),
)

TYPE_TRANSACTION_DICT = dict(TYPE_TRANSACTION)


class User(Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    address = Column(String(256))
    age = Column(Integer)
    active = Column(Boolean, default=True)

    def __init__(self, name, address, age, active=None):
        self.name = name 
        self.address = address 
        self.age = age
        self.active = active

    @property
    def amount(self):
        amount = self.accounts.with_entities(func.sum(Account.amount)).first()[0]
        return amount if amount else 0

    @cached_property
    def count_accounts(self):
        count = self.accounts.with_entities(func.count(Account.id)).first()[0]
        return count if count else 0

    def to_json(self):
        return dict(
            id=self.id,
            name=self.name,
            address=self.address,
            age=self.age,
            active=self.active,
            amount=self.amount,
            count_accounts=self.count_accounts
        )


class Account(Model):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relation(User, backref=backref("accounts", lazy="dynamic"))
    active = Column(Boolean, default=True)

    def __init__(self, amount, user, active=None):
        self.amount = amount
        self.user = user
        self.active = active

    @property
    def transactions_list(self):
        transactions_to = self.transactions_to.all()
        transactions_from = self.transactions_from.all()
        transactions = transactions_to + transactions_from
        return transactions

    @cached_property
    def count_transactions(self):
        count = len(self.transactions_list)
        return count


class Transaction(Model):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    account_to_id = Column(Integer, ForeignKey("accounts.id"))
    account_to = relation(Account, backref=backref("transactions_to", lazy="dynamic"), 
                          foreign_keys=[account_to_id])
    account_from_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    account_from = relation(Account, backref=backref("transactions_from", lazy="dynamic"), 
                            foreign_keys=[account_from_id])
    amount = Column(Float)
    type = Column(String(3))
    date_create = Column(DateTime)

    def __init__(self, account_to, account_from, amount, type=MONEY_SET, date_create=None):
        self.account_to = account_to 
        self.account_from = account_from if account_from else None
        self.type = type
        self.amount = amount
        if not date_create:
            date_create = datetime.datetime.now()
        self.date_create = date_create

    @property 
    def type_name(self):
        return TYPE_TRANSACTION_DICT.get(self.type)
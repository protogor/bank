#-*-coding: utf-8-*-
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, \
                    ValidationError, IntegerField, SelectField


def check_set_age(form, field):
    age = form.data["age"]
    try:
        age_int = int(age)
    except TypeError:
        raise ValidationError(u"Введите числовое значение.")
    if age_int < 5:
        raise ValidationError(u"Возраст введен неправильно.")


def check_set_amount(form, field):
    amount = form.data["amount"]
    try:
        amount = float(amount)
    except TypeError:
        raise ValidationError(u"Средства заданы неправильно.")

    if amount < 0:
        raise ValidationError(u"Значение должно быть больше 0.")        


def check_set_account(form, field):
    from bank.models import Account

    account_id = form.data["account_to"]
    if account_id == 0:
        raise ValidationError(u"Это поле обязательное!")
    if not Account.query.get(account_id):
        raise ValidationError(u"Аккаунт не существует")


def check_set_account_from(form, field):
    from bank.models import Account

    account_from_id = form.data["account_from"]
    if account_from_id != 0:
        if not Account.query.get(account_from_id):
            raise ValidationError(u"Аккаунт не существует")
        account_to_id = form.data["account_to"]
        if account_from_id == account_to_id:
            raise ValidationError(u"Нельзя переводить на один и тот же счет!")


def check_set_type(form, field):
    from bank.models import TYPE_TRANSACTION_DICT

    type = form.data["type"]
    if not TYPE_TRANSACTION_DICT.get(type):
        raise ValidationError(u"Такого типа транзакции не существует!")


class SelectAccounts(SelectField):

    def __init__(self, *args, **kwargs):
        from bank.models import Account

        super(SelectAccounts, self).__init__(*args, **kwargs)
        self.choices = [(account.id, u"%s № %s счет %s" % (account.user.name, account.user.id, account.id)) 
                        for account in Account.query.order_by("user").all()]
        self.choices.insert(0, (0, "---"))
        self.coerce = int


class SelectType(SelectField):

    def __init__(self, *args, **kwargs):
        from bank.models import TYPE_TRANSACTION

        super(SelectType, self).__init__(*args, **kwargs)
        self.choices = TYPE_TRANSACTION
        self.coerce = str


class FormTransaction(FlaskForm):
    account_to = SelectAccounts(u"Аккаунт", validators=[check_set_account])
    account_from = SelectAccounts(u"Акканут источник", validators=[check_set_account_from])
    type = SelectType(u"Тип", validators=[check_set_type])
    amount = StringField(u"Средства", validators=[validators.DataRequired(message=u"Это поле обязательное!"), 
                                                  check_set_amount])


class FormSearch(FlaskForm):
    account = SelectAccounts(u"Аккаунт", validators=[check_set_account])
    date_start = StringField(u"Дата с", validators=[validators.Length(min=2, max=50)])
    date_end = StringField(u"Дата до", validators=[validators.Length(min=2, max=50)])


class FormUser(FlaskForm):
    name = StringField(u"Имя", validators=[validators.DataRequired(message=u"Это поле обязательное!"), 
                                           validators.Length(min=2, max=50)])
    address = StringField(u"Адрес", validators=[validators.DataRequired(message=u"Это поле обязательное!"), 
                                                validators.Length(min=5, max=256)])
    age = IntegerField(u"Возраст", validators=[validators.DataRequired(message=u"Это поле обязательное!"), 
                                               check_set_age])


class FormAccount(FlaskForm):
    amount = StringField(u"Средства", validators=[validators.DataRequired(message=u"Это поле обязательное!"), 
                                                  check_set_amount])

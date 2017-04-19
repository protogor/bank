#-*-coding: utf-8-*-
import datetime
from flask import Blueprint, render_template, request, url_for, redirect, abort
from database import db_session
from bank.forms import FormUser, FormAccount, FormTransaction, FormSearch
from bank.models import User, Transaction, Account, MONEY_SET, MONEY_GET, MONEY_BEETWEN


general = Blueprint("general", __name__, template_folder="templates")

@general.route('/', methods=["GET", "POST"])
@general.route('/users/', methods=["GET", "POST"])
def users():
    form = FormUser()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User(name=form.data["name"], 
                        address=form.data["address"],  
                        age=form.data["age"])
            db_session.add(user)
            db_session.commit()
            return redirect(url_for("general.users"))

    users = User.query.all()
    return render_template("users/users_list.html", users=users, form=form)


@general.route('/users/<int:user_id>/', methods=["GET", "POST"])
def user_detail(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404)
    form = FormAccount()
    if form.validate_on_submit():
        account = Account(amount=float(form.data["amount"]), user=user)
        db_session.add(account)
        db_session.commit()
        return redirect(url_for("general.user_detail", user_id=user_id))

    accounts = user.accounts.all()
    return render_template("users/user_detail.html", user=user, accounts=accounts, form=form)


@general.route('/transactions/', methods=["GET", "POST"])
def transactions():
    form = FormTransaction()
    if request.method == "POST" and not request.form.get("search"):
        if form.validate_on_submit():
            account_to_id = form.data["account_to"]
            account_to = Account.query.get(account_to_id)
            account_from_id = form.data["account_from"]
            account_from = None
            if account_from_id:
                account_from = Account.query.get(account_from_id)        
            type = form.data["type"]
            amount = float(form.data["amount"])
            if type == MONEY_SET:
                account_to.amount += amount
            elif type == MONEY_GET:
                amount = min(account_to.amount, amount) 
                account_to.amount -= amount
            elif type == MONEY_BEETWEN:
                amount = min(account_from.amount, amount) 
                account_from.amount -= amount
                account_to.amount += amount
            transaction = Transaction(account_to=account_to, 
                                      account_from=account_from, 
                                      type=type, 
                                      amount=amount)
            db_session.add(transaction)
            db_session.commit()
            return redirect(url_for("general.transactions"))
    
    form_search = FormSearch()
    transactions = Transaction.query
    if request.method == "POST" and request.form.get("search"):
        account_id = request.form.get("account")
        date_start = request.form.get("date_start")
        date_end = request.form.get("date_end")
        if account_id != "0":
            transactions = transactions.filter(Transaction.account_to_id == account_id)
        if date_start:
            date_start = datetime.datetime.strptime(date_start, "%Y-%m-%d %H:%M")
            transactions = transactions.filter(Transaction.date_create > date_start)
        if date_end:
            date_end = datetime.datetime.strptime(date_end, "%Y-%m-%d %H:%M")
            transactions = transactions.filter(Transaction.date_create < date_end)

    transactions = transactions.all()
    return render_template("transactions/transactions_list.html", 
                            transactions=transactions, form=form, form_search=form_search)
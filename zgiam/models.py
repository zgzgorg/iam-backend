"""Database model module"""

import logging
import typing
import sqlalchemy
import sqlalchemy.schema
import sqlalchemy.sql
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import flask_login
import flask_dance.consumer.storage.sqla

import zgiam.lib.log
import zgiam.database

base = sqlalchemy.ext.declarative.declarative_base()


logger: logging.Logger = zgiam.lib.log.get_logger(__name__)


class Account(flask_login.UserMixin, base):
    """account table model
    it can be a bot/team account or a user
    """

    __tablename__ = "account"
    email = sqlalchemy.Column(sqlalchemy.String(255), primary_key=True, index=True)
    first_name = sqlalchemy.Column(sqlalchemy.String(30), nullable=False)
    last_name = sqlalchemy.Column(sqlalchemy.String(30), nullable=False)
    id = sqlalchemy.Column(sqlalchemy.String(100), unique=True)
    chinese_name = sqlalchemy.Column(sqlalchemy.String(255))
    nickname = sqlalchemy.Column(sqlalchemy.String(255))
    phone_number = sqlalchemy.Column(sqlalchemy.String(30), nullable=False)
    wechat_id = sqlalchemy.Column(sqlalchemy.String(30))
    line_id = sqlalchemy.Column(sqlalchemy.String(30))
    shirt_size = sqlalchemy.Column(sqlalchemy.String(10))
    company = sqlalchemy.Column(sqlalchemy.String(50))
    school = sqlalchemy.Column(sqlalchemy.String(50))
    register_date = sqlalchemy.Column(sqlalchemy.Date, server_default=sqlalchemy.sql.func.now())
    dietary_restriction = sqlalchemy.Column(sqlalchemy.String(255))
    reimbursement_platform = sqlalchemy.Column(sqlalchemy.String(50))
    reimbursement_method = sqlalchemy.Column(sqlalchemy.String(50))
    reimbursement_phone_number = sqlalchemy.Column(sqlalchemy.String(30))
    reimbursement_email = sqlalchemy.Column(sqlalchemy.String(255))
    join_date = sqlalchemy.Column(sqlalchemy.Date)
    birthday = sqlalchemy.Column(sqlalchemy.Date)
    memo = sqlalchemy.Column(sqlalchemy.JSON)
    type = sqlalchemy.Column(sqlalchemy.String(30))
    review_by_id = sqlalchemy.Column(sqlalchemy.String(100), sqlalchemy.ForeignKey("account.id"))
    review_status = sqlalchemy.Column(sqlalchemy.String(30))
    has_iam_google_account = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    reviewed_accounts: "Account" = sqlalchemy.orm.relationship(
        "Account", backref=sqlalchemy.orm.backref("review_by_user", remote_side=id)
    )
    # as always, we can do below too:
    # review_by_user = sqlalchemy.orm.relationship("User", remote_side=id)
    # reviewed_users = sqlalchemy.orm.relationship(
    #     "User", backref=sqlalchemy.orm.backref("user", remote_side=id)
    # )

    groups: typing.List["Group"] = sqlalchemy.orm.relationship(
        "Group", secondary="accout_group", back_populates="accounts"
    )

    tokens: typing.List["AccountToken"] = sqlalchemy.orm.relationship(
        "AccountToken", back_populates="account"
    )

    def __repr__(self):
        return (
            f"Account<name: {self.first_name} {self.last_name}, "
            f"email: {self.email}, id: {self.id}>"
        )

    def generate_id(self) -> str:
        """General ORG id for account
        The idea is first_name + last_name initial + duplicate number(if it is 0 will not be used)

        Returns:
            str: a general id
        """
        if self.id:
            return self.id

        with zgiam.database.get_session() as session:
            pure_firstname = self.first_name.replace(" ", "").lower()  # type: ignore
            lastname_initial = self.last_name.replace(" ", "").lower()[0]  # type: ignore

            temp_id = f"{pure_firstname}{lastname_initial}"
            query = (
                session.query(Account)
                .filter(Account.id.like(f"%{temp_id}%"))
                .statement.with_only_columns([sqlalchemy.sql.func.count()])
                .order_by(None)
            )
            count = session.execute(query).scalar()
            self.id = temp_id if not count else f"{temp_id}{count}"
        return self.id


class Group(base):
    """group table model"""

    __tablename__ = "group"
    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    year = sqlalchemy.Column(sqlalchemy.Integer)
    session = sqlalchemy.Column(sqlalchemy.Integer)
    chinese_name = sqlalchemy.Column(sqlalchemy.String(255))
    english_name = sqlalchemy.Column(sqlalchemy.String(60))
    email = sqlalchemy.Column(sqlalchemy.String(255), unique=True, index=True)
    memo = sqlalchemy.Column(sqlalchemy.JSON)

    accounts: typing.List["Account"] = sqlalchemy.orm.relationship(
        "Account", secondary="accout_group", back_populates="groups"
    )

    def __repr__(self):
        return f"Group<name: {self.english_name}, email: {self.email}, id: {self.id}>"


class AccountGroup(base):
    """account and group during many to many join table"""

    __tablename__ = "accout_group"
    account_id = sqlalchemy.Column(
        sqlalchemy.String(100), sqlalchemy.ForeignKey("account.id"), primary_key=True
    )
    group_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("group.id"), primary_key=True
    )


class OAuth(flask_dance.consumer.storage.sqla.OAuthConsumerMixin, base):
    """account OAuth token"""

    __tablename__ = "oauth"
    # XXX: not sure why need id column in OAuthConsumerMixin
    id = sqlalchemy.Column(sqlalchemy.Integer)
    provider_user_id = sqlalchemy.Column(sqlalchemy.String(256), unique=True, nullable=False)

    account_id = sqlalchemy.Column(
        sqlalchemy.String(100), sqlalchemy.ForeignKey("account.id"), primary_key=True
    )
    # flask-login, and flask-dance use `user`, but we are using `account`
    user: Account = sqlalchemy.orm.relationship(Account)

    @property
    def user_id(self):
        """user_id
        flask-login need this
        """
        return self.account_id

    @property
    def account(self):
        """account
        flask-login need user, but we are using account
        """
        return self.user

    @account.setter
    def account(self, account_):
        """account setter"""
        self.user = account_

    def __repr__(self):
        return f"OAuth<account_id: {self.account_id}, provider: {self.provider}>"


class AccountToken(base):
    """account token"""

    __tablename__ = "account_token"

    account_id = sqlalchemy.Column(sqlalchemy.String(100), sqlalchemy.ForeignKey("account.id"))
    token = sqlalchemy.Column(sqlalchemy.String(300), primary_key=True)
    # this expire time is not JWT expire time
    expire_time = sqlalchemy.Column(sqlalchemy.DateTime)

    account: Account = sqlalchemy.orm.relationship("Account", back_populates="tokens")

    def __repr__(self):
        return f"AccountToken<account_id: {self.account_id}, partial token: {self.token[-10:]}>"

"""Database model module"""

import logging
import typing
import sqlalchemy
import sqlalchemy.schema
import sqlalchemy.sql
import sqlalchemy.orm
import sqlalchemy.ext.declarative


import zgiam.lib.log
import zgiam.database

BASE = sqlalchemy.ext.declarative.declarative_base()


logger: logging.Logger = zgiam.lib.log.get_logger(__name__)


class Account(BASE):
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
    phone_number = sqlalchemy.Column(sqlalchemy.String(30))
    shirt_size = sqlalchemy.Column(sqlalchemy.String(10))
    company = sqlalchemy.Column(sqlalchemy.String(50))
    school = sqlalchemy.Column(sqlalchemy.String(50))
    register_date = sqlalchemy.Column(sqlalchemy.DateTime, server_default=sqlalchemy.sql.func.now())
    dietary_restriction = sqlalchemy.Column(sqlalchemy.String(255))
    reimbursement_platform = sqlalchemy.Column(sqlalchemy.String(50))
    reimbursement_method = sqlalchemy.Column(sqlalchemy.String(50))
    reimbursement_phone_number = sqlalchemy.Column(sqlalchemy.String(30))
    reimbursement_email = sqlalchemy.Column(sqlalchemy.String(255))
    join_date = sqlalchemy.Column(sqlalchemy.DateTime)
    birthday = sqlalchemy.Column(sqlalchemy.DateTime)
    memo = sqlalchemy.Column(sqlalchemy.JSON)
    type = sqlalchemy.Column(sqlalchemy.String(30))
    review_by_id = sqlalchemy.Column(sqlalchemy.String(100), sqlalchemy.ForeignKey("account.id"))
    review_status = sqlalchemy.Column(sqlalchemy.String(30))
    has_iam_google_account = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    reviewed_users: "Account" = sqlalchemy.orm.relationship(
        "Account", backref=sqlalchemy.orm.backref("review_by_user", remote_side=id)
    )
    # as always, we can do below too:
    # review_by_user = sqlalchemy.orm.relationship("User", remote_side=id)
    # reviewed_users = sqlalchemy.orm.relationship(
    #     "User", backref=sqlalchemy.orm.backref("user", remote_side=id)
    # )

    groups: typing.List["Group"] = sqlalchemy.orm.relationship(
        "Group", secondary="user_group", back_populates="accounts"
    )

    def __repr__(self):
        return (
            f"Account<name: {self.first_name} {self.last_name}, "
            f"email: {self.email}, id: {self.id}>"
        )


class Group(BASE):
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
        "Account", secondary="user_group", back_populates="groups"
    )

    def __repr__(self):
        return f"Group<name: {self.english_name}, email: {self.email}, id: {self.id}>"


class UserGroup(BASE):
    """user and group during many to many join table"""

    __tablename__ = "user_group"
    user_id = sqlalchemy.Column(
        sqlalchemy.String(100), sqlalchemy.ForeignKey("account.id"), primary_key=True
    )
    group_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("group.id"), primary_key=True
    )

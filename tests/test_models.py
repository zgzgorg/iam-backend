"""testing for zgiam.models module"""
# pylint: disable=C0116,W0621,W0212,W0611
import pytest
import sqlalchemy.exc

from tests.mocks.mock_database import db  # noqa: F401
import zgiam.models


def test_account_create(db):
    account = zgiam.models.Account(
        email="william@iam.test", first_name="william", last_name="chen", id="will"
    )
    db.session.add(account)
    db.session.commit()
    readback_account = (
        db.session.query(zgiam.models.Account).filter_by(email="william@iam.test").one()
    )
    assert (
        repr(readback_account) == "Account<name: william chen, email: william@iam.test, id: will>"
    )


def test_account_create_no_id(db):
    account = zgiam.models.Account(
        email="william2@iam.test", first_name="william", last_name="chen"
    )
    db.session.add(account)
    db.session.commit()
    readback_account = (
        db.session.query(zgiam.models.Account).filter_by(email="william2@iam.test").one()
    )
    assert readback_account.id == account.id


def test_duplicate_account_create(db):
    account = zgiam.models.Account(
        email="william@iam.test", first_name="william", last_name="chen", id="will"
    )
    db.session.add(account)
    db.session.commit()
    duplicate_account = zgiam.models.Account(
        email="william@iam.test", first_name="william", last_name="chen", id="will"
    )
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.add(duplicate_account)
        db.session.commit()
    db.session.rollback()


def test_create_account_miss_email(db):
    account = zgiam.models.Account(first_name="william", last_name="chen", id="willchen")
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.add(account)
        db.session.commit()


def test_account_review_by(db):
    review_account = zgiam.models.Account(
        email="william@iam.test", first_name="william", last_name="chen", id="will"
    )
    db.session.add(review_account)
    db.session.commit()
    account = zgiam.models.Account(
        email="jason@iam.test", first_name="jason", last_name="chen", review_by_id="will"
    )
    db.session.add(account)
    db.session.commit()
    readback_account = db.session.query(zgiam.models.Account).filter_by(id="will").one()
    assert readback_account.reviewed_accounts[0].id == account.id


def test_group_create(db):
    group = zgiam.models.Group(email="team@team.com")
    db.session.add(group)
    db.session.commit()
    readback_group = db.session.query(zgiam.models.Group).filter_by(email="team@team.com").one()
    assert repr(readback_group) == "Group<name: None, email: team@team.com, id: 1>"


def test_account_group_create(db):
    review_account = zgiam.models.Account(
        email="william@iam.test", first_name="william", last_name="chen", id="will"
    )
    db.session.add(review_account)
    db.session.commit()
    group = zgiam.models.Group(email="team@team.com")
    db.session.add(group)
    db.session.commit()
    readback_account = db.session.query(zgiam.models.Account).filter_by(id="will").one()
    readback_group = db.session.query(zgiam.models.Group).filter_by(email="team@team.com").one()
    readback_group.accounts.append(readback_account)
    db.session.commit()
    readback_group = db.session.query(zgiam.models.Group).filter_by(email="team@team.com").one()
    assert readback_group.accounts[0].id == readback_account.id
    readback_account_group = db.session.query(zgiam.models.AccountGroup).all()
    assert len(readback_account_group) == 1

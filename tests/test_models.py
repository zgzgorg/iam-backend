"""testing for zgiam.models module"""
# pylint: disable=C0116,W0621,W0212,W0611
import pytest
import sqlalchemy.exc
import zgiam.models


def test_account_create(db, unittest_data):
    account = unittest_data.account1
    db.session.add(account)
    db.session.commit()
    readback_account = db.session.query(zgiam.models.Account).filter_by(email=account.email).one()
    assert (
        repr(readback_account)
        == "Account<name: account one, email: accounto@iam.test, id: accounto>"
    )


def test_account_create_no_id(db, unittest_data):
    account = unittest_data.account1
    account.id = None
    db.session.add(account)
    db.session.commit()
    readback_account = db.session.query(zgiam.models.Account).filter_by(email=account.email).one()
    assert readback_account.id == account.id


def test_duplicate_account_create(db, unittest_data):
    account = unittest_data.account1
    db.session.add(account)
    db.session.commit()
    duplicate_account = zgiam.models.Account(
        email=account.email,
        first_name=account.first_name,
        last_name=account.last_name,
        id=account.id,
    )
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.add(duplicate_account)
        db.session.commit()
    db.session.rollback()


def test_create_account_miss_email(db, unittest_data):
    account = unittest_data.account1
    del account.email
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.add(account)
        db.session.commit()


def test_account_review_by(db, unittest_data):
    review_account = unittest_data.account1
    db.session.add(review_account)
    db.session.commit()
    account = unittest_data.account2
    account.review_by_id = review_account.id
    db.session.add(account)
    db.session.commit()
    readback_account = db.session.query(zgiam.models.Account).filter_by(id=review_account.id).one()
    assert readback_account.reviewed_accounts[0].id == account.id


def test_group_create(db, unittest_data):
    group = unittest_data.group1
    db.session.add(group)
    db.session.commit()
    readback_group = db.session.query(zgiam.models.Group).filter_by(email=group.email).one()
    assert repr(readback_group) == "Group<name: None, email: group1@team.com, id: 1>"


def test_account_group_create(db, unittest_data):
    account = unittest_data.account1
    group = unittest_data.group1
    db.session.add(account)
    db.session.commit()
    db.session.add(group)
    db.session.commit()
    readback_account = db.session.query(zgiam.models.Account).filter_by(id=account.id).one()
    readback_group = db.session.query(zgiam.models.Group).filter_by(email=group.email).one()
    readback_group.accounts.append(readback_account)
    db.session.commit()
    readback_group = db.session.query(zgiam.models.Group).filter_by(email=group.email).one()
    assert readback_group.accounts[0].id == readback_account.id
    readback_account_group = db.session.query(zgiam.models.AccountGroup).all()
    assert len(readback_account_group) == 1


def test_oauth_create(db, unittest_data):
    account = unittest_data.account1
    oauth = unittest_data.oauth1
    oauth.account = unittest_data.account1
    db.session.add_all([account, oauth])
    db.session.commit()
    readback_oauth = db.session.query(zgiam.models.OAuth).filter_by(account_id=account.id).one()
    assert repr(readback_oauth) == "OAuth<account_id: accounto, provider: orgiam>"
    # check the flask-login and flask-account need
    assert readback_oauth.user_id == account.id
    assert readback_oauth.account == account
    assert readback_oauth.user == account


def test_account_token_create(db, unittest_data):
    account = unittest_data.account1
    db.session.add(account)
    account_token = unittest_data.account_token1
    db.session.add(account_token)
    db.session.commit()
    readback_account_token = (
        db.session.query(zgiam.models.AccountToken).filter_by(account_id=account.id).one()
    )
    assert repr(readback_account_token) == "AccountToken<account_id: accounto, partial token: ...>"


def test_account_id_create_no_duplicate_name(db, unittest_data):
    account = unittest_data.account1
    expect_id = account.id
    account.id = None
    db.session.add(account)
    db.session.commit()
    id_ = account.generate_id()
    assert id_ == expect_id
    db.session.commit()


def test_account_id_create_with_duplicate_name(db, unittest_data):
    account1 = unittest_data.account1
    account3 = unittest_data.account3
    expect_id = account3.id
    account3.id = None
    db.session.add_all([account1, account3])
    db.session.commit()
    id_ = account3.generate_id()
    assert id_ == expect_id


def test_account_id_already_exist(db, unittest_data):
    account = unittest_data.account1
    db.session.add(account)
    db.session.commit()
    readback_account = db.session.query(zgiam.models.Account).filter_by(email=account.email).one()
    assert readback_account.id == account.generate_id()

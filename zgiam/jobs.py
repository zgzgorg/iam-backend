"""jobs modules"""
# TODO: may need to refactor and use tasks system with queue

import logging

import zgiam.lib.log
import zgiam.lib.config
import zgiam.lib.google
import zgiam.models


logger: logging.Logger = zgiam.lib.log.get_logger(__name__)


def create_google_workspace_account(account: zgiam.models.Account) -> None:
    """create Google Workspace account from Account models

    Args:
        account (zgiam.models.Account): database Account model
    """
    config = zgiam.lib.config.get_config()
    primary_domain = config.get("CORE", "PRIMARY_DOMAIN")
    body = {
        "externalIds": [{"value": account.id, "type": "organization"}],
        "primaryEmail": f"{account.id}@{primary_domain}",
        "orgUnitPath": f"/{primary_domain}",
        "name": {"givenName": account.first_name, "familyName": account.last_name},
        "password": account.phone_number,
        "changePasswordAtNextLogin": True,
        "recoveryEmail": account.email,
        "emails": [{"address": account.email, "type": "home"}],
    }
    zgiam.lib.google.AdminDirectory().users.insert(body=body).execute()

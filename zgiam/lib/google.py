"""Google client module"""
import abc
import logging
import os.path
import typing

import googleapiclient.discovery
import google.oauth2.service_account

import zgiam.lib.log
import zgiam.lib.config

logger: logging.Logger = zgiam.lib.log.get_logger(__name__)


class Google(metaclass=abc.ABCMeta):
    """Google client abstract connector class"""

    @abc.abstractmethod
    def __init__(
        self,
        /,
        service_account_key_path: str = "",
        *args,
        scopes: typing.Union[list, None] = None,
        **kwargs,
    ):  # pylint: disable=keyword-arg-before-vararg
        """[summary]

        Args:
            service_account_key_path (str, optional): service account key path.
                Defaults to config file GOOGLE_SERVICE_ACCOUNT_KEY_PATH:GENERAL_KEY
            scopes (list, optional): a scopes list Google required. Defaults to None.

        Raises:
            RuntimeError: key path not set
        """
        if not service_account_key_path:
            config = zgiam.lib.config.get_config()
            service_account_key_path = config.get("GOOGLE_SERVICE_ACCOUNT_KEY_PATH", "GENERAL_KEY")
            if not service_account_key_path:
                raise RuntimeError(
                    "{GOOGLE_SERVICE_ACCOUNT_KEY_PATH:GENERAL_KEY} not in the config file"
                )
        service_account_key_path = os.path.normpath(service_account_key_path)

        self._credentials = google.oauth2.service_account.Credentials.from_service_account_file(
            service_account_key_path, scopes=scopes
        )


class AdminDirectory(Google):
    """Google Admin directory client connector class"""

    def __init__(
        self, /, service_account_key_path: str = "", *args, **kwargs
    ):  # pylint: disable=keyword-arg-before-vararg
        """Google admin directory API
            Reference: https://developers.google.com/admin-sdk/directory/reference/rest

        Args:
            service_account_key_path (str, optional): service account key path.
                Defaults to config file GOOGLE_SERVICE_ACCOUNT_KEY_PATH:ADMIN_DIRECTORY_KEY
                if not set, read fromm GOOGLE_SERVICE_ACCOUNT_KEY_PATH:GENERAL_KEY
        """
        if not service_account_key_path:
            config = zgiam.lib.config.get_config()
            service_account_key_path = config.get(
                "GOOGLE_SERVICE_ACCOUNT_KEY_PATH", "ADMIN_DIRECTORY_KEY"
            )
        super().__init__(
            service_account_key_path,
            *args,
            scopes=["https://www.googleapis.com/auth/admin.directory.user"],
            **kwargs,
        )
        self.service = googleapiclient.discovery.build(
            "admin", "directory_v1", credentials=self._credentials
        )

    @property
    def users(self) -> googleapiclient.discovery.Resource:
        """users API
            Reference: https://developers.google.com/admin-sdk/directory/reference/rest/v1/users

        Returns:
            googleapiclient.discovery.Resource: google resource class
        """
        return self.service.users()  # pylint: disable = no-member

    @property
    def groups(self) -> googleapiclient.discovery.Resource:
        """Groups API
            Reference: https://developers.google.com/admin-sdk/directory/reference/rest/v1/groups

        Returns:
            googleapiclient.discovery.Resource: [description]
        """
        return self.service.groups()  # pylint: disable = no-member

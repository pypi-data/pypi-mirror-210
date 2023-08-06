"""Module containing the tsd-iam-ldap-sync package's exceptions."""


class TsdConfigException(Exception):
    """Base class for package exceptions."""


class ConfigurationFileUnavailable(TsdConfigException):
    """Config file is not available."""


class ConfigurationValidationError(TsdConfigException):
    """Config validation failed."""

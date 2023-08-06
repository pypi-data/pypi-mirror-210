import pathlib

try:
    import click
except ImportError:
    raise Exception("To use authenticated role provider you have to install rebotics_sdk[shell]")

from rebotics_sdk.cli.utils import app_dir, ReboticsScriptsConfiguration

from rebotics_sdk.providers import \
    RetailerProvider, CvatProvider, AdminProvider, DatasetProvider, FVMProvider, HawkeyeProvider


PROVIDER_NAME_TO_CLASS = {
    'retailer': RetailerProvider,
    'cvat': CvatProvider,
    'admin': AdminProvider,
    'dataset': DatasetProvider,
    'fvm': FVMProvider,
    'hawkeye': HawkeyeProvider,
}


class AuthenticatedRoleProvider:
    def __init__(self):
        self.app_path = pathlib.Path(app_dir)
        assert self.app_path.exists(), "App path from cli should exist and be available"

    def get_provider(self, provider_name, role):
        config_provider = ReboticsScriptsConfiguration(
            self.app_path / f"{provider_name}.json",
            PROVIDER_NAME_TO_CLASS[provider_name]
        )
        return config_provider.get_provider(role)


def get_provider(provider_name, role):
    """
    get authenticated provider for given role.
    Intendent to be used in scripts provided by the rebotics team.

    :param provider_name: name of the provider. One of: retailer, cvat, admin, dataset, fvm, hawkeye
    :param role: role to use for authentication

    General usage:
    >>> from rebotics_sdk import get_provider
    >>> admin = get_provider('admin', 'r3dev')
    >>> admin.version()
    """
    return AuthenticatedRoleProvider().get_provider(provider_name, role)

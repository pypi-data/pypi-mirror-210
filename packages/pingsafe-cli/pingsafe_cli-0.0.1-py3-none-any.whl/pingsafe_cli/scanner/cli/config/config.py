import logging

from pingsafe_cli.scanner.cli.registry import HttpMethod, GET_CONFIG_DATA_URL
from pingsafe_cli.scanner.cli.utils import  make_request, add_global_config_file, add_iac_config_file, \
    add_secret_config_file, upsert_pingsafe_cli

LOGGER = logging.getLogger("cli")


def set_configs(args):
    response = make_request(HttpMethod.GET, GET_CONFIG_DATA_URL, args.api_token)
    admin_configs = response.json()

    add_global_config_file(args, admin_configs)
    add_iac_config_file(args.cache_directory, admin_configs)
    add_secret_config_file(args.cache_directory, admin_configs)

    upsert_pingsafe_cli(args.cache_directory)
    LOGGER.info("PingSafe CLI Configured Successfully!")
    return 0

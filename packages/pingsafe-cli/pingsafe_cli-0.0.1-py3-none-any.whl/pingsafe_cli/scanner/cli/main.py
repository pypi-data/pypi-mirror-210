import requests
import logging
import sys
import pingsafe_cli.scanner.cli.command_line_arguments as CommandLineArgs
from pingsafe_cli.scanner.cli.codescanner import code_scanner
from pingsafe_cli.scanner.cli.config import config
from pingsafe_cli.scanner.cli.registry import MainSubParser, MissingConfig, MissingRequiredFlags, PlatformNotSupported
from pingsafe_cli.scanner.cli.utils import delete_all_cache, get_version, \
    initialize_logger, get_cache_directory, get_exit_code_on_crash

LOGGER = logging.getLogger("cli")


def main(args, cache_directory):
    if cache_directory != "" and args.invalidate_cache:
        delete_all_cache(cache_directory)
        LOGGER.info("Cache invalidated!")
        return 0

    if args.main_sub_parser == MainSubParser.CODE:
        return code_scanner.handle_code_sub_parser(args, cache_directory)
    elif args.main_sub_parser == MainSubParser.CONFIG:
        return config.set_configs(args)


def start():
    cache_directory = ""
    log_level = 20
    try:
        args = CommandLineArgs.evaluate_command_line_arguments()

        if args.debug:
            log_level = 10

        cache_directory = get_cache_directory()

        initialize_logger("cli", log_level)

        exit_code = main(args, cache_directory)
        LOGGER.debug(f"Exiting with code {exit_code}")
        sys.exit(exit_code)
    except requests.ConnectionError:
        LOGGER.warning("Something went wrong. Please check your internet connection or contact PingSafe customer support.")
        sys.exit(get_exit_code_on_crash(cache_directory))
    except requests.Timeout:
        LOGGER.warning("The request timed out.")
        sys.exit(get_exit_code_on_crash(cache_directory))
    except MissingConfig as e:
        LOGGER.warning(
            "Missing required configurations\nTry reconfiguring: pingsafe-cli config --api-token <pingsafe-api-token> ...")
        sys.exit(1)
    except MissingRequiredFlags as e:
        LOGGER.warning(e)
        sys.exit(1)
    except PlatformNotSupported as e:
        LOGGER.warning(e)
        sys.exit(0)
    except Exception as e:
        if log_level == 10:
            LOGGER.error(str(e))
        code = get_exit_code_on_crash(cache_directory)
        LOGGER.error(f"Something went wrong. Exiting with status code: {code}")
        sys.exit(code)


if __name__ == "__main__":
    start()

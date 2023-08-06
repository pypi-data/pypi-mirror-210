import argparse
from pingsafe_cli.scanner.cli.registry import OutputFormat, PACKAGE_NAME, DEFAULT_PINGSAFE_DIR
from pingsafe_cli.scanner.cli.utils import get_home_path
from importlib_metadata import version as get_version


def evaluate_command_line_arguments():
    # Initialize global parser
    parser = argparse.ArgumentParser(
        prog='PingSafeCli',
        description='PingSafe CLI to scan code for vulnerabilities.',
        epilog='PingSafe CLI to scan code for vulnerabilities.')

    # pingsafecli --all-sub-flags... (global flags)
    parser.add_argument("--invalidate-cache", dest="invalidate_cache", action="store_true", default=False,
                        help="Delete all stored cache")
    parser.add_argument("-v", "--version", action="version", help="PingSafe CLI Version",
                        version=get_version(PACKAGE_NAME))
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true", default=False, help="Show limited information")
    parser.add_argument("--debug", dest="debug", action="store_true", default=False, help="Add to switch to debug mode")
    parser.add_argument("--workers-count", dest="global_workers_count", metavar="",
                 help="Set worker count")
    parser.add_argument("--output-format", dest="global_output_format", metavar="",
                                   help="Result Output format",
                                   default=OutputFormat.JSON, choices=[OutputFormat.JSON, OutputFormat.CSV])
    parser.add_argument("--output-file", dest="global_output_file", metavar="", default="",
                                   help="Output file location")


    # Initialized subparser for global parser
    sub_parser = parser.add_subparsers(dest="main_sub_parser", title="Scan Type",
                                       description="PingSafe allows various types of scan.",
                                       help="Scan Type")

    # scanner subcommand[code/config]
    code_sub_parser = sub_parser.add_parser("code", prog="Code Scanner", description="PingSage scans your code.",
                                            help="Code Scanner")
    config_sub_parser = sub_parser.add_parser("config", prog="Configure PingSafe CLI",
                                              description="Configure your PingSafe CLI",
                                              help="Configure PingSafe CLI")

    # Initialized subparser for code parser
    code_sub_parser_type = code_sub_parser.add_subparsers(dest="code_type_sub_parser", help="Scan Code Type")

    secret_parser = code_sub_parser_type.add_parser("secret", prog="Secret Detection", description="",
                                                    help="Secret Detection")

    # scanner code secret --all-secret-sub-flags...
    secret_parser.add_argument("-d", "--directory", dest="directory", help="Directory to scan", required=True)
    secret_parser.add_argument("--generate-baseline", dest="generate_baseline", action="store_true", default=False,
                               help="Generate Baseline to ignore issues. Select between all-commits and current working directory(cwd)")
    secret_parser.add_argument("--all-commits", dest="all_commits", action="store_true", default=False,
                               help="Scan all commits")
    secret_parser.add_argument("--base-commit", dest="base_commit", metavar="", default="",
                               help="Base commit to start scan from")
    secret_parser.add_argument("--base-branch", dest="base_branch", metavar="", default="", help="Base branch to scan")
    secret_parser.add_argument("--include-ignored", dest="include_ignored", action="store_true", default=False,
                               help="Include ignored resources from baseline")
    secret_parser.add_argument("--verified-only", dest="verified_only", action="store_true", default=False,
                               help="Give results for verified secrets only")
    secret_parser.add_argument("--excluded-detectors", dest="excluded_detectors", nargs="+", default=[],
                               help="Give results for verified secrets only")
    secret_parser.add_argument("--disable-verification", dest="disable_verification", action="store_true",
                               default=False, help="Disable verification of secrets")
    secret_parser.add_argument("--skip-paths", dest="skip_paths", nargs="+", default=[], metavar="",
                               help="Skip path to scan")

    config_sub_parser.add_argument("--api-token", dest="api_token", required=True,
                                   help="Set your API Token")
    config_sub_parser.add_argument("--cache-directory", dest="cache_directory", metavar="",
                                   default=get_home_path(DEFAULT_PINGSAFE_DIR),
                                   help="Directory to store PingSafe Cache. By Default it is stored in $HOME/.pingsafe(Recommended)")
    config_sub_parser.add_argument("--output-format", dest="output_format", metavar="",
                                   help="Result Output format",
                                   default=OutputFormat.JSON, choices=[OutputFormat.JSON, OutputFormat.CSV])
    config_sub_parser.add_argument("--output-file", dest="output_file", metavar="", default="",
                                   help="Output file location")
    config_sub_parser.add_argument("--workers-count", dest="workers_count", default=5, metavar="",
                                   help="Set worker count")
    config_sub_parser.add_argument("--on-crash-exit-code", dest="on_crash_exit_code", default=1,
                                   metavar="", type=int,
                                   help="Exit status when something went wrong")

    return parser.parse_args()

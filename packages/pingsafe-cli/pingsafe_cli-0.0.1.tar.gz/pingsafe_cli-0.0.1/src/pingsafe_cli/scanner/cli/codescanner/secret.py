import hashlib
import json
import logging
import os.path
import subprocess
import uuid
from pingsafe_cli.scanner.cli.registry import CodeTypeSubParser, BASELINE_FILE, OutputFormat, PACKAGE_NAME, \
    MissingRequiredFlags
from pingsafe_cli.scanner.cli.utils import read_from_file, get_config_path, write_json_to_file, write_csv_to_file, \
    get_version

LOGGER = logging.getLogger("cli")
HASH_STRING = "pingsafe_hashing_string"


def secret_parser(args, cache_directory):
    secret_pre_evaluation(args)

    global_config_path = get_config_path(cache_directory)
    global_config_data = read_from_file(global_config_path)

    secret_config_path = get_config_path(cache_directory, CodeTypeSubParser.SECRET)
    secret_config_data = read_from_file(secret_config_path)

    # Calling secret-detector binary
    issues = call_secret_detector(args, global_config_data, secret_config_data, cache_directory)

    if args.generate_baseline:
        return generate_baseline(issues, args.directory)

    if len(issues) > 0:
        return secret_post_evaluation(args, issues, secret_config_data, global_config_data)
    return 0


def secret_pre_evaluation(args):
    if args.generate_baseline and (args.base_commit == "" or args.base_branch == ""):
        raise MissingRequiredFlags("Please provide mandatory flags --base-commit and --base-branch while generating baseline.")

    if (args.base_commit != "" and args.base_branch == "") or (args.base_branch != "" and args.base_commit == ""):
        raise MissingRequiredFlags("Please provide mandatory flags --base-commit and --base-branch")


def generate_baseline(issues, repo_path):
    baseline_path = repo_path + "/" + BASELINE_FILE

    result_hash = [generate_components_hash(issue["patches"], issue["type"]) for issue in issues]

    write_json_to_file(baseline_path, {"ignored_secrets_hash": list(set(result_hash))})
    LOGGER.info(f"Baseline generated successfully at {baseline_path}")
    return 0


def secret_post_evaluation(args, issues, secret_config_data, global_config_data):
    filtered_issues = []
    ignored_secrets_hash = []
    exit_code = 0

    baseline_path = args.directory + "/" + BASELINE_FILE
    if os.path.exists(baseline_path):
        baseline_data = read_from_file(baseline_path)
        ignored_secrets_hash = baseline_data["ignored_secrets_hash"]

    for issue in issues:
        check_for_exit = False
        if args.include_ignored:
            check_for_exit = True
            filtered_issues.append(issue)
            print_issue(issue, args.quiet, args.all_commits)
        elif generate_components_hash(issue["patches"], issue["type"]) not in ignored_secrets_hash:
            check_for_exit = True
            filtered_issues.append(issue)
            print_issue(issue, args.quiet, args.all_commits)

        if exit_code == 0 and check_for_exit and evaluate_exit_strategy(issue, secret_config_data) == 1:
            exit_code = 1

    output_file, output_format = get_output_file_and_format(args, global_config_data)

    if len(filtered_issues) > 0 and output_file != "":
        if output_format == OutputFormat.JSON:
            write_json_to_file(output_file, filtered_issues)
        elif output_format == OutputFormat.CSV:
            write_csv_to_file(output_file, filtered_issues)
        LOGGER.info(f"Result generated successfully at {output_file}")

    return exit_code


def call_secret_detector(args, global_config_data, secret_config_data, cache_directory):
    output_file_for_secret_detector = ""
    try:
        output_file_for_secret_detector = f"/tmp/{uuid.uuid4()}.json"
        command = generate_command(args, global_config_data, secret_config_data, output_file_for_secret_detector,
                                   cache_directory)

        subprocess.run(command)
        if os.path.exists(output_file_for_secret_detector):
            return read_from_file(output_file_for_secret_detector)
        return []
    except Exception as e:
        LOGGER.debug("Exception while call_secret_detector", e)
        raise e
    finally:
        if os.path.exists(output_file_for_secret_detector):
            os.remove(output_file_for_secret_detector)


def generate_command(args, global_config_data, secret_config_data, output_file, cache_directory):
    if args.base_branch and args.base_commit:
        args.all_commits = True

    workers_count = global_config_data["workers_count"]
    if args.global_workers_count:
        workers_count = args.global_workers_count

    version = get_version(PACKAGE_NAME)
    command = [f"{cache_directory}/bin/{version}/bin_secret_detector", "--repo-path", args.directory, "--worker-count",
               str(workers_count), "--output-path", output_file]

    paths_to_skip = args.skip_paths + global_config_data["pathToIgnore"]
    excluded_detectors = get_detectors_to_exclude(secret_config_data, args.excluded_detectors)

    if args.verified_only:
        command.extend(["--verified-only"])
    if args.all_commits:
        command.extend(["--all-commits"])
    if args.disable_verification:
        command.extend(["--disable-verification"])
    if len(paths_to_skip) > 0:
        for path in paths_to_skip:
            command.extend(["--skip-path", path])
    if args.base_branch and args.base_commit:
        command.extend(["--base-branch", args.base_branch, "--base-commit", args.base_commit])
    if len(excluded_detectors) > 0:
        for detector in excluded_detectors:
            command.extend(["--excluded-detectors", detector])
    if args.debug:
        command.extend(["--debug"])

    return command


def get_detectors_to_exclude(secret_config_data, excluded_detectors):
    admin_blacklisted_detectors = secret_config_data["blacklistedDetectors"]
    insuppressible_detectors = secret_config_data["insuppressibleDetectors"]

    uniq_detectors_to_exclude = list(set(admin_blacklisted_detectors + excluded_detectors))

    return [detector for detector in uniq_detectors_to_exclude if detector not in insuppressible_detectors]


def generate_components_hash(secret_patches, detector_type):
    sorted_components = sorted(secret_patches.keys())
    return detector_type.lower() + "_" + calculate_hash("".join(secret_patches[component]["value"] for component in sorted_components), "sha256")


def calculate_hash(string, algorithm):
    string += HASH_STRING
    hash_object = hashlib.new(algorithm)
    hash_object.update(string.encode("utf-8"))
    return hash_object.hexdigest()


def print_issue(issue, quiet, all_commits):
    if quiet:
        line_numbers = [str(issue["patches"][patch]["line"]) for patch in issue["patches"].keys()]
        verified_message = "verified" if issue["isSecretVerified"] else "unverified"
        message = f'[ISSUE]\tFound {verified_message} hardcoded {issue["title"]} at {issue["filePath"]} in line {",".join(line_numbers)}'
        if all_commits:
            message += f" for commit id {issue['commitId']}"
        print(message)
    else:
        print(json.dumps(issue, indent=4))



def evaluate_exit_strategy(issue, secret_config_data):
    check_if_verified = bool(secret_config_data["exitStrategy"]["exitOnlyOnVerifiedSecret"])
    whitelisted_severity = secret_config_data["exitStrategy"]["severity"]

    if issue["severity"] in whitelisted_severity:
        return 1
    if check_if_verified and issue["isSecretVerified"]:
        return 1

    return 0


def get_output_file_and_format(args, global_config_data):
    output_file = global_config_data["output_file"]
    if args.global_output_file:
        output_file = args.global_output_file

    output_format = global_config_data["output_format"]
    if args.global_output_format:
        output_format = args.global_output_format

    return output_file, output_format
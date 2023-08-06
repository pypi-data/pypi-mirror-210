import csv
import json
import logging
import os.path
import platform
import subprocess

import requests
from importlib_metadata import version as get_version
from pingsafe_cli.scanner.cli.registry import CONFIG_FILE_NAME, CodeTypeSubParser, IacConfigData, HttpMethod, \
    PACKAGE_NAME, PIP_COMMAND, PYPI_URL, GET_PRE_SIGNED_URL, BINARY_LIST, DEFAULT_TIMEOUT, LogColors, \
    DEFAULT_PINGSAFE_DIR, PINGSAFE_LOCAL_CONFIG_PATH, PlatformNotSupported

LOGGER = logging.getLogger("cli")


# Custom formatter class
class ColoredFormatter(logging.Formatter):
    FORMATS = {
        logging.ERROR: LogColors.FAIL + '%(levelname)s\t%(message)s' + LogColors.ENDC,
        logging.WARNING: LogColors.WARNING + '%(levelname)s\t%(message)s' + LogColors.ENDC,
        logging.INFO: '%(levelname)s\t%(message)s',
        logging.DEBUG: '%(levelname)s\t%(message)s',
        logging.CRITICAL: LogColors.FAIL + '%(levelname)s\t%(message)s' + LogColors.ENDC,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def initialize_logger(name, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    formatter = ColoredFormatter()
    handler.setFormatter(formatter)
    logger.propagate = False
    logger.addHandler(handler)


def get_os_and_architecture():
    operating_system = platform.system().lower()
    arch = platform.machine().lower()
    return operating_system, arch


def make_request(method, url, api_token, query_params=None, data={}):
    request_headers = generate_headers(api_token)
    response = requests.request(
        method=method,
        url=url,
        data=json.dumps(data),
        headers=request_headers,
        params=query_params,
        timeout=DEFAULT_TIMEOUT,
    )
    if response.status_code == 401:
        raise Exception("Unauthorized 401")
    if response.status_code == 501:
        raise PlatformNotSupported(f"Platform {request_headers['x-runtime-arch']} is not supported.")
    return response


def read_from_file(file_path):
    with open(file_path) as infile:
        return json.load(infile)


def write_json_to_file(file_path, data):
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def write_csv_to_file(file_path, data):
    if len(data) <= 0:
        return
    field_names = data[0].keys()
    with open(file_path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def generate_headers(api_token):
    version = get_version(PACKAGE_NAME)
    current_os, arch = get_os_and_architecture()
    return {
        'Content-Type': "application/json",
        'x-service-account-token': f'Bearer {api_token}',
        'user-agent': f'pingsafe-cli-{version}',
        'x-runtime-arch': f'{current_os}_{arch}'
    }


def check_if_paths_exist(paths):
    for path in paths:
        if not os.path.exists(path):
            return False
    return True


def add_global_config_file(args, admin_configs):
    if not os.path.exists(args.cache_directory):
        os.makedirs(args.cache_directory)

    global_config_file_path = args.cache_directory + "/" + CONFIG_FILE_NAME
    global_config = generate_custom_config(args)

    if os.path.exists(global_config_file_path):
        os.remove(global_config_file_path)
    write_json_to_file(global_config_file_path, {**admin_configs["global"], **global_config})

    local_config_dir = get_home_path(DEFAULT_PINGSAFE_DIR)
    if not os.path.exists(local_config_dir):
        os.makedirs(local_config_dir)
    write_json_to_file(get_home_path(PINGSAFE_LOCAL_CONFIG_PATH), {"cache_directory": args.cache_directory})


def add_iac_config_file(cache_directory, admin_configs, last_refreshed_time=None):
    iac_cache_dir = cache_directory + "/" + CodeTypeSubParser.IAC
    iac_config_file_path = iac_cache_dir + "/" + CONFIG_FILE_NAME
    iac_config_data = admin_configs[CodeTypeSubParser.IAC]
    iac_config_data[IacConfigData.LAST_REFRESHED_AT] = last_refreshed_time

    if not os.path.exists(iac_cache_dir):
        os.makedirs(iac_cache_dir)
    if os.path.exists(iac_config_file_path):
        os.remove(iac_config_file_path)
    write_json_to_file(iac_config_file_path, iac_config_data)


def add_secret_config_file(cache_directory, admin_configs, last_refreshed_time=None):
    secret_cache_dir = cache_directory + "/" + CodeTypeSubParser.SECRET
    secret_config_file_path = secret_cache_dir + "/" + CONFIG_FILE_NAME
    secret_config_data = admin_configs[CodeTypeSubParser.SECRET]

    if not os.path.exists(secret_cache_dir):
        os.makedirs(secret_cache_dir)
    if os.path.exists(secret_config_file_path):
        os.remove(secret_config_file_path)
    write_json_to_file(secret_config_file_path, secret_config_data)


def delete_all_cache(cache_directory):
    global_config_file_path = get_config_path(cache_directory)
    iac_config_file_path = get_config_path(cache_directory, CodeTypeSubParser.IAC)

    if os.path.exists(global_config_file_path):
        global_config_data = read_from_file(global_config_file_path)
        global_config_data["version"] = 0
        write_json_to_file(global_config_file_path, global_config_data)

    if os.path.exists(iac_config_file_path):
        iac_config_data = read_from_file(iac_config_file_path)
        iac_config_data[IacConfigData.LAST_REFRESHED_AT] = None
        write_json_to_file(iac_config_file_path, iac_config_data)


def generate_custom_config(args):
    return {
        "api_token": args.api_token,
        "cache_directory": args.cache_directory,
        "output_file": args.output_file,
        "output_format": args.output_format,
        "on_crash_exit_code": args.on_crash_exit_code,
        "workers_count": args.workers_count
    }


def get_config_path(cache_directory, provider=""):
    if provider != "":
        return cache_directory + "/" + provider + "/" + CONFIG_FILE_NAME
    return cache_directory + "/" + CONFIG_FILE_NAME


def get_cache_directory():
    local_config_path = get_home_path(PINGSAFE_LOCAL_CONFIG_PATH)
    if os.path.exists(local_config_path):
        local_config = read_from_file(local_config_path)
        return local_config["cache_directory"]
    return ""


def check_for_cli_updates(current_version):
    response = requests.get(f'{PYPI_URL}')
    if response.status_code != 200:
        LOGGER.error(f"[PyPi] Failed to check for updates, err: {response.text}")
        return
    LOGGER.debug(PIP_COMMAND)
    latest_version = response.json()['info']['version']
    if current_version != latest_version:
        LOGGER.debug(f"Update available, updating to latest version: {latest_version}")
        subprocess.call(f"{PIP_COMMAND}", shell=True)
    else:
        LOGGER.debug("No updates available")


def download_file(url, destination):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(destination, 'wb') as f:
            # Download the file in chunks
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    os.chmod(destination, 0o755)


def get_presigned_urls(cache, binary_list):
    data = {}
    for binary in binary_list:
        data[binary] = True
    global_config_file_path = get_config_path(cache)
    global_config_data = read_from_file(global_config_file_path)

    response = make_request(HttpMethod.POST, GET_PRE_SIGNED_URL, global_config_data["api_token"], None, data)
    if response.status_code != 200:
        LOGGER.error(f"Failed to get pres-signed urls, err: {response.text}")
        return {}
    else:
        return response.json()


def download(version, binary, url, cache):
    download_path = os.path.join(cache, "bin")
    if not os.path.exists(download_path):
        os.mkdir(download_path)

    version_path = os.path.join(download_path, version)
    if not os.path.exists(version_path):
        os.mkdir(version_path)

    file_path = os.path.join(version_path, binary)
    global_config_file_path = get_config_path(cache)
    global_config_data = read_from_file(global_config_file_path)
    download_file(url, file_path)
    LOGGER.debug(f"Successfully downloaded {binary} binary for version: {version}")


def get_exit_code_on_crash(cache_directory):
    try:
        if os.path.exists(get_config_path(cache_directory)):
            return read_from_file(get_config_path(cache_directory))["on_crash_exit_code"]
        return 1
    except Exception as e:
        logging.getLogger("cli").exception("Exception while get_exit_code_on_crash", e)
        return 1


# upsert_pingsafe_cli: will check that if any new pingsafe-cli version is available at PyPi, it will upgrade now
# and on next run it will download new binaries and run updated pingsafe-cli with updated binaries
def upsert_pingsafe_cli(cache_directory):
    current_version = get_version(PACKAGE_NAME)
    check_for_cli_updates(current_version)

    paths = []
    for binary in BINARY_LIST:
        paths.append(os.path.join(cache_directory, "bin", current_version, binary))

    download_required = not check_if_paths_exist(paths)
    if download_required:
        signed_urls = get_presigned_urls(cache_directory, BINARY_LIST)
        LOGGER.debug("Downloading required dependencies")
        for binary, signed_url in signed_urls.items():
            download(current_version, binary, signed_url, cache_directory)


def get_home_path(directory):
    if platform.system() == "Windows":
        return os.path.join(os.path.expandvars("$HOME"), directory)
    return os.path.join(os.path.expanduser("~"), directory)

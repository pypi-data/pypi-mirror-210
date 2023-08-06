import os.path
from enum import Enum

CONFIG_FILE_NAME = "config.json"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG_ENABLED = 0
BASELINE_FILE = ".baseline"
PACKAGE_NAME = "pingsafe_cli"
DEFAULT_TIMEOUT = (3.1, 5)
BINARY_LIST = ["bin_secret_detector"]

APP_URL = "https://app.pingsafe.com"
LOCAL_SERVER_URL = "http://localhost:8080"
BASE_URL = APP_URL

GET_PRE_SIGNED_URL = f"{BASE_URL}/apis/v1/cli/setup"
GET_CONFIG_DATA_URL = f"{BASE_URL}/apis/v1/cli/config"

MAIN_PIP_COMMAND = f"pip3 install --upgrade {PACKAGE_NAME}"
TEST_PIP_COMMAND = f"pip3 install -i https://test.pypi.org/simple/ --upgrade {PACKAGE_NAME}"
MAIN_PYPI_URL = f'https://pypi.org/pypi/{PACKAGE_NAME}/json'
TEST_PYPI_URL = f'https://test.pypi.org/pypi/{PACKAGE_NAME}/json'
PIP_COMMAND = MAIN_PIP_COMMAND
PYPI_URL = MAIN_PYPI_URL

DEFAULT_PINGSAFE_DIR = ".pingsafe"
PINGSAFE_LOCAL_CONFIG_PATH = os.path.join(DEFAULT_PINGSAFE_DIR, "local_config.json")


class MainSubParser(str, Enum):
    CODE = "code"
    CONFIG = "config"


class CodeTypeSubParser(str, Enum):
    IAC = "iac"
    SECRET = "secret"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"


class IacProvider(str, Enum):
    ALL = "all"
    TERRAFORM = "terraform"
    TERRAFORM_PLAN = "terraform-plan"
    CLOUDFORMATION = "cloudformation"
    KUBERNETES = "kubernetes"
    HELM = "helm"


class IacConfigData(str, Enum):
    LAST_REFRESHED_AT = "last_refreshed_at"


class OutputFormat(str, Enum):
    JSON = "JSON"
    CSV = "CSV"


class MissingConfig(Exception):
    pass


class MissingRequiredFlags(Exception):
    pass


class PlatformNotSupported(Exception):
    pass


class LogColors(str, Enum):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

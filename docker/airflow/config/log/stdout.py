# FIXME: to fix
from copy import deepcopy
from airflow.config_templates.airflow_local_settings import DEFAULT_LOGGING_CONFIG
import sys

LOGGING_CONFIG = deepcopy(DEFAULT_LOGGING_CONFIG)
LOGGING_CONFIG["handlers"]["processor"] = {
    "class": "logging.StreamHandler",
    "formatter": "airflow",
    "stream": sys.stdout,
}

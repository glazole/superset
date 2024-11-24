# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# This file is included in the final Docker image and SHOULD be overridden when
# deploying the image to prod. Settings configured here are intended for use in local
# development environments. Also note that superset_config_docker.py is imported
# as a final step as a means to override "defaults" configured here
#
import logging
import os
import pkg_resources

from flask_appbuilder.security.manager import AUTH_LDAP
from flask_caching.backends.filesystemcache import FileSystemCache
from importlib.resources import files
from typing import Any, Callable, Literal, TYPE_CHECKING, TypedDict
from celery.schedules import crontab

logger = logging.getLogger()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("superset")

DATABASE_DIALECT = os.getenv("DATABASE_DIALECT")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_DB = os.getenv("DATABASE_DB")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = (
    f"{DATABASE_DIALECT}://"
    f"{DATABASE_USER}:{DATABASE_PASSWORD}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"
)

EXAMPLES_USER = os.getenv("EXAMPLES_USER")
EXAMPLES_PASSWORD = os.getenv("EXAMPLES_PASSWORD")
EXAMPLES_HOST = os.getenv("EXAMPLES_HOST")
EXAMPLES_PORT = os.getenv("EXAMPLES_PORT")
EXAMPLES_DB = os.getenv("EXAMPLES_DB")

SQLALCHEMY_EXAMPLES_URI = (
    f"{DATABASE_DIALECT}://"
    f"{EXAMPLES_USER}:{EXAMPLES_PASSWORD}@"
    f"{EXAMPLES_HOST}:{EXAMPLES_PORT}/{EXAMPLES_DB}"
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "1")

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")


CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}
DATA_CACHE_CONFIG = CACHE_CONFIG


class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = ("superset.sql_lab",)
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_prefetch_multiplier = 1
    task_acks_late = False
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }
# ----------------------------------------------------
# AUTHENTICATION CONFIG
# ----------------------------------------------------
AUTH_TYPE = AUTH_LDAP
AUTH_LDAP_SERVER = "ldap://openldap:389"
AUTH_LDAP_USE_TLS = False
AUTH_LDAP_SEARCH = "dc=handyman,dc=moscow"  # the LDAP search base
AUTH_LDAP_UID_FIELD = "cn"  # the username field
# For a typical OpenLDAP setup (where LDAP searches require a special account):
# The user must be the LDAP USER as defined in LDAP_ADMIN_USERNAME
AUTH_LDAP_BIND_USER = "cn=admin,dc=handyman,dc=moscow"  # the special bind username for search
AUTH_LDAP_BIND_PASSWORD = "LBwVsdcybztkTbWouZHURUh4gm3MMMMjGPLKSw1Y"  # the special bind password for search
# registration configs
AUTH_USER_REGISTRATION = True  # allow users who are not already in the FAB DB
AUTH_USER_REGISTRATION_ROLE = "Admin"  # this role will be given in addition to any AUTH_ROLES_MAPPING
AUTH_LDAP_FIRSTNAME_FIELD = "givenName"
AUTH_LDAP_LASTNAME_FIELD = "sn"
AUTH_LDAP_EMAIL_FIELD = "mail"  # if null in LDAP, email is set to: "{username}@email.notfound"
# # a mapping from LDAP DN to a list of FAB roles
AUTH_ROLES_MAPPING = {
    "cn=Admin,ou=Groups,dc=handyman,dc=moscow": ["Admin"],
}
# the LDAP user attribute which has their role DNs
AUTH_LDAP_GROUP_FIELD = "memberOf"
# if we should replace ALL the user's roles each login, or only on registration
AUTH_ROLES_SYNC_AT_LOGIN = False

# ---------------------------------------------------
# Babel config for translations
# ---------------------------------------------------
BABEL_DEFAULT_LOCALE = "ru"
LANGUAGES = {
    "ru": {"flag": "ru", "name": "Russian"},
    "en": {"flag": "us", "name": "English"}
}

# ---------------------------------------------------
# Image and file configuration
# ---------------------------------------------------
SUPERSET_LOG_VIEW = True
BASE_DIR = pkg_resources.resource_filename("superset", "")
UPLOAD_FOLDER = BASE_DIR + "./uploads/"
UPLOAD_CHUNK_SIZE = 4096
IMG_UPLOAD_FOLDER = BASE_DIR + "./uploads/"
IMG_UPLOAD_URL = "./uploads/"

EXCEL_EXTENSIONS = {"xlsx", "xls"}
CSV_EXTENSIONS = {"csv", "tsv", "txt"}
CSV_UPLOAD_MAX_SIZE = None
CSV_EXPORT = {"encoding": "utf-8"}
EXCEL_EXPORT: dict[str, Any] = {}

#--------------------------------------------------------
# smtp server configuration
#--------------------------------------------------------
EMAIL_NOTIFICATIONS = True  # активация уведомлений
SMTP_HOST = "postbox.cloud.yandex.net"
SMTP_STARTTLS = True
SMTP_SSL = False
SMTP_USER = "postbox-user"
SMTP_PORT = 587
SMTP_PASSWORD = "BA7ja2wiGJ6wqSoOY/RHm5s1KSj90MMmWC/AZLTV9Wxl"
SMTP_MAIL_FROM = "airflow@handyman.moscow"
SMTP_SSL_SERVER_AUTH = False
ENABLE_CHUNK_ENCODING = False

# ---------------------------------------------------
# Feature flags
# ---------------------------------------------------
FEATURE_FLAGS = {
    "DRUID_JOINS": False,
    "DYNAMIC_PLUGINS": False,
    "DISABLE_LEGACY_DATASOURCE_EDITOR": True,
    "ENABLE_TEMPLATE_PROCESSING": False,
    "ENABLE_JAVASCRIPT_CONTROLS": False,
    "KV_STORE": False,
    "PRESTO_EXPAND_DATA": False,
    "THUMBNAILS": False,
    "SHARE_QUERIES_VIA_KV_STORE": False,
    "TAGGING_SYSTEM": False,
    "SQLLAB_BACKEND_PERSISTENCE": True,
    "LISTVIEWS_DEFAULT_CARD_VIEW": False,
    "ESCAPE_MARKDOWN_HTML": False,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_VIRTUALIZATION": True,
    "GLOBAL_ASYNC_QUERIES": False,
    "EMBEDDED_SUPERSET": False,
    "ALERT_REPORTS": True,
    "DASHBOARD_RBAC": True,
    "ENABLE_ADVANCED_DATA_TYPES": False,
    "ALERTS_ATTACH_REPORTS": True,
    "ALLOW_FULL_CSV_EXPORT": True,
    "ALLOW_ADHOC_SUBQUERY": False,
    "USE_ANALAGOUS_COLORS": False,
    "RLS_IN_SQLLAB": False,
    "CACHE_IMPERSONATION": False,
    "CACHE_QUERY_BY_USER": False,
    "EMBEDDABLE_CHARTS": True,
    "DRILL_TO_DETAIL": True,
    "DRILL_BY": True,
    "DATAPANEL_CLOSED_BY_DEFAULT": False,
    "HORIZONTAL_FILTER_BAR": False,
    "ESTIMATE_QUERY_COST": False,
    "SSH_TUNNELING": False,
    "AVOID_COLORS_COLLISION": True,
    "MENU_HIDE_USER_INFO": False,
    "ENABLE_SUPERSET_META_DB": False,
    "PLAYWRIGHT_REPORTS_AND_THUMBNAILS": False,
    "CHART_PLUGINS_EXPERIMENTAL": True,
}

CELERY_CONFIG = CeleryConfig

# FEATURE_FLAGS = {"ALERT_REPORTS": True}
ALERT_REPORTS_NOTIFICATION_DRY_RUN = True
WEBDRIVER_BASEURL = "http://superset:8088/"  # When using docker compose baseurl should be http://superset_app:8088/
# The base URL for the email report hyperlinks.
WEBDRIVER_BASEURL_USER_FRIENDLY = WEBDRIVER_BASEURL

SQLLAB_CTAS_NO_LIMIT = True

#
# Optionally import superset_config_docker.py (which will have been included on
# the PYTHONPATH) in order to allow for local settings to be overridden
#
try:
    import superset_config_docker
    from superset_config_docker import *  # noqa

    logger.info(
        f"Loaded your Docker configuration at " f"[{superset_config_docker.__file__}]"
    )
except ImportError:
    logger.info("Using default Docker config...")

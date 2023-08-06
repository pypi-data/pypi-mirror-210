# -*- coding: utf-8 -*-

import datetime
import logging
import sys
import io
import os
import json
import base64
import uuid
import time
import warnings
import copy
import pytz
from dateutil.parser import parse as dt_parse
from jinja2 import Template
from subprocess import Popen, PIPE, STDOUT
import tempfile

from google.cloud import bigquery
from google.cloud import firestore
from google.cloud import storage
from google.cloud import exceptions
from google.oauth2 import service_account

 # Globals
 #
_dag_name = "{DAG_NAME}"
_dag_type = "gbq-to-gbq"
_dag_generator_version = "{CURRENT_VERSION}"
TASK_STATUS_FIRESTORE_COLLECTION = "gbq-to-gbq-tasks-status"
AIRFLOW_COM_FIRESTORE_COLLECTION = "airflow-com"

DAG_INIT_STATUS_NORMAL = "NORMAL"
DAG_INIT_STATUS_FORCE_FAILED = "FORCE_FAILED"
DAG_INIT_STATUS_DUPLICATE_SUCCESS = "DUPLICATE_SUCCESS"


import airflow
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator, ShortCircuitOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.models import Variable
from airflow.operators import FashiondDataPubSubPublisherOperator
from airflow.operators import FashiondDataGoogleComputeInstanceOperator

# FD tools
from dependencies import fd_toolbox

default_args = {
    "owner": "TAILER",
    "depends_on_past": False,
    "email": [""],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=2),
    "start_date": datetime.datetime("{DAG_START_DATE}"),
    "provide_context": True
}

# Globals
#
_dag_name = "{DAG_NAME}"
_dag_type = "gbq-to-gbq"
_dag_generator_version = "{CURRENT_VERSION}"

import os
import logging

from dataclasses import dataclass, field
from typing import Optional, List, Dict

from dataclasses_json import dataclass_json
from pycarlo.core import Session, Client, Mutation
from pycarlo.lib.schema import GenericScalar
from sgqlc.types import Variable, non_null

from airflow_mcd.hooks import SessionHook


logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class AirflowEnv:
    # these env vars are used to get additional information about the Airflow
    # environment when running in AWS
    env_name: str = os.environ.get('AIRFLOW_ENV_NAME', 'airflow')
    env_id: Optional[str] = os.environ.get('AIRFLOW_ENV_ID')
    version: Optional[str] = os.environ.get('AIRFLOW_VERSION')
    base_url: Optional[str] = os.environ.get('AIRFLOW__WEBSERVER__BASE_URL')


@dataclass_json
@dataclass
class DagTaskInstanceResult:
    task_id: str
    state: str
    log_url: str
    prev_attempted_tries: int
    duration: float
    execution_date: str
    start_date: str
    end_date: str
    next_retry_datetime: Optional[str]
    max_tries: int
    try_number: int
    exception_message: Optional[str]
    inlets: Optional[List[Dict]]
    outlets: Optional[List[Dict]]


@dataclass_json
@dataclass
class BaseDagResult:
    dag_id: str
    env: AirflowEnv = field(init=False)

    def __post_init__(self):
        self.env = AirflowEnv()


@dataclass_json
@dataclass
class BaseDagRunResult(BaseDagResult):
    run_id: str
    success: bool


@dataclass_json
@dataclass
class DagResult(BaseDagRunResult):
    tasks: Optional[List[DagTaskInstanceResult]]
    state: str
    execution_date: str
    start_date: str
    end_date: str
    reason: Optional[str]
    event_type: str = 'dag'


@dataclass_json
@dataclass
class DagTaskResult(BaseDagRunResult):
    task: DagTaskInstanceResult
    event_type: str = 'task'


@dataclass_json
@dataclass
class TaskSlaMiss:
    task_id: str
    execution_date: str
    timestamp: str


@dataclass_json
@dataclass
class SlaMissesResult(BaseDagResult):
    sla_misses: List[TaskSlaMiss]
    event_type: str = 'sla_miss'


class AirflowEventsClient:
    """
    Client class used to send Airflow related events to Monte Carlo.
    """

    _UPLOAD_AIRFLOW_DAG_RESULT_OPERATION = "upload_airflow_dag_result"
    _UPLOAD_AIRFLOW_TASK_RESULT_OPERATION = "upload_airflow_task_result"
    _UPLOAD_AIRFLOW_SLA_MISSES_OPERATION = "upload_airflow_sla_misses"

    def __init__(self, mcd_session_conn_id: str):
        self.mcd_session_conn_id = mcd_session_conn_id

    def upload_dag_result(self, result: DagResult):
        payload = {
            'dag_id': result.dag_id,
            'run_id': result.run_id,
            'success': result.success,
            'reason': result.reason,
            'state': result.state,
            'execution_date': result.execution_date,
            'start_date': result.start_date,
            'end_date': result.end_date,
            'env': self._env_to_payload(result.env),
            'payload': Variable('payload'),
        }
        self._upload_result(self._UPLOAD_AIRFLOW_DAG_RESULT_OPERATION, payload, result.to_dict())

    def upload_task_result(self, result: DagTaskResult):
        payload = {
            'dag_id': result.dag_id,
            'run_id': result.run_id,
            'task_id': result.task.task_id,
            'success': result.success,
            'state': result.task.state,
            'log_url': result.task.log_url,
            'execution_date': result.task.execution_date,
            'start_date': result.task.start_date,
            'end_date': result.task.end_date,
            'duration': result.task.duration,
            'attempt_number': result.task.prev_attempted_tries,
            'env': self._env_to_payload(result.env),
            'payload': Variable('payload'),
        }
        if result.task.next_retry_datetime:
            payload['next_retry_date'] = result.task.next_retry_datetime
        if result.task.exception_message:
            payload['exception_message'] = result.task.exception_message
        self._upload_result(self._UPLOAD_AIRFLOW_TASK_RESULT_OPERATION, payload, result.to_dict())

    def upload_sla_misses(self, result: SlaMissesResult):
        payload = {
            'dag_id': result.dag_id,
            'env': self._env_to_payload(result.env),
            'payload': Variable('payload'),
        }
        self._upload_result(self._UPLOAD_AIRFLOW_SLA_MISSES_OPERATION, payload, result.to_dict())

    def _upload_result(self, operation_name: str, operation_parameters: Dict, payload_value: Dict):
        try:
            mc_client = Client(self._get_session())

            query = Mutation(payload=non_null(GenericScalar))
            attr = getattr(query, operation_name)
            attr(**operation_parameters)
            mc_client(query=query, variables={'payload': payload_value})
        except Exception as exc:
            logger.exception(f'Failed to upload information to MC: {exc}')

    def _get_session(self) -> Session:
        return SessionHook(mcd_session_conn_id=self.mcd_session_conn_id).get_conn()

    @staticmethod
    def _env_to_payload(env: AirflowEnv) -> Dict:
        values = {
            'env_name': env.env_name,
        }
        if env.env_id:
            values['env_id'] = env.env_id
        if env.base_url:
            values['base_url'] = env.base_url
        if env.version:
            values['version'] = env.version

        return values

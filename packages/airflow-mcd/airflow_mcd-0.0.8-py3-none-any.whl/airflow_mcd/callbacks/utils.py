import logging
from copy import deepcopy

import pytz
from airflow import DAG
from airflow.models import TaskInstance, SlaMiss, DagRun
from attr import asdict
from datetime import datetime

from airflow_mcd.callbacks.client import DagResult, DagTaskResult, AirflowEventsClient, DagTaskInstanceResult, \
    SlaMissesResult, TaskSlaMiss
from typing import Dict, List, Any, Optional


logger = logging.getLogger(__name__)


class AirflowEventsClientUtils:
    @classmethod
    def mcd_post_dag_result(
            cls,
            context: Dict,
            success: bool,
    ):
        if 'dag' not in context or 'run_id' not in context or 'dag_run' not in context:
            logger.error('Invalid context received in MCD callback: dag, run_id and dag_run are expected')
            return

        dag: DAG = context['dag']
        dag_run: DagRun = context['dag_run']
        task_instances = dag_run.get_task_instances()
        result = DagResult(
            dag_id=dag.dag_id,
            run_id=context['run_id'],
            success=success,
            reason=context.get('reason'),
            tasks=[cls._get_task_instance_result(ti) for ti in task_instances],
            state=dag_run.state,
            execution_date=dag_run.execution_date.isoformat(),
            start_date=dag_run.start_date.isoformat(),
            end_date=dag_run.end_date.isoformat(),
        )
        cls._get_events_client(dag).upload_dag_result(result)

    @classmethod
    def mcd_post_task_result(cls, success: bool, context: Dict):
        if 'dag' not in context or 'run_id' not in context or 'task_instance' not in context:
            logger.error('Invalid context received in MCD task callback: dag, run_id and task_instance are expected')
            return

        dag = context['dag']
        ti = context['task_instance']
        exception_message = str(context['exception']) if 'exception' in context else None
        result = DagTaskResult(
            dag_id=dag.dag_id,
            run_id=context['run_id'],
            success=success,
            task=cls._get_task_instance_result(ti, exception_message),
        )
        cls._get_events_client(dag).upload_task_result(result)

    @classmethod
    def mcd_post_sla_misses(cls, dag: DAG, sla_misses: List[SlaMiss]):
        result = SlaMissesResult(
            dag_id=dag.dag_id,
            sla_misses=[
                TaskSlaMiss(
                    task_id=sla_miss.task_id,
                    execution_date=sla_miss.execution_date.isoformat(),
                    timestamp=sla_miss.timestamp.isoformat(),
                ) for sla_miss in sla_misses
            ]
        )
        cls._get_events_client(dag).upload_sla_misses(result)

    @classmethod
    def _get_task_instance_result(
            cls,
            ti: TaskInstance,
            exception_message: Optional[str] = None
    ) -> DagTaskInstanceResult:
        return DagTaskInstanceResult(
            task_id=ti.task_id,
            state=ti.state,
            log_url=ti.log_url,
            prev_attempted_tries=ti.prev_attempted_tries,
            duration=ti.duration,
            execution_date=ti.execution_date.isoformat(),
            start_date=ti.start_date.isoformat(),
            end_date=ti.end_date.isoformat() if ti.end_date else datetime.now(tz=pytz.UTC).isoformat(),
            next_retry_datetime=cls._get_next_retry_datetime(ti),
            max_tries=ti.max_tries,
            try_number=ti.try_number,
            exception_message=exception_message,
            inlets=cls._get_lineage_list(ti, 'inlets'),
            outlets=cls._get_lineage_list(ti, 'outlets'),
        )

    @classmethod
    def _get_events_client(cls, dag: DAG) -> AirflowEventsClient:
        dag_params = dag.params or {}
        mcd_session_conn_id = dag_params.get('mcd_session_conn_id', 'mcd_default_session')
        return AirflowEventsClient(mcd_session_conn_id=mcd_session_conn_id)

    @classmethod
    def _get_next_retry_datetime(cls, ti: TaskInstance) -> Optional[str]:
        if not hasattr(ti, 'task') or not ti.end_date:
            return None
        return ti.next_retry_datetime().isoformat()

    @classmethod
    def _get_lineage_dict(cls, o: Any) -> Dict:
        attrs = deepcopy(asdict(o))
        attrs['type'] = str(type(o))
        return attrs

    @classmethod
    def _get_lineage_list(cls, ti: TaskInstance, attr: str) -> Optional[List[Dict]]:
        if not hasattr(ti, 'task'):
            return None
        lineage_list = getattr(ti.task, attr)
        if not lineage_list:
            return None
        return [
            cls._get_lineage_dict(lineage_object) for lineage_object in lineage_list
        ]

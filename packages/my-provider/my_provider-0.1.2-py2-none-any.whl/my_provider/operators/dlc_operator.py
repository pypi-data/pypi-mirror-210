from typing import Any

from airflow.models.baseoperator import BaseOperator
from airflow.utils.context import Context
from my_provider_top.my_provider.hooks.dlc_hook import DLCHook
import logging
LOG = logging.getLogger(__name__)


class DLCOperator(BaseOperator):
    def __init__(
            self,
            *,
            dlc_conn_id: str,
            sql="",
            engine="",
            job_name="",
            cmd_args ="",
            executor_size="",
            driver_size="",
            executor_numbers=0,
            **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.sql = sql
        self.engine = engine
        self.dlc_conn_id = dlc_conn_id
        self.job_name = job_name
        self.cmd_args = cmd_args
        self.executor_size = executor_size
        self.driver_size = driver_size
        self.executor_numbers = executor_numbers
        self.task_set: set | None = None
        self.batch_id: str | None = None

    def execute(self, context: Context) -> Any:
        print(vars(self))
        is_success = False
        dlc_hook = DLCHook(dlc_conn_id=self.dlc_conn_id)
        if len(self.sql) > 0 and len(self.executor_size) == 0:
            task_set = dlc_hook.create_sql_task(sql=self.sql, engine=self.engine)
            self.task_set = task_set
            LOG.info(f"execute task_set: [{task_set}]")
            is_success = dlc_hook.check_task_state(task_set)
        if len(self.sql) > 0 and len(self.executor_size) > 0:
            batch_id = dlc_hook.create_spark_batch_sql_task(
                sql=self.sql,
                engine=self.engine,
                executor_size=self.executor_size,
                driver_size=self.driver_size,
                executor_numbers=self.executor_numbers
            )
            self.batch_id = batch_id
            LOG.info(f"execute batch_id: [{batch_id}]")
            is_success = dlc_hook.check_spark_batch_sql_task_state(batch_id)
        if len(self.job_name) > 0:
            task_id = dlc_hook.create_spark_app_task(job_name=self.job_name, cmd_args=self.cmd_args)
            self.task_set = {task_id}
            is_success = dlc_hook.check_task_state({task_id})
        if not is_success:
            error_message = 'Task failed to run'
            self.log.error(error_message)
            raise ValueError(error_message)

    def on_kill(self):
        LOG.info("begin kill instance.")
        LOG.info(f"self: {vars(self)}")
        task_set = self.task_set
        dlc_hook = DLCHook(dlc_conn_id=self.dlc_conn_id)
        dlc_hook.cancel_task(task_set)






import base64
import time
from typing import Any
from airflow.hooks.base import BaseHook
from tencentcloud.common import credential
from tencentcloud.common.exception import TencentCloudSDKException
from tencentcloud.common.profile import client_profile
from tencentcloud.dlc.v20210125 import dlc_client, models

import logging

LOG = logging.getLogger(__name__)


class SQLTaskStates:
    INIT = 0
    RUNNING = 1
    SUCCESS = 2
    ERROR = -1
    CANCEL = -3


class BatchSQLTaskSates:
    INIT = 0
    SUCCESS = 1
    FAIL = 2
    CANCEL = 3
    EXPIRATION = 4


class DLCHook(BaseHook):
    def get_conn(self) -> Any:
        conn = self.get_connection(self.dlc_conn_id)
        cred = credential.Credential(conn.login, conn.password)
        region = conn.extra_dejson.get('region', 'ap-beijing')
        profile = client_profile.ClientProfile()
        client = dlc_client.DlcClient(cred, region, profile)
        return client

    def __init__(self, dlc_conn_id: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.dlc_conn_id = dlc_conn_id

    # 创建普通sql任务
    def create_sql_task(self, sql: str, engine: str) -> set:
        client = self.get_conn()
        # Describe DataEngine
        describe_data_engine_req = models.DescribeDataEnginesRequest()
        describe_data_engine_req_filter = models.Filter()
        describe_data_engine_req_filter.Name = "data-engine-name"
        describe_data_engine_req_filter.Values = [engine]
        describe_data_engine_req.Filters = [describe_data_engine_req_filter]
        LOG.info(f"describe_data_engine_req: [{vars(describe_data_engine_req)}]")
        describe_data_engine_rsp = client.DescribeDataEngines(describe_data_engine_req)
        if len(describe_data_engine_rsp.DataEngines) == 0:
            LOG.error(f"DataEngine: [{engine}] is not exist! ")
            return set()
        task_type = "SQLTask"
        if describe_data_engine_rsp.DataEngines[0].EngineType.lower().find("spark") > 0:
            task_type = "SparkSQLTask"

        request = models.CreateTasksRequest()
        request.Tasks = models.TasksInfo()
        request.DatabaseName = ""
        request.DataEngineName = engine
        request.Tasks.SQL = base64.b64encode(sql.encode('utf8')).decode('utf8')
        request.Tasks.TaskType = task_type
        request.Tasks.FailureTolerance = "Terminate"
        try:
            response = client.CreateTasks(request)
            return set(response.TaskIdSet)
        except TencentCloudSDKException:
            LOG.exception(
                "Exception while create task"
            )

    # 检查任务状态
    def check_task_state(self, task_set: set) -> bool:
        client = self.get_conn()
        request = models.DescribeTasksRequest()
        request_filter = models.Filter()
        request_filter.Name = "task-id"
        state = False

        while len(task_set) > 0:
            request_filter.Values = list(task_set)
            request.Filters = [request_filter]
            try:
                response = client.DescribeTasks(request)
                for task in response.TaskList:
                    LOG.info(f"task:[{task.Id}] Progress: [{task.ProgressDetail}]")
                    # 任务终止态
                    if task.State == SQLTaskStates.CANCEL:
                        LOG.warn(f"The task[{task.Id}] has been canceled. ")
                        task_set.remove(task.Id)
                        state = False
                        break
                    elif task.State in [SQLTaskStates.SUCCESS]:
                        task_set.remove(task.Id)
                        state = True
                    elif task.State in [SQLTaskStates.ERROR]:
                        LOG.error(f"The task[{task.Id}] has error. {task.OutputMessage}")
                        task_set.remove(task.Id)
                        state = False
                        break
            except TencentCloudSDKException:
                LOG.exception(
                    "Exception while getting task state. Task id: %s", task_set
                )
            time.sleep(2)
        return state

    # 取消sql任务
    def cancel_task(self, task_set: set):
        client = self.get_conn()
        request = models.CancelTaskRequest()
        for task in task_set:
            LOG.info(f"Cancel Task: [{task}].")
            request.TaskId = task
            try:
                client.CancelTask(request)
            except TencentCloudSDKException:
                LOG.exception(
                    "Exception while cancelling query. Task id: %s .", task
                )

    # 创建spark 作业任务
    def create_spark_app_task(self, job_name: str, cmd_args: str):
        client = self.get_conn()
        request = models.CreateSparkAppTaskRequest()
        request.JobName = job_name
        request.CmdArgs = cmd_args
        response = client.CreateSparkAppTask(request)
        return response.TaskId

    # 创建spark batch sql任务
    def create_spark_batch_sql_task(
            self,
            executor_size: str,
            driver_size: str,
            executor_numbers: int,
            engine: str,
            sql: str,
    ) -> str:
        client = self.get_conn()
        create_spark_batch_sql_request = models.CreateSparkSessionBatchSQLRequest()
        create_spark_batch_sql_request.DataEngineName = engine
        create_spark_batch_sql_request.ExecuteSQL = base64.b64encode(sql.encode('utf8')).decode('utf8')
        create_spark_batch_sql_request.DriverSize = driver_size
        create_spark_batch_sql_request.ExecutorMaxNumbers = executor_numbers
        create_spark_batch_sql_request.ExecutorSize = executor_size
        try:
            response = client.CreateSparkSessionBatchSQL(create_spark_batch_sql_request)
            return response.BatchId
        except TencentCloudSDKException:
            LOG.exception(
                "Exception while create task"
            )

    # 检查spark batch sql 任务状态
    def check_spark_batch_sql_task_state(self, batch_id: str) -> bool:
        client = self.get_conn()
        request = models.DescribeSparkSessionBatchSqlLogRequest()
        request.BatchId = batch_id
        state = False

        while True:
            try:
                response = client.DescribeSparkSessionBatchSqlLog(request)
                if response.State == BatchSQLTaskSates.FAIL:
                    LOG.error(f"The task[{batch_id}] has error")
                    state = False
                    break
                elif response.State == BatchSQLTaskSates.CANCEL:
                    LOG.error(f"The task[{batch_id}] has been canceled")
                    state = False
                    break
                elif response.State == BatchSQLTaskSates.SUCCESS:
                    state = True
                    break
                elif response.State in [BatchSQLTaskSates.EXPIRATION, response.State == BatchSQLTaskSates.INIT]:
                    LOG.info(f"batch id [{batch_id}], logs[{response.LogSet}]")
            except TencentCloudSDKException:
                LOG.exception(
                    "Exception while getting task state. Batch id: %s", batch_id
                )
            time.sleep(2)
        return state


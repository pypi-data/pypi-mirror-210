from typing import Any

from airflow.models.baseoperator import BaseOperator
from airflow.utils.context import Context

from my_provider.hooks.my_hook import MyCustomHook


class MyOperator(BaseOperator):
    def __init__(
            self,
            *,
            flag: str,
            **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.flag = flag

    def execute(self, context: Context) -> Any:
        my_hook = MyCustomHook
        my_hook.my_method(self=self, flag=self.flag)

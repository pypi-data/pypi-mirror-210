from airflow.hooks.base import BaseHook


class MyCustomHook(BaseHook):
    def __init__(self, flag, *args, **kwargs):
        super(MyCustomHook, self).__init__(*args, **kwargs)
        self.flag = flag

    def my_method(
            self,
            flag: str
    ) -> None:
        print(flag)

from airflow.plugins_manager import AirflowPlugin
from my_provider_top.my_provider.hooks.my_hook import MyCustomHook
from my_provider_top.my_provider.hooks.dlc_hook import DLCHook


class MyProviderPlugin(AirflowPlugin):
    name = "my_provider"
    hooks = [MyCustomHook, DLCHook]


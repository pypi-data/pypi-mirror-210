from airflow.plugins_manager import AirflowPlugin
from my_provider.hooks.dlc_hook import DLCHook


class MyProviderPlugin(AirflowPlugin):
    name = "my_provider"
    hooks = [DLCHook]


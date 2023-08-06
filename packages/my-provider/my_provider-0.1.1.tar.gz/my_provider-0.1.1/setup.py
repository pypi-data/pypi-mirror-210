from setuptools import setup, find_packages
setup(
    name='my_provider',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'apache-airflow>=2.0.0',
        'tencentcloud-sdk-python-internal>=3.0.769'

    ],
    entry_points={
        'apache_airflow_provider': [
            'my_provider = my_provider'
        ]
    }
)
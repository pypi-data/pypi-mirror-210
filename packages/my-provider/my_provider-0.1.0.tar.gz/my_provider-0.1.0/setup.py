from setuptools import setup, find_packages
setup(
    name='my_provider',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'apache-airflow>=2.0.0'
    ],
    entry_points={
        'apache_airflow_provider': [
            'my_provider = my_provider'
        ]
    }
)
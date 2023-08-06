"""
fill in
"""

from pyspark.sql import SparkSession
from schema_jobs.jobs.configuration.database_configuration import DatabaseConfig


def deploy_database(config: DatabaseConfig):
    """
    fill in
    """
    SparkSession.getActiveSession()
    SparkSession.getActiveSession().sql(
        f"CREATE DATABASE IF NOT EXISTS {config.database_name};"
    )

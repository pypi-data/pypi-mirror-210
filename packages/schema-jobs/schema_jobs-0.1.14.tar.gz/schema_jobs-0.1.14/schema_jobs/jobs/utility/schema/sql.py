"""
fill in
"""

from pyspark.sql import SparkSession


def deploy_sql(sql: str):
    """
    fill in
    """

    SparkSession.getActiveSession().sql(sql)

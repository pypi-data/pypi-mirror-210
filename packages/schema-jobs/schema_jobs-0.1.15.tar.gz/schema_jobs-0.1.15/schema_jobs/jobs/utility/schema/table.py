"""
fill in
"""

from pyspark.sql import SparkSession
from schema_jobs.jobs.configuration.table_configs import TableConfig


def deploy_table(config: TableConfig):

    """
    fill in
    """
    data_frame = SparkSession.getActiveSession().createDataFrame([], config.schema)
    data_frame.write.format("delta").mode("overwrite").saveAsTable(
        f"{config.database_name}.{config.table_name}"
    )

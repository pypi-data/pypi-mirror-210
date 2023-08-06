"""
fill in

"""

from schema_jobs.jobs.configuration.database_configuration import DatabaseConfiguration
from schema_jobs.jobs.configuration.table_configs import tables
from schema_jobs.jobs.utility.schema.database import deploy_database
from schema_jobs.jobs.utility.schema.table import deploy_table


def deploy_database_tables():
    """
    fill in
    """
    # spark = SparkSession \
    #    .builder \
    #    .appName("Schema App") \
    #    .getOrCreate()
    deploy_database(DatabaseConfiguration)
    for table in tables:
        deploy_table(table)


if __name__ == "__main__":
    deploy_database_tables()

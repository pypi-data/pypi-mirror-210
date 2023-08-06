"""
fill in
"""

from pyspark.sql.types import (
    BooleanType,
    BooleanType,
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)


def bronze_machine_raw():
    """
    fill in
    """
    schema = StructType(
        [
            StructField("N8j2", DoubleType(), True),
            StructField("42mj", DoubleType(), True),
            StructField("6tk3", BooleanType(), True),
        ]
    )
    return schema


def silver_machine_raw():
    """
    fill in
    """
    schema = StructType(
        [
            StructField("N8j2", DoubleType(), True),
            StructField("42mj", DoubleType(), True),
            StructField("6tk3", BooleanType(), True),
            StructField("engine_type", StringType(), True),
        ]
    )
    return schema


def bronze_sap_bseg():
    """
    fill in
    """
    schema = StructType(
        [
            StructField("MANDT", StringType(), True),
            StructField("BUKRS", StringType(), True),
            StructField("BELNR", StringType(), True),
            StructField("GJAHR", DoubleType(), True),
            StructField("BUZEI", DoubleType(), True),
        ]
    )
    return schema


def bronze_sales():
    """
    fill in
    """
    schema = StructType(
        [
            StructField("ORDERNUMBER", IntegerType(), True),
            StructField("SALE", DoubleType(), True),
            StructField("ORDERDATE", IntegerType(), True),
            StructField("STATUS", BinaryType(), True),
            StructField("CUSTOMERNAME", StringType(), True),
            StructField("ADDRESSLINE", IntegerType(), True),
            StructField("CITY", StringType(), True),
            StructField("STATE", StringType(), True),
            StructField("STORE", StringType(), True),
        ]
    )
    return schema


def gold_sales():
    """
    fill in
    """
    schema = StructType(
        [
            StructField("CUSTOMERNAME", StringType(), True),
            StructField("AVG", DoubleType(), True),
            StructField("TOTAL", DoubleType(), True),
        ]
    )
    return schema

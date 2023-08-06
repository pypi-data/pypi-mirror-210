"""
fill in
"""

from pyspark.sql.types import (
    BinaryType,
    FloatType,
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
            StructField("N8j2", FloatType(), True),
            StructField("42mj", FloatType(), True),
            StructField("6tk3", BinaryType(), True),
        ]
    )
    return schema


def silver_machine_raw():
    """
    fill in
    """
    schema = StructType(
        [
            StructField("N8j2", FloatType(), True),
            StructField("42mj", FloatType(), True),
            StructField("6tk3", BinaryType(), True),
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
            StructField("GJAHR", FloatType(), True),
            StructField("BUZEI", FloatType(), True),
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
            StructField("SALE", FloatType(), True),
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
            StructField("AVG", FloatType(), True),
            StructField("TOTAL", FloatType(), True),
        ]
    )
    return schema

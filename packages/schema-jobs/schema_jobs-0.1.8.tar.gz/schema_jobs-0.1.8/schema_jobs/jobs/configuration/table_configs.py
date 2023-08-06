"""
fill in
"""

import abc
from dataclasses import dataclass

from schema_jobs.jobs.utility.schema.schemas import (
    bronze_machine_raw,
    bronze_sales,
    bronze_sap_bseg,
    gold_sales,
)


class TableConfig(abc.ABC):
    """
    fill in

    """

    table_name = ""
    database_name = ""
    schema = ""


@dataclass
class TableConfigBronzeMachineRaw(TableConfig):
    """
    fill in

    """

    table_name = "bronze_machine_raw"
    database_name = "dev"
    schema = bronze_machine_raw()


@dataclass
class TableConfigBronzSapBseg(TableConfig):
    """
    fill in

    """

    table_name = "bronze_sap_bseg"
    database_name = "dev"
    schema = bronze_sap_bseg()


@dataclass
class TableConfigBronzeSales(TableConfig):
    """
    fill in

    """

    table_name = "bronze_sales"
    database_name = "dev"
    schema = bronze_sales()


@dataclass
class TableConfigGoldSales(TableConfig):
    """
    fill in

    """

    table_name = "gold_sales"
    database_name = "dev"
    schema = gold_sales()


tables = [
    TableConfigBronzeMachineRaw,
    TableConfigBronzSapBseg,
    TableConfigBronzeSales,
    TableConfigGoldSales,
]

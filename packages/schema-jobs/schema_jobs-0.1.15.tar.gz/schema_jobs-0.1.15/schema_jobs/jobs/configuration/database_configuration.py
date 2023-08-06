"""
fill in

"""
import abc
from dataclasses import dataclass


class DatabaseConfig(abc.ABC):
    """
    fill in

    """

    database_name = "dev"


@dataclass
class DatabaseConfiguration(DatabaseConfig):
    """
    fill in
    """

    database_name = "dev"

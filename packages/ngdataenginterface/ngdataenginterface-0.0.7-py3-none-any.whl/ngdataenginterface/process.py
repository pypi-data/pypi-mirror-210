from dataclasses import dataclass
from typing import Optional

import copy
import logging

from pyspark.sql.window import Window
from pyspark.sql.functions import col, row_number

from ngdataenginterface.table import Table

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class MergeParams:
    def __init__(
        self,
        partition: Optional[list],
        order: Optional[list],
    ):
        self.partition = partition
        self.order = order


class Process:
    def __init__(self, read: Table, write: Table, merge: dict = {}):
        self.read = read
        self.write = write
        self.merge = MergeParams(
            partition=merge.get("partition_columns"), order=merge.get("order_columns")
        )

    def merge_tables(self, df1, df2):
        """
        This function merges two dataframes based on a specified partition and order.
        It assigns a row number based on the order within each partition and filters
        for only the first row in each partition.

        Parameters:
        df1 (DataFrame): The first dataframe.
        df2 (DataFrame): The second dataframe.

        Returns:
        DataFrame: The merged dataframe.
        """
        if self.merge.partition is None or self.merge.order is None:
            raise ValueError(
                "The merge parameters 'partition' and 'order' must be specified."
            )

        logger.info("Merging tables...")
        # Union of the two dataframes
        merged_df = df1.union(df2)

        # Create a window specification
        window_spec = Window.partitionBy(
            [col(x) for x in self.merge.partition]
        ).orderBy([col(x).desc() for x in self.merge.order])

        # Add a row number column
        merged_df = merged_df.withColumn("row", row_number().over(window_spec))

        # Filter for the first row in each partition
        result_df = merged_df.filter(col("row") == 1).drop("row")

        logger.info("Tables merged successfully.")
        return result_df

    def read_previous_partition_table(self):
        current_date = copy.deepcopy(
            self.read.meta.date
        )  # deepcopying object to avoid changing the original object
        self.read.meta.date = self.read.previous_partition_date()  # type: ignore
        previous_partition_table = self.read.read_table()
        self.read.meta.date = current_date  # returning to original state
        return previous_partition_table

    def merge_previous_partition(self):
        df1 = self.read_previous_partition_table()
        # df1.show()
        df2 = self.read.read_table()
        # df2.show()
        return self.merge_tables(df1, df2)

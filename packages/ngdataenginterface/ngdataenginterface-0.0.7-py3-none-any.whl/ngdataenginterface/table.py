import logging

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from pyspark import SQLContext
from pyspark.sql.types import *
from pyspark.sql.functions import lit
from pyspark.sql import DataFrame

from ngdataenginterface.aws_interface import AWSInterface
from ngdataenginterface.spark_manager import SparkManager
from ngdataenginterface.utils import handle_pyspark_timestamp_in_schema

logger = logging.getLogger(__name__)


PARTITION_MAP = {
    "part_year": lambda dt: dt.strftime("%Y"),
    "part_month": lambda dt: dt.strftime("%m"),
    "part_day": lambda dt: dt.strftime("%d"),
    "part_hour": lambda dt: dt.strftime("%H"),
    "part_minute": lambda dt: dt.strftime("%M"),
}


@dataclass
class PathParams:
    env: str
    bucket_name: str
    object_path: str
    partition: str
    file_type: str

    def input_validation(self, data):
        # table validation
        assert "bucket_name" in data.keys(), "Couldn`t find `bucket_name` in path input"
        assert "object_path" in data.keys(), "Couldn`t find `object_path` in path input"
        assert "partition" in data.keys(), "Couldn`t find `partition` in path input"
        assert "file_type" in data.keys(), "Couldn`t find `file_type` in path input"

    @classmethod
    def from_dict(cls, data: dict[str, str]):
        instance = cls(
            env=data["env"],
            bucket_name=data["bucket_name"],
            object_path=data["object_path"],
            partition=data["partition"],
            file_type=data["file_type"],
        )

        instance.input_validation(data)
        return instance


@dataclass
class MetaParams:
    date: datetime
    overwrite: bool = False


class Table:
    def __init__(
        self,
        path: PathParams,
        meta: MetaParams,
        aws_interface: AWSInterface,
        spark_manager: SparkManager,
    ):
        self.path = path
        self.meta = meta
        self.aws_interface = aws_interface
        self.spark_manager = spark_manager
        logger.info("Table object initialized.")

    def partition_path(self, date=None) -> str:
        """Constructs the partition path from each partition and current execution date

        Parameters
        ----------
        self : TableParams
        date : datetime

        Returns
        -------
        str
            the resulting partition path
        """
        logger.info("Generating partition path.")
        if not self.path.partition:
            return ""

        if date is None:
            date = self.meta.date

        partition_path = ""

        # iterates on each partition
        for part in self.path.partition.split("/"):
            # constructs the partition path from 'ref_date'
            partition_path += part + "=" + PARTITION_MAP[part](date) + "/"

        # returns the partition_path without last '/' charactere
        return partition_path[:-1]

    def previous_partition_date(self):
        """
        Calculate the previous partition date based on the current partition indicator.

        Returns:
            datetime.datetime: The previous partition date.

        Raises:
            ValueError: If the partition indicator is unknown.
        """
        logger.info("Calculating previous partition date.")
        if not self.path.partition:
            return None

        # Define a dictionary mapping partition indicator to corresponding delta
        partition_to_delta = {
            "part_year": relativedelta(years=1),
            "part_month": relativedelta(months=1),
            "part_day": timedelta(days=1),
            "part_hour": timedelta(hours=1),
            "part_minute": timedelta(minutes=1),
        }

        # Split the partition_indicator string into individual partitions
        partitions = self.path.partition.split("/")

        # Loop through each partition in reverse order until a match is found
        for partition in reversed(partitions):
            if partition in partition_to_delta:
                return self.meta.date - partition_to_delta[partition]

        # If no match is found, raise an error
        raise ValueError(f"Unknown partition indicator: {self.path.partition}")

    def previous_partition_path(self):
        """
        Generate the previous partition path based on the current partition date.

        Returns:
            str: The previous partition path.

        """
        logger.info("Generating previous partition path.")

        # Get the previous partition date
        previous_date = self.previous_partition_date()

        # Generate the previous partition path from the previous date
        return self.partition_path(date=previous_date)

    def bucket_url(self, s3="s3a"):
        """
        Generate the URL for the bucket.

        Args:
            s3 (str, optional): The S3 protocol to use. Defaults to "s3a".

        Returns:
            str: The bucket URL.
        """
        logger.info("Generating bucket URL.")
        return f"{s3}://{self.path.bucket_name}"

    def table_path(self):
        """
        Generate the path for the table.

        Returns:
            str: The table path.
        """
        logger.info("Generating table path.")
        return f"{self.path.object_path}/table"

    def schema_path(self):
        """
        Generate the path for the schema.

        Returns:
            str: The schema path.
        """
        logger.info("Generating schema path.")
        return f"{self.path.object_path}/schema.json"

    def table_path_with_partition(self):
        """
        Generate the table path with the partition.

        Returns:
            str: The table path with the partition.
        """
        logger.info("Generating table path with partition.")
        table_path = self.table_path()
        partition_path = self.partition_path()

        if partition_path:
            return f"{table_path}/{partition_path}"

        return table_path

    def table_url(self):
        """
        Generate the URL for the table.

        Returns:
            str: The table URL.
        """
        logger.info("Generating table URL.")
        return f"{self.bucket_url()}/{self.table_path()}"

    def table_url_with_partition(self):
        """
        Generate the URL for the table.

        Returns:
            str: The table URL.
        """
        logger.info("Generating table URL.")
        return f"{self.bucket_url()}/{self.table_path_with_partition()}"

    def check_for_new_data(self):
        """
        Check if there is new data in the table.

        Returns:
            bool: True if there is new data, False otherwise.
        """
        path = self.table_path_with_partition()
        bucket_name = self.path.bucket_name
        logger.info("Checking object within path: %s in bucket: %s", path, bucket_name)
        object_list = self.aws_interface.list_objects_key_aws(bucket_name, path)
        logger.debug("Objects: %s", object_list)
        return len(object_list) != 0

    def retrieve_schema(self) -> StructType:
        """
        Retrieve the schema for the data.

        Returns:
            pyspark.sql.types.StructType: The retrieved schema.

        Raises:
            ValueError: If there is an issue retrieving or handling the schema.
        """
        logger.info("Retrieving schema.")
        logger.info("Bucket Name: %s", self.path.bucket_name)
        logger.info("Object Path: %s", self.schema_path())

        # Get the object from AWS S3 bucket
        schema_object = self.aws_interface.get_object_aws(
            self.path.bucket_name,
            self.schema_path(),
        )

        # Decode the object to string
        schema_str = schema_object.decode("utf8").replace("\n    ", "")

        try:
            # Convert the string to JSON
            schema_json = json.loads(schema_str)

            # Convert the JSON schema to PySpark StructType schema
            pyspark_schema = StructType.fromJson(schema_json)

            logger.debug("PySpark Schema: %s", repr(pyspark_schema))

            # Handle timestamp issues in PySpark schema
            return handle_pyspark_timestamp_in_schema(pyspark_schema)
        except (ValueError, Exception) as e:
            raise ValueError("Error retrieving or handling schema: {}".format(str(e)))

    def read_table(self):
        """
        Read the table data based on the file type.

        Returns:
            pyspark.sql.DataFrame: The loaded table data.

        Raises:
            Exception: If the file type is not found.
        """

        path = self.table_url_with_partition()
        schema = self.retrieve_schema()

        logger.info("Reading table data from path: %s", path)

        if self.path.file_type == "csv":
            return (
                self.spark_manager.spark.read.option("header", False)
                .format("csv")
                .schema(schema)
                .load(path)
            )
        elif self.path.file_type == "json":
            return (
                self.spark_manager.spark.read.format("json").schema(schema).load(path)
            )
        elif self.path.file_type == "parquet":
            sql = SQLContext(self.spark_manager.spark)  # type: ignore
            return sql.read.schema(schema).parquet(path)

        # Throw an error for unsupported file types
        raise Exception("File type not found")

    def write_schema(self, df: DataFrame):
        """
        Write the schema of the DataFrame to the destination.

        Args:
            df (pyspark.sql.DataFrame): The DataFrame containing the table data.

        Raises:
            ValueError: If there is an issue with putting the schema object to AWS S3.
        """
        # Get the PySpark schema from the DataFrame
        pyspark_schema = df.schema.jsonValue()

        try:
            self.aws_interface.put_object_aws(
                self.path.bucket_name, self.schema_path(), pyspark_schema
            )
        except Exception as e:
            raise ValueError("Error writing schema: {}".format(str(e)))

    def delete_table_to_overwrite(self):
        """
        Delete the destination table if overwrite is set to True in the metadata.

        Raises:
            ValueError: If there is an issue with deleting the table objects from AWS S3.
        """
        # Skip overwriting if the overwrite indicator is set to False in the metadata
        if self.meta.overwrite == False:
            return

        try:
            self.aws_interface.delete_objects_aws(
                self.path.bucket_name,
                self.table_path_with_partition(),
            )
        except Exception as e:
            raise ValueError("Error deleting table objects: {}".format(str(e)))

    def write_table(self, df: DataFrame):
        """
        Write the table data to the destination.

        Args:
            df (pyspark.sql.DataFrame): The DataFrame containing the table data.

        Raises:
            ValueError: If there is an issue with deleting the destination table or writing the schema.
        """
        logging.info("Writing table to destination.")
        logging.debug("Overwrite: %s", self.meta.overwrite)
        # Delete the destination table if overwrite is True
        self.delete_table_to_overwrite()

        # Get the table path
        path = self.table_url()
        logging.debug("Table path: %s", path)
        # Get the file type
        file_type = self.path.file_type
        # Split the partition string into individual partitions
        partitions = self.path.partition.split("/")

        # Check if the table should be saved partitioned
        if partitions != [""]:
            for part in partitions:
                # Add the partition column in the table
                df = df.withColumn(part, lit(PARTITION_MAP[part](self.meta.date)))
            # Write the table partitioned
            df.write.partitionBy(partitions).mode("append").format(file_type).save(path)
            print("\nescreveu:")
            # df.show()
        else:
            # Write the table without partition
            df.write.mode("append").format(file_type).save(path)

        # Write the schema
        try:
            self.write_schema(df)
        except Exception as e:
            raise ValueError("Error writing schema: {}".format(str(e)))

from datetime import datetime
from typing import Dict
from ngdataenginterface.table import Table, PathParams, MetaParams
from ngdataenginterface.aws_interface import AWSInterface
from ngdataenginterface.spark_manager import SparkManager

import logging


class Analytical:
    """
    Class Analytical encapsulates the functionality for table read and write operations,
    along with the execution of a specified aggregation function.
    """

    def __init__(
        self,
        read_params: Dict[str, dict],
        write_params: Dict[str, dict],
        aggregation_function,
        date: datetime,
        aws_interface: AWSInterface,
        spark_manager: SparkManager,
        overwrite: bool = False,
        log_level: int = logging.INFO,
    ) -> None:
        """
        Instantiates an Analytical object.
        """
        self.read = self._init_tables(
            read_params, date, aws_interface, spark_manager, overwrite
        )
        self.write = self._init_tables(
            write_params, date, aws_interface, spark_manager, overwrite
        )
        self.aggregation_function = aggregation_function
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)  # Set the log level

    @staticmethod
    def _init_tables(
        params: Dict[str, dict],
        date: datetime,
        aws_interface: AWSInterface,
        spark_manager: SparkManager,
        overwrite: bool,
    ) -> Dict[str, Table]:
        """
        Initialize the tables for data read and write operations.
        """
        tables = {}
        print("\nparams: ", params, "\n")
        for table_name, table_params in params.items():
            path = PathParams.from_dict(table_params)
            meta = MetaParams(date=date, overwrite=overwrite)
            tables[table_name] = Table(
                path=path,
                meta=meta,
                aws_interface=aws_interface,
                spark_manager=spark_manager,
            )
        return tables

    def prepare_inputs(self) -> None:
        """
        Prepare the inputs by reading data from the tables.
        """
        self.logger.info("Preparing inputs...")
        try:
            self.inputs = {
                table_name: table.read_table()
                for table_name, table in self.read.items()
            }
            self.logger.debug(f"Prepared inputs: {self.inputs}")
        except Exception as e:
            self.logger.error(f"Failed to prepare inputs: {e}")
            raise e
        self.logger.info("Inputs prepared successfully.")

    def run(self) -> None:
        """
        Run the aggregation function and write the output back to the tables.
        """
        self.logger.info("Running the aggregation function...")
        try:
            self.prepare_inputs()
            print("\ninputs: ", self.inputs, "\n")
            print("\nagg:", self.aggregation_function, "\n")
            self.output = self.aggregation_function(inputs=self.inputs)
            self.logger.debug(f"Aggregation output: {self.output}")
            print("\noutput2: ", self.output, "\n")
            for table_name, table in self.write.items():
                print("\noutput: ", self.output[table_name], "\n")
                table.write_table(self.output[table_name])
            self.logger.info(
                "Successfully ran the aggregation function and wrote output to tables."
            )
        except Exception as e:
            self.logger.error(f"Failed to run the aggregation function: {e}")
            raise e

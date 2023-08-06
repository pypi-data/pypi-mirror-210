from datamodel import data_source
from reportmodel import report_generator
from typing import Callable
from environment.environment import setup_logger

logger = setup_logger()

class Report:
    """Generates reports using a data source and report generator."""

    def __init__(
        self,
        data_model: data_source.IDataSource,
        report_model: report_generator.ReportGenerator,
    ) -> None:
        """
        Initialize the Report object.

        Args:
            data_model: An instance of a data source implementing the IDataSource interface.
            report_model: An instance of a report generator.

        """
        self._reportmodel = report_model
        self._datamodel = data_model

    def create(self, path: Callable[[dict], str]):
        """
        Create reports using the provided data source and report generator.

        Args:
            path: A callable that returns the path for each generated report, based on the provided data.

        """
        self._reportmodel.generate(data={"data" : self._datamodel.data}, path=path(self._datamodel.data))
    
    def create_each(self, path: Callable[[dict], str]):
        """
        Create reports using the provided data source and report generator.

        Args:
            path: A callable that returns the path for each generated report, based on the provided data.

        """
        for row in self._datamodel.data:
            logger.debug(row)
            self._reportmodel.generate(data=row, path=path(row))

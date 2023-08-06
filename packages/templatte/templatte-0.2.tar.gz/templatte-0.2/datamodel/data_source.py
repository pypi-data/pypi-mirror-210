from abc import ABC
from typing import Callable
import pandas as pd


class IDataSource(ABC):
    """Interface for data sources."""

    def __init__(self) -> None:
        """Initialize the data source."""
        self._data = None
        self._transformers = []
        super().__init__()

    @property
    def data(self) -> dict:
        """Get the transformed data."""
        self.connect()
        self.transform()
        return self._data.to_dict(orient="records")

    @data.setter
    def data(self, data: pd.DataFrame) -> None:
        """Set the data."""
        self._data = data

    def add_transformer(
        self, transformer: Callable[[pd.DataFrame], pd.DataFrame]
    ) -> None:
        """Add a data transformer."""
        self._transformers.append(transformer)

    def connect(self) -> None:
        """Connect to the data source."""
        self.data(None)

    def transform(self):
        """Transform the data using registered transformers."""
        for transformer in self._transformers:
            self._data = transformer(self._data)


class CsvDataSource(IDataSource):
    """Data source for CSV files."""

    def __init__(self) -> None:
        """Initialize the CSV data source."""
        super().__init__()

    def connect(self, connection: str, csv_args: dict = {}) -> None:
        """Connect to the CSV file."""
        df = pd.read_csv(connection, **csv_args)
        self.data(df)


class ExcelDataSource(IDataSource):
    """Data source for Excel files."""

    def __init__(self, connection: str, excel_args : dict = {}) -> None:
        """Initialize the Excel data source."""
        super().__init__()
        self.excel_args = excel_args
        self.connection = connection

    def connect(self) -> None:
        """Connect to the Excel file."""
        df = pd.read_excel(self.connection, **self.excel_args)
        self._data = df

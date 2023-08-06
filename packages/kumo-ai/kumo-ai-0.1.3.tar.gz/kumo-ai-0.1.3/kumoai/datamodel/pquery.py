from dataclasses import field
from enum import Enum
from typing import Dict, List, Literal, Optional, Union

from pydantic import Field, validator
from pydantic.dataclasses import dataclass

from kumoai.datamodel.data_source import DataSourceType

TableName = str


class SemanticType(str, Enum):
    numerical = 'numerical'
    categorical = 'categorical'
    multicategorical = 'multicategorical'
    ID = 'ID'
    text = 'text'
    timestamp = 'timestamp'


class Dtype(Enum):
    bool = 'bool'
    int = 'int'
    byte = 'byte'
    int16 = 'int16'
    int32 = 'int32'
    int64 = 'int64'
    float = 'float'
    float32 = 'float32'
    float64 = 'float64'
    string = 'string'
    date = 'date'
    time = 'time'
    timedelta = 'timedelta'
    unsupported = 'unsupported'


@dataclass
class Column:
    name: str
    stype: SemanticType


class TableType(str, Enum):
    FACT = 'fact'
    DIMENSION = 'dimension'


class FileType(Enum):
    CSV = "CSV"
    PARQUET = "PARQUET"


@dataclass
class S3SourceTable:
    """V2 table definition schema for table located on s3."""
    # We support two types of table file path:
    # 1. s3_path specifies the whole directory (prefix), ending with "/"
    # 2. s3_path specifies the full path of a single file, ending with file
    #    name suffix that must be one of ".csv" or ".parquet"
    s3_path: str

    # If not provided, then the file_path must either end in `.csv` or
    # `.parquet`, and we will parse the file type from there. Please use the
    # `validated_file_type` proper to access the parsed & validated file type.
    file_type: Optional[FileType] = None

    data_source_type: Literal[DataSourceType.S3] = DataSourceType.S3

    @property
    def table(self) -> TableName:
        if self.s3_path.endswith('/'):
            return TableName(
                self.s3_path.rstrip('/').rsplit('/', maxsplit=1)[1])
        filename = self.s3_path.rsplit('/', maxsplit=1)[1]
        return TableName(filename.rsplit('.', maxsplit=1)[0])  # strip suffix


@dataclass
class SnowflakeSourceTable:
    snowflake_connector_id: str
    database: str
    schema_name: str
    table: TableName
    data_source_type: Literal[
        DataSourceType.SNOWFLAKE] = DataSourceType.SNOWFLAKE


@dataclass
class TableDefinition:
    table_type: TableType

    # List of ALL columns selected from source table
    cols: List[Column]

    source_table: Union[S3SourceTable, SnowflakeSourceTable] = Field(
        discriminator='data_source_type')

    # Name of the primary key column.
    pkey: Optional[str] = None

    # Name of the time column, required to have stype=SemanticType.timestamp
    time_col: Optional[str] = None

    # Optional SQL statement to create a view on top of source table.
    sql: Optional[str] = None

    @validator("time_col", "pkey")
    def empty_str_to_none(cls, v: Optional[str]) -> Optional[str]:
        if v == '':
            return None
        return v


@dataclass
class S3SourceTableRequest:
    """
    S3 table location at either:
    <s3_root_dir>/<table_name>/*[.csv|.parquet]
    <s3_root_dir>/<table_name>[.csv|.parquet]
    """
    s3_root_dir: str
    table_names: Optional[List[str]] = None
    file_type: Optional[FileType] = None


@dataclass
class SnowflakeSourceTableRequest:
    snowflake_connector_id: str

    # TODO(siyang): We should move database and schema out of SF connector.
    # database: Optional[str] = None
    # schema: Optional[str] = None

    table_names: Optional[List[str]] = None


@dataclass
class SourceColumn:
    """Represents a column within a source table.

    Source Tables are tables within a connector that have not yet been
    saved to the Kumo MetadataDB.
    """

    name: str
    stype: SemanticType
    dtype: Dtype
    is_primary: bool


@dataclass
class SourceTableInfo:
    source_table: Union[S3SourceTable, SnowflakeSourceTable] = Field(
        discriminator='data_source_type')

    cols: List[SourceColumn] = field(default_factory=list)

    def as_dim_table(self, pkey_col: Optional[str] = None) -> TableDefinition:
        return self._as_table_definition(table_type=TableType.DIMENSION,
                                         pkey_col=pkey_col,
                                         time_col=None)

    def as_fact_table(self,
                      time_col: Optional[str] = None,
                      *,
                      pkey_col: Optional[str] = None) -> TableDefinition:
        return self._as_table_definition(table_type=TableType.FACT,
                                         pkey_col=pkey_col,
                                         time_col=time_col)

    def _as_table_definition(
            self,
            table_type: TableType,
            pkey_col: Optional[str] = None,
            time_col: Optional[str] = None) -> TableDefinition:
        if not pkey_col:
            pkeys = [col.name for col in self.cols if col.is_primary]
            assert len(pkeys) <= 1
            pkey_col = pkeys[0] if pkeys else None
        if table_type == TableType.DIMENSION and not pkey_col:
            raise ValueError(
                'Primary key (pkey_col) is required for DIMENSION table!')

        if not time_col:
            time_cols = [
                col.name for col in self.cols
                if col.stype == SemanticType.timestamp
            ]
            time_col = time_cols[0] if time_cols else None
        if table_type == TableType.FACT and not time_col:
            raise ValueError(
                'Time column (time_col) is required for FACT table!')

        return TableDefinition(
            table_type=table_type,
            cols=[Column(name=col.name, stype=col.stype) for col in self.cols],
            source_table=self.source_table,
            pkey=pkey_col,
            time_col=time_col)


@dataclass
class ColumnKey:
    """Reference to a column within a PQuery/Graph definition."""
    table_name: TableName
    col_name: str


@dataclass
class ColumnKeyGroup:
    """Group of column keys to be linked together in a graph."""
    columns: List[ColumnKey]  # Always sorted and deduped, immutable


@dataclass
class GraphDefinition:
    tables: Dict[TableName, TableDefinition]

    col_groups: List[ColumnKeyGroup]


@dataclass
class PQueryResource:
    """Predictive Query resource definition."""
    name: str

    query_yaml: str

    graph: GraphDefinition

    graph_display_name: Optional[str] = None

    advanced_options_yaml: Optional[str] = None

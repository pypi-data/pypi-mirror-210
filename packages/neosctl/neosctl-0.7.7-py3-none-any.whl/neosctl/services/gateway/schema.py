from typing import Dict, List, Literal, Optional, Union

import pydantic
from pydantic import BaseModel


class FieldDataType(BaseModel):
    meta: Dict[str, str]
    type: str  # noqa: A003


class FieldDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    primary: bool
    optional: bool
    data_type: FieldDataType


class IcebergTableProperties(BaseModel):
    format: Optional[str] = None  # noqa: A003
    partitioning: Optional[List[str]] = None
    location: Optional[str] = None
    format_version: Optional[int] = None


class StreamingSchemaBase(BaseModel):
    type: Literal["streaming"]  # noqa: A003
    fields: Optional[List[FieldDefinition]]
    iceberg_table_properties: Optional[IcebergTableProperties] = None


class StoredSchemaBase(BaseModel):
    type: Literal["stored"]  # noqa: A003
    fields: Optional[List[FieldDefinition]]


class SubsetSchema(BaseModel):
    type: Literal["subset"]  # noqa: A003
    parent_product: str
    columns: List[str]


class CreateStreamingSchema(StreamingSchemaBase):
    flow_type: str


class Info(BaseModel):
    label: str
    owner: Union[str, None]
    contact_ids: List[str]
    links: List[str]
    notes: Union[str, None]


class CreateDataProduct(BaseModel):
    name: str
    description: str
    info: Info
    details: Union[StoredSchemaBase, CreateStreamingSchema, SubsetSchema] = pydantic.Field(..., discriminator="type")


class StreamingDataProductSchema(StreamingSchemaBase):
    fields: List[FieldDefinition]


class StoredDataProductSchema(StoredSchemaBase):
    fields: List[FieldDefinition]


class UpdateDataProductSchema(BaseModel):
    details: Union[StreamingDataProductSchema, StoredDataProductSchema] = pydantic.Field(..., discriminator="type")


class UpdateDataProductInfo(BaseModel):
    info: Info


class ExpectationItem(BaseModel):
    expectation_type: str
    kwargs: dict
    meta: dict


class ExpectationWeights(BaseModel):
    accuracy: float
    completeness: float
    consistency: float
    uniqueness: float
    validity: float


class ExpectationColumnThresholds(BaseModel):
    accuracy: Union[float, None]
    completeness: Union[float, None]
    consistency: Union[float, None]
    uniqueness: Union[float, None]
    validity: Union[float, None]


class ExpectationThresholds(BaseModel):
    table: float
    columns: Dict[str, ExpectationColumnThresholds]


class UpdateQualityExpectations(BaseModel):
    custom_details: List[ExpectationItem]
    weights: Union[ExpectationWeights, None]
    thresholds: Union[ExpectationThresholds, None]


class CreateSource(BaseModel):
    name: str
    description: Union[str, None] = None
    info: Info


class UpdateSource(BaseModel):
    name: str
    description: Union[str, None] = None


class UpdateSourceInfo(BaseModel):
    info: Info


class ExternalDatabaseConnectionDetails(BaseModel):
    type: Literal["external_database"]  # noqa: A003
    engine: str
    schema_: str = pydantic.Field(..., alias="schema")
    host: str
    port: int
    database: str
    user_env: str
    password_env: str


class FileConnectionDetails(BaseModel):
    type: Literal["file"]  # noqa: A003
    url: str
    access_key_env: Optional[str]
    access_secret_env: Optional[str]


class CreateConnection(BaseModel):
    name: str
    details: Union[
        ExternalDatabaseConnectionDetails,
        FileConnectionDetails,
    ]


class TableConnectionParams(BaseModel):
    type: Literal["table"]  # noqa: A003
    table: str


class QueryConnectionParams(BaseModel):
    type: Literal["query"]  # noqa: A003
    query: str


class CSVConnectionParams(BaseModel):
    type: Literal["csv"]  # noqa: A003
    path: Union[str, List[str]]
    has_header: Optional[bool]
    delimiter: Optional[str]
    quote_char: Optional[str]
    escape_char: Optional[str]


class CreateSourceConnection(BaseModel):
    details: Union[
        TableConnectionParams,
        QueryConnectionParams,
        CSVConnectionParams,
    ]

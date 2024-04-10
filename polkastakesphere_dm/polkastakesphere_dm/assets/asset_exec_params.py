# from dagster import Config
from typing import Annotated
from typing import Literal
from typing import Union

from pydantic import BaseModel


class SubstrateExtractParameters(BaseModel):
    start_date: str = "2019-04-01"
    end_date: str = "2023-11-30"
    gcp_project: str
    gcp_dataset: str
    gcp_table: str
    gcp_materialize_dataset: str
    timestamp_column: str = "ts"
    sink_update_mode: str = "append"
    destination: Annotated[Union[list[str], Literal["local"]], str] = "local"

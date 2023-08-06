from typing import List, Optional, Any, Dict

from pydantic import BaseModel


class SeriesModel(BaseModel):
    name: str
    columns: List[str]
    values: List[List[Any]]
    tags: Optional[Dict[str, str]]


class ResultModel(BaseModel):
    statement_id: int
    series: Optional[List[SeriesModel]]
    error: Optional[str]


class ResultsModel(BaseModel):
    results: List[ResultModel]

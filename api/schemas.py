from pydantic import BaseModel


class ReadMetricsResponse(BaseModel):
    metrics: list[str]
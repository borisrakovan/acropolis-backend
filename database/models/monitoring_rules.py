import enum
from decimal import Decimal
from typing import Optional, Union, Literal

from pydantic import BaseModel
from sqlalchemy import Column, JSON, Enum
from sqlmodel import Field, SQLModel, Relationship


class MetricType(enum.Enum):
    Temperature = "TEMPERATURE"
    WindSpeed = "WIND-SPEED"  #  m/s
    RelativeHumidity = "RELATIVE-HUMIDITY"
    Precipitation = "PRECIPITATION"
    # Pressure = "PRESSURE"
    # SnowDepth = "SNOW-DEPTH"
    # SnowCover = "SNOW-COVER"
    # Wind = "WIND"
    # uhrn zrazok mm


class LogicalOperator(enum.Enum):
    """Types of logic comparison operators"""

    LTE = "<="
    LT = "<"
    GTE = ">="
    GT = ">"
    EQ = "="
    NEQ = "!="


class PointRadiusArea(BaseModel):
    type: Literal["POINT-RADIUS-AREA"]
    lat: Decimal
    long: Decimal
    radius: float
    radius_unit: Literal["KM"] | Literal["M"] = Field(default="M")


class SpecificArea(BaseModel):
    type: Literal["SPECIFIC-AREA"]
    area_id: int


class AreaDefinition(BaseModel):
    __root__: Union[PointRadiusArea, SpecificArea]


class EvaluationMode(enum.Enum):
    SINGLE_VALUE = "SINGLE-VALUE"
    AVERAGE_VALUE = "AVERAGE-VALUE"


class TimeWindowDefinition(BaseModel):
    time_unit: Literal["HOUR"] | Literal["DAY"] = Field(default="HOUR")
    value: int


class MonitoringRuleBase(SQLModel):
    title: str
    metric: MetricType = Field(sa_column=Column(Enum(MetricType)))
    logical_operator: LogicalOperator = Field(sa_column=Column(Enum(LogicalOperator)))
    evaluation_mode: EvaluationMode
    value: float
    area_definition: AreaDefinition = Field(default={}, sa_column=Column(JSON))
    time_window: TimeWindowDefinition = Field(default={}, sa_column=Column(JSON))


class MonitoringRuleCreate(MonitoringRuleBase):
    alert_definitions: list["AlertDefinitionCreate"]


class MonitoringRuleRead(MonitoringRuleBase):
    id: int
    alert_definitions: list["AlertDefinitionRead"]
    alert_triggers: list["AlertTrigger"]


class MonitoringRule(MonitoringRuleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    alert_definitions: list["AlertDefinition"] = Relationship(back_populates="monitoring_rule")
    alert_triggers: list["AlertTrigger"] = Relationship(back_populates="monitoring_rule")

    # def from_orm(cls, obj: Any):


from database.models.alerts import AlertDefinition, AlertDefinitionCreate, AlertDefinitionRead, AlertTrigger
MonitoringRuleCreate.update_forward_refs()
MonitoringRuleRead.update_forward_refs()
MonitoringRule.update_forward_refs()

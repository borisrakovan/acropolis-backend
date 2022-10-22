import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Enum
from sqlmodel import SQLModel, Field, Relationship


class AlertType(enum.Enum):
    Email = "EMAIL"
    SMS = "SMS"


class AlertDefinitionBase(SQLModel):
    alert_type: AlertType = Field(sa_column=Column(Enum(AlertType)))
    contact_info: str
    message_template: str


class AlertDefinitionRead(AlertDefinitionBase):
    id: int


class AlertDefinitionCreate(AlertDefinitionBase):
    pass


class AlertDefinition(AlertDefinitionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    monitoring_rule_id: Optional[int] = Field(default=None, foreign_key="monitoringrule.id")
    monitoring_rule: Optional["MonitoringRule"] = Relationship(back_populates="alert_definitions")


class AlertTriggerBase(SQLModel):
    triggered_at: datetime
    notified_at: datetime | None = Field(default=None)
    reference_value: float
    actual_value: float


class AlertTrigger(AlertTriggerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    monitoring_rule_id: int | None = Field(default=None, foreign_key="monitoringrule.id")
    monitoring_rule: Optional["MonitoringRule"] = Relationship(back_populates="alert_triggers")
    monitoring_run_id: int | None = Field(default=None, foreign_key="monitoringrun.id")
    monitoring_run: Optional["MonitoringRun"] = Relationship(back_populates="alert_triggers")


from database.models.monitoring_rules import MonitoringRule
from database.models.monitoring_runs import MonitoringRun
AlertDefinition.update_forward_refs()

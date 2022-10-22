import enum
from typing import Optional

from sqlalchemy import Column, Enum
from sqlmodel import SQLModel, Field, Relationship


class AlertType(enum.Enum):
    Email = "EMAIL"
    SMS = "SMS"


class AlertDefinitionBase(SQLModel):
    alert_type: AlertType = Field(sa_column=Column(Enum(AlertType)))
    contact_info: str


class AlertDefinitionRead(AlertDefinitionBase):
    id: int


class AlertDefinitionCreate(AlertDefinitionBase):
    pass


class AlertDefinition(AlertDefinitionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    monitoring_rule_id: Optional[int] = Field(default=None, foreign_key="monitoringrule.id")
    monitoring_rule: Optional["MonitoringRule"] = Relationship(back_populates="alert_definitions")


from database.models.monitoring_rules import MonitoringRule
AlertDefinition.update_forward_refs()

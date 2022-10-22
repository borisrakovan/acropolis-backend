from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class MonitoringRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    started_at: datetime
    finished_at: datetime | None = Field(default=None)
    alert_triggers: list["AlertTrigger"] = Relationship(back_populates="monitoring_run")


from database.models.alerts import AlertTrigger
MonitoringRun.update_forward_refs()
